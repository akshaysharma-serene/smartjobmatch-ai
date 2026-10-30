from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ExperienceItem(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    dates: Optional[str] = None
    is_current: bool = False
    highlights: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None
    details: Optional[str] = None


class ProjectItem(BaseModel):
    name: str
    technologies: List[str] = Field(default_factory=list)
    description: str
    highlights: List[str] = Field(default_factory=list)


class ResumeParsedData(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)


class ResumeCreate(BaseModel):
    filename: str
    extracted_text: str
    parsed_data: ResumeParsedData
    version: int = 1
    is_active: bool = True


class ResumeUpdate(BaseModel):
    filename: Optional[str] = None
    is_active: Optional[bool] = None
    parsed_data: Optional[ResumeParsedData] = None


class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    extracted_text: str
    parsed_data: ResumeParsedData
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
