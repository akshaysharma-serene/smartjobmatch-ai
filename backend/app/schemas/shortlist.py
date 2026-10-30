from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobOut
from app.schemas.match import JobMatchOut


class ShortlistCreate(BaseModel):
    status: Optional[str] = "shortlisted"  # shortlisted, rejected, saved
    notes: Optional[str] = None


class ShortlistUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class ShortlistOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    resume_id: Optional[int] = None
    status: str
    match_score: float
    notes: Optional[str] = None
    shortlisted_at: datetime
    updated_at: datetime
    job: JobOut
    match: Optional[JobMatchOut] = None
    model_config = ConfigDict(from_attributes=True)
