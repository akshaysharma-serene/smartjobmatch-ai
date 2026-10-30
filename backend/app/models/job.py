from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # linkedin, greenhouse, lever, mock, manual
    external_job_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True, index=True)
    work_mode = Column(String(50), nullable=True)  # Remote, Hybrid, On-site
    employment_type = Column(String(50), nullable=True)  # Full-time, Contract, Internship, etc.
    
    required_skills_json = Column(Text, nullable=True)  # JSON array of strings
    preferred_skills_json = Column(Text, nullable=True)  # JSON array of strings
    
    minimum_experience = Column(Float, nullable=True)
    maximum_experience = Column(Float, nullable=True)
    
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True)  # INR, USD, EUR, etc.
    
    posted_at = Column(DateTime, nullable=True)
    job_url = Column(String(1024), nullable=True)
    application_url = Column(String(1024), nullable=True)
    
    content_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), default="active", nullable=False)  # active, closed, archived
    
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    shortlists = relationship("ShortlistedJob", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source", "external_job_id", name="uq_source_external_job_id"),
        Index("ix_job_title_company", "title", "company"),
    )

