from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobOut


class ApplicationCreate(BaseModel):
    job_id: int
    application_status: str = "To Apply"  # Saved, To Apply, Applied, Assessment, Interview, Offer, Rejected, Withdrawn
    applied_at: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    application_status: Optional[str] = None
    applied_at: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    application_status: str
    applied_at: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: JobOut
    model_config = ConfigDict(from_attributes=True)
