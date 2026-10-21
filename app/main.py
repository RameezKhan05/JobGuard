from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Application, Folder, JobInstance, AutomationRequest
from app.schemas import ActionRequest, ActionResponse
from app.security import get_current_user
from app.services import submit_job_action

app = FastAPI(title="Control-M Self-Service Portal", version="0.1.0",
    description="Phase 1 scaffold. LDAP/ACL and final-state reconciliation are not yet implemented.")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/applications")
def list_applications(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # Add ACL filtering before shared use.
    return db.scalars(select(Application).where(Application.is_active.is_(True))).all()

@app.get("/api/v1/folders")
def list_folders(application_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # Add ACL filtering before shared use.
    return db.scalars(select(Folder).where(Folder.application_id == application_id, Folder.is_active.is_(True))).all()

@app.get("/api/v1/jobs")
def list_jobs(folder_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # Reads PostgreSQL catalogue; no Control-M call for each browse request.
    return db.scalars(select(JobInstance).where(JobInstance.folder_id == folder_id, JobInstance.is_current.is_(True))).all()

@app.post("/api/v1/jobs/{job_instance_id}/actions", response_model=ActionResponse)
def job_action(job_instance_id: int, body: ActionRequest, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    job = db.get(JobInstance, job_instance_id)
    if not job or not job.is_current: raise HTTPException(status_code=404, detail="Current job instance not found in catalogue")
    req = submit_job_action(db, job, user, body.action, body.reason)
    return ActionResponse(request_id=req.id, request_number=req.request_number, status=req.status, message=req.result_summary or "Request recorded")

@app.get("/api/v1/requests/{request_id}")
def get_request(request_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    req = db.get(AutomationRequest, request_id)
    if not req: raise HTTPException(status_code=404, detail="Request not found")
    # Add requester/admin access check before shared use.
    return req
