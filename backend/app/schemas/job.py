from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class JobBase(BaseModel):
    source: str
    external_job_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_experience: Optional[float] = None
    maximum_experience: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "INR"
    posted_at: Optional[datetime] = None
    job_url: Optional[str] = None
    application_url: Optional[str] = None
    status: str = "active"


class JobCreate(JobBase):
    content_hash: str


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[str] = None


class JobOut(JobBase):
    id: int
    content_hash: str
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    match_score: Optional[float] = None  # Populated when joined with active match
    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: List[JobOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobSearchQuery(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    source: Optional[str] = None
    min_score: Optional[float] = None
    min_experience: Optional[float] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "match_score"  # match_score, posted_at, created_at
    sort_order: str = "desc"


class JobImportRequest(BaseModel):
    source: Optional[str] = "manual"
    job_url: Optional[str] = None
    title: str
    company: str
    description: str
    location: Optional[str] = "Bengaluru, Karnataka, India"
    work_mode: Optional[str] = "Hybrid"
    application_url: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    minimum_experience: Optional[float] = None
