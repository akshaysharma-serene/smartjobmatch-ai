import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.user import User
from app.models.resume import Resume
from app.models.preference import JobSearchPreferences
from app.services.job_sync_service import JobSyncService
from app.services.resume_parser import ResumeParserService
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_job_sync_pipeline_execution():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    user = User(email="sync@test.com", password_hash=hash_password("pw"), full_name="Sync User")
    db.add(user)
    db.commit()

    pref = JobSearchPreferences(
        user_id=user.id,
        keywords_json='["Senior Java Developer"]',
        locations_json='["Bengaluru, Karnataka, India"]',
        work_modes_json='["Hybrid"]',
        minimum_match_score=70.0,
        scoring_weights_json='{"technical_skills": 0.35, "semantic_similarity": 0.25, "experience": 0.15, "job_title": 0.10, "location_work_mode": 0.10, "education_certifications": 0.05}',
        sync_frequency="every_6_hours",
    )
    db.add(pref)
    db.commit()

    # Run pipeline
    stats = await JobSyncService.run_sync_pipeline(db, user.id)
    assert stats["total_fetched"] > 0
    assert stats["new_jobs_added"] > 0
    assert isinstance(stats["errors"], dict)

    # Re-run pipeline to ensure idempotency
    stats_rerun = await JobSyncService.run_sync_pipeline(db, user.id)
    assert stats_rerun["new_jobs_added"] == 0
    assert stats_rerun["existing_jobs_updated"] > 0

    db.close()

