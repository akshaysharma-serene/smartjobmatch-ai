from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.job import JobOut


class MissingSkills(BaseModel):
    required: List[str] = Field(default_factory=list)
    preferred: List[str] = Field(default_factory=list)


class MatchExplanation(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    experience_compatibility: str
    location_compatibility: str
    suggested_keywords: List[str] = Field(default_factory=list)
    breakdown_notes: Dict[str, str] = Field(default_factory=dict)


class JobMatchOut(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    overall_score: float
    skill_score: float
    semantic_score: float
    experience_score: float
    title_score: float
    location_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: MissingSkills
    explanation: MatchExplanation
    calculated_at: datetime
    job: Optional[JobOut] = None
    model_config = ConfigDict(from_attributes=True)


class RunMatchRequest(BaseModel):
    resume_id: Optional[int] = None
    job_ids: Optional[List[int]] = None  # None means all active jobs


class MatchAnalytics(BaseModel):
    total_matched: int
    excellent_matches: int  # 85-100
    strong_matches: int     # 70-84
    potential_matches: int  # 55-69
    low_matches: int        # <55
    average_score: float
    top_matched_skills: List[Dict[str, Any]]
    top_missing_skills: List[Dict[str, Any]]
    score_distribution: List[Dict[str, Any]]
