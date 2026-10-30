from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base


class ShortlistedJob(Base):
    __tablename__ = "shortlisted_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(50), default="shortlisted", nullable=False)  # shortlisted, rejected, saved
    match_score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    shortlisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="shortlists")
    job = relationship("Job", back_populates="shortlists")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_shortlist"),
    )

