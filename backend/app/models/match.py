from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    overall_score = Column(Float, nullable=False, index=True)
    skill_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    title_score = Column(Float, nullable=False)
    location_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)

    matched_skills_json = Column(Text, nullable=False)  # JSON array of matched skill strings
    missing_skills_json = Column(Text, nullable=False)  # JSON object with required & preferred missing
    explanation_json = Column(Text, nullable=False)     # JSON object with strengths, gaps, advice
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")

    __table_args__ = (
        UniqueConstraint("user_id", "resume_id", "job_id", name="uq_user_resume_job_match"),
        Index("ix_match_user_score", "user_id", "overall_score"),
    )

