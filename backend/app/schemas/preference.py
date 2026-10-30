from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class PreferenceBase(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    work_modes: List[str] = Field(default_factory=list)
    minimum_experience: Optional[float] = None
    maximum_experience: Optional[float] = None
    minimum_match_score: float = 70.0
    scoring_weights: Dict[str, float] = Field(default_factory=dict)
    sync_frequency: str = "every_6_hours"


class PreferenceUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    work_modes: Optional[List[str]] = None
    minimum_experience: Optional[float] = None
    maximum_experience: Optional[float] = None
    minimum_match_score: Optional[float] = None
    scoring_weights: Optional[Dict[str, float]] = None
    sync_frequency: Optional[str] = None


class PreferenceOut(PreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
