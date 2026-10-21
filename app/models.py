from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

def utcnow(): return datetime.now(timezone.utc)

class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class ControlMEnvironment(Base):
    __tablename__ = "controlm_environments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    api_base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class ApplicationADGroup(Base):
    __tablename__ = "application_ad_groups"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    ad_group_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint("application_id", "ad_group_name", "role"),)

class PlanRefreshRun(Base):
    __tablename__ = "plan_refresh_runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("controlm_environments.id"), nullable=False)
    plan_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="RUNNING", nullable=False)
    records_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_summary: Mapped[str | None] = mapped_column(Text)

class Folder(Base):
    __tablename__ = "folders"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("controlm_environments.id"), nullable=False)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    controlm_server: Mapped[str] = mapped_column(String(255), nullable=False)
    folder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint("environment_id", "controlm_server", "folder_name"),)

class JobInstance(Base):
    __tablename__ = "job_instances"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_run_id: Mapped[int | None] = mapped_column(ForeignKey("plan_refresh_runs.id"))
    folder_id: Mapped[int] = mapped_column(ForeignKey("folders.id"), nullable=False)
    controlm_server: Mapped[str] = mapped_column(String(255), nullable=False)
    folder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_id: Mapped[str] = mapped_column(String(255), nullable=False)
    order_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    api_job_id: Mapped[str] = mapped_column(String(600), nullable=False)
    observed_status: Mapped[str | None] = mapped_column(String(100))
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (Index("ix_job_instances_folder_current", "folder_id", "is_current"), Index("ix_job_instances_name", "job_name"), Index("ix_job_instances_api_job_id", "api_job_id"))

class AutomationRequest(Base):
    __tablename__ = "automation_requests"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    environment_id: Mapped[int] = mapped_column(ForeignKey("controlm_environments.id"), nullable=False)
    job_instance_id: Mapped[int] = mapped_column(ForeignKey("job_instances.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False)
    controlm_http_status: Mapped[int | None] = mapped_column(Integer)
    result_summary: Mapped[str | None] = mapped_column(Text)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class RequestEvent(Base):
    __tablename__ = "request_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("automation_requests.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
