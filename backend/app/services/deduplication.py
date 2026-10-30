import json
from datetime import datetime, timezone
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.models.job import Job


class DeduplicationService:
    @staticmethod
    def upsert_job(db: Session, job_dict: dict) -> Tuple[Job, bool]:
        """
        Deduplicates and upserts a job record.
        Checks:
        1. (source, external_job_id)
        2. job_url (if present)
        3. content_hash
        Returns (job_instance, is_new_record)
        """
        source = job_dict["source"]
        external_id = job_dict["external_job_id"]
        job_url = job_dict.get("job_url")
        content_hash = job_dict["content_hash"]
        now = datetime.now(timezone.utc)

        # 1. Match on source + external_id
        existing = db.query(Job).filter(
            Job.source == source,
            Job.external_job_id == external_id
        ).first()

        # 2. Match on canonical job_url if external_id differed or missing
        if not existing and job_url:
            existing = db.query(Job).filter(Job.job_url == job_url).first()

        # 3. Match on content_hash (exact text match across same company/role)
        if not existing and content_hash:
            existing = db.query(Job).filter(Job.content_hash == content_hash).first()

        if existing:
            # Update last_seen_at and refreshed fields if active
            existing.last_seen_at = now
            existing.status = job_dict.get("status", existing.status)
            if job_dict.get("application_url") and not existing.application_url:
                existing.application_url = job_dict.get("application_url")
            db.commit()
            db.refresh(existing)
            return existing, False

        # Create new job
        new_job = Job(
            source=source,
            external_job_id=external_id,
            title=job_dict["title"],
            company=job_dict["company"],
            description=job_dict["description"],
            location=job_dict.get("location"),
            work_mode=job_dict.get("work_mode"),
            employment_type=job_dict.get("employment_type", "Full-time"),
            required_skills_json=json.dumps(job_dict.get("required_skills", [])),
            preferred_skills_json=json.dumps(job_dict.get("preferred_skills", [])),
            minimum_experience=job_dict.get("minimum_experience"),
            maximum_experience=job_dict.get("maximum_experience"),
            salary_min=job_dict.get("salary_min"),
            salary_max=job_dict.get("salary_max"),
            salary_currency=job_dict.get("salary_currency", "INR"),
            posted_at=job_dict.get("posted_at") or now,
            job_url=job_url,
            application_url=job_dict.get("application_url"),
            content_hash=content_hash,
            status=job_dict.get("status", "active"),
            first_seen_at=now,
            last_seen_at=now,
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job, True

