import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import JobMatch
from app.models.shortlist import ShortlistedJob
from app.models.preference import JobSearchPreferences
from app.services.job_normalizer import JobNormalizerService
from app.services.deduplication import DeduplicationService
from app.services.job_matcher import JobMatcherService
from app.services.shortlist_service import ShortlistService
from app.schemas.resume import ResumeParsedData

from app.integrations.linkedin import LinkedInJobSource
from app.integrations.greenhouse import GreenhouseJobSource
from app.integrations.lever import LeverJobSource
from app.integrations.mock_data import MockJobSource

logger = logging.getLogger(__name__)


class JobSyncService:
    _is_running: bool = False
    _last_run_time: datetime = None
    _last_run_stats: Dict[str, Any] = {}

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        return {
            "is_running": cls._is_running,
            "last_run_time": cls._last_run_time.isoformat() if cls._last_run_time else None,
            "last_stats": cls._last_run_stats,
            "sources": [
                LinkedInJobSource().get_connection_status(),
                GreenhouseJobSource().get_connection_status(),
                LeverJobSource().get_connection_status(),
                MockJobSource().get_connection_status(),
            ]
        }

    @classmethod
    async def run_sync_pipeline(cls, db: Session, user_id: int) -> Dict[str, Any]:
        if cls._is_running:
            return {"status": "in_progress", "message": "A synchronization run is already active."}

        cls._is_running = True
        try:
            # 1. Load preferences
            pref = db.query(JobSearchPreferences).filter(JobSearchPreferences.user_id == user_id).first()
            keywords = json.loads(pref.keywords_json) if pref and pref.keywords_json else [
                "Senior Java Developer", "Java Backend Developer", "Spring Boot Developer", "Full-Stack Developer Java React"
            ]
            locations = json.loads(pref.locations_json) if pref and pref.locations_json else ["Bengaluru, Karnataka, India"]
            weights = json.loads(pref.scoring_weights_json) if pref and pref.scoring_weights_json else None
            min_score = pref.minimum_match_score if pref else 70.0
            work_modes = json.loads(pref.work_modes_json) if pref and pref.work_modes_json else ["Remote", "Hybrid", "On-site"]

            # 2. Query configured authorized sources
            sources = [
                LinkedInJobSource(),
                GreenhouseJobSource(),
                LeverJobSource(),
                MockJobSource(),
            ]

            raw_jobs = []
            source_errors = {}
            for src in sources:
                try:
                    jobs = await src.fetch_jobs(keywords=keywords, locations=locations, limit=30)
                    raw_jobs.extend(jobs)
                except Exception as e:
                    source_errors[src.source_name] = str(e)
                    logger.warning(f"Error fetching from source {src.source_name}: {e}")

            # 3, 4, 5, 6: Normalize, validate, detect duplicates, save
            saved_jobs: List[Job] = []
            new_count = 0
            updated_count = 0

            for raw in raw_jobs:
                norm_dict = JobNormalizerService.normalize_job_dict(raw)
                job_inst, is_new = DeduplicationService.upsert_job(db, norm_dict)
                saved_jobs.append(job_inst)
                if is_new:
                    new_count += 1
                else:
                    updated_count += 1

            # 7 & 8: Match jobs against the active resume
            active_resume = db.query(Resume).filter(
                Resume.user_id == user_id,
                Resume.is_active == True,
            ).first()

            matched_count = 0
            shortlisted_count = 0

            if active_resume:
                parsed_dict = json.loads(active_resume.parsed_data_json)
                parsed_resume = ResumeParsedData(**parsed_dict)

                # Match all active jobs in the DB
                all_active_jobs = db.query(Job).filter(Job.status == "active").all()
                for j in all_active_jobs:
                    match_res = JobMatcherService.evaluate_match(
                        parsed_resume=parsed_resume,
                        resume_raw_text=active_resume.extracted_text,
                        job=j,
                        custom_weights=weights,
                        target_roles=keywords,
                        preferred_work_modes=work_modes,
                    )

                    # Upsert match record
                    existing_match = db.query(JobMatch).filter(
                        JobMatch.user_id == user_id,
                        JobMatch.resume_id == active_resume.id,
                        JobMatch.job_id == j.id,
                    ).first()

                    now = datetime.now(timezone.utc)
                    if existing_match:
                        existing_match.overall_score = match_res["overall_score"]
                        existing_match.skill_score = match_res["skill_score"]
                        existing_match.semantic_score = match_res["semantic_score"]
                        existing_match.experience_score = match_res["experience_score"]
                        existing_match.title_score = match_res["title_score"]
                        existing_match.location_score = match_res["location_score"]
                        existing_match.education_score = match_res["education_score"]
                        existing_match.matched_skills_json = json.dumps(match_res["matched_skills"])
                        existing_match.missing_skills_json = json.dumps(match_res["missing_skills"])
                        existing_match.explanation_json = json.dumps(match_res["explanation"])
                        existing_match.calculated_at = now
                        db.commit()
                    else:
                        new_match = JobMatch(
                            user_id=user_id,
                            resume_id=active_resume.id,
                            job_id=j.id,
                            overall_score=match_res["overall_score"],
                            skill_score=match_res["skill_score"],
                            semantic_score=match_res["semantic_score"],
                            experience_score=match_res["experience_score"],
                            title_score=match_res["title_score"],
                            location_score=match_res["location_score"],
                            education_score=match_res["education_score"],
                            matched_skills_json=json.dumps(match_res["matched_skills"]),
                            missing_skills_json=json.dumps(match_res["missing_skills"]),
                            explanation_json=json.dumps(match_res["explanation"]),
                            calculated_at=now,
                        )
                        db.add(new_match)
                        db.commit()

                    matched_count += 1

                    # 9: Auto-shortlist if score >= threshold
                    shortlisted = ShortlistService.auto_shortlist_if_eligible(
                        db=db,
                        user_id=user_id,
                        job_id=j.id,
                        resume_id=active_resume.id,
                        match_score=match_res["overall_score"],
                        threshold=min_score,
                    )
                    if shortlisted:
                        shortlisted_count += 1

            cls._last_run_time = datetime.now(timezone.utc)
            cls._last_run_stats = {
                "total_fetched": len(raw_jobs),
                "new_jobs_added": new_count,
                "existing_jobs_updated": updated_count,
                "jobs_matched": matched_count,
                "auto_shortlisted": shortlisted_count,
                "errors": source_errors,
            }
            return cls._last_run_stats

        finally:
            cls._is_running = False
