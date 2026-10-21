from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Folder, JobInstance, AutomationRequest, RequestEvent
from app.controlm_client import ControlMClient, ControlMError

def require_application_role(db: Session, application_id: int, username: str, required_role: str):
    # Fail closed until LDAP group membership and application ACL mapping are implemented.
    raise HTTPException(status_code=501, detail="Application ACL is not configured; Hold/Release is disabled until LDAP group authorization is implemented.")

def submit_job_action(db: Session, job: JobInstance, username: str, action: str, reason: str):
    folder = db.get(Folder, job.folder_id)
    if not folder or not folder.is_active:
        raise HTTPException(status_code=409, detail="Folder is not active")
    require_application_role(db, folder.application_id, username, "OPERATOR")
    request = AutomationRequest(request_number=f"CM-{uuid4().hex[:12].upper()}", requested_by=username,
        application_id=folder.application_id, environment_id=folder.environment_id, job_instance_id=job.id,
        action_type=action, status="SUBMITTED", correlation_id=str(uuid4()))
    db.add(request); db.flush()
    db.add(RequestEvent(request_id=request.id, event_type="SUBMITTED", actor=username, message=reason))
    db.commit(); db.refresh(request)
    try:
        status_code, summary = ControlMClient().set_job_action(job.api_job_id, action)
        request.controlm_http_status = status_code; request.status = "IN_PROGRESS"; request.result_summary = summary
        db.add(RequestEvent(request_id=request.id, event_type="API_ACCEPTED", actor="controlm-service", message=summary))
    except ControlMError as exc:
        msg = str(exc); request.status = "UNKNOWN" if "TIMEOUT_UNKNOWN" in msg else "FAILED"
        request.result_summary = msg
        db.add(RequestEvent(request_id=request.id, event_type=request.status, actor="controlm-service", message=msg))
        if request.status == "FAILED": request.completed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(request)
    return request
