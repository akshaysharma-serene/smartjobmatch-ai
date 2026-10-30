from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class JobSearchPreferences(Base):
    __tablename__ = "job_search_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    keywords_json = Column(Text, nullable=False)      # JSON list of target titles / keywords
    locations_json = Column(Text, nullable=False)     # JSON list of locations
    work_modes_json = Column(Text, nullable=False)    # JSON list: ["Remote", "Hybrid", "On-site"]
    
    minimum_experience = Column(Float, nullable=True)
    maximum_experience = Column(Float, nullable=True)
    
    minimum_match_score = Column(Float, default=70.0, nullable=False)
    scoring_weights_json = Column(Text, nullable=False)  # JSON object with weights
    sync_frequency = Column(String(50), default="every_6_hours", nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="preferences")

