from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.shortlist import ShortlistedJob
from app.models.match import JobMatch


class ShortlistService:
    @staticmethod
    def auto_shortlist_if_eligible(
        db: Session,
        user_id: int,
        job_id: int,
        resume_id: int,
        match_score: float,
        threshold: float = 70.0,
    ) -> Optional[ShortlistedJob]:
        """Automatically shortlists a job if score >= threshold and not already saved/rejected."""
        if match_score < threshold:
            return None

        existing = db.query(ShortlistedJob).filter(
            ShortlistedJob.user_id == user_id,
            ShortlistedJob.job_id == job_id,
        ).first()

        now = datetime.now(timezone.utc)
        if existing:
            # If already explicitly rejected, do not revert to shortlisted
            if existing.status == "rejected":
                return existing
            existing.match_score = match_score
            existing.resume_id = resume_id
            existing.updated_at = now
            db.commit()
            db.refresh(existing)
            return existing

        shortlist_entry = ShortlistedJob(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status="shortlisted",
            match_score=match_score,
            notes=f"Automatically shortlisted with match score {match_score}%.",
            shortlisted_at=now,
            updated_at=now,
        )
        db.add(shortlist_entry)
        db.commit()
        db.refresh(shortlist_entry)
        return shortlist_entry

    @staticmethod
    def update_status(
        db: Session,
        user_id: int,
        job_id: int,
        status: str,
        notes: Optional[str] = None,
        resume_id: Optional[int] = None,
        score: float = 0.0,
    ) -> ShortlistedJob:
        entry = db.query(ShortlistedJob).filter(
            ShortlistedJob.user_id == user_id,
            ShortlistedJob.job_id == job_id,
        ).first()

        now = datetime.now(timezone.utc)
        if entry:
            entry.status = status
            if notes is not None:
                entry.notes = notes
            entry.updated_at = now
            db.commit()
            db.refresh(entry)
            return entry

        # Fetch score from JobMatch if not passed
        if score == 0.0:
            match = db.query(JobMatch).filter(
                JobMatch.user_id == user_id,
                JobMatch.job_id == job_id,
            ).first()
            if match:
                score = match.overall_score
                resume_id = match.resume_id

        entry = ShortlistedJob(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=status,
            match_score=score,
            notes=notes,
            shortlisted_at=now,
            updated_at=now,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def remove_from_shortlist(db: Session, user_id: int, job_id: int) -> bool:
        entry = db.query(ShortlistedJob).filter(
            ShortlistedJob.user_id == user_id,
            ShortlistedJob.job_id == job_id,
        ).first()
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False

