import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.services.deduplication import DeduplicationService
from app.services.job_normalizer import JobNormalizerService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    yield db
    db.close()


def test_deduplication_service(test_db):
    raw_1 = {
        "source": "curated",
        "external_job_id": "job-101",
        "title": "Senior Java Developer",
        "company": "Target Tech",
        "description": "5+ years developing Spring Boot services.",
        "location": "Bengaluru",
        "job_url": "https://careers.target.com/jobs/101",
    }
    norm_1 = JobNormalizerService.normalize_job_dict(raw_1)
    job1, is_new1 = DeduplicationService.upsert_job(test_db, norm_1)
    assert is_new1 is True
    assert job1.id is not None

    # Upsert exact same job again
    job2, is_new2 = DeduplicationService.upsert_job(test_db, norm_1)
    assert is_new2 is False
    assert job2.id == job1.id

    # Same job with different external_id but same job_url
    raw_dup_url = dict(raw_1)
    raw_dup_url["external_job_id"] = "different-external-id"
    norm_dup_url = JobNormalizerService.normalize_job_dict(raw_dup_url)
    job3, is_new3 = DeduplicationService.upsert_job(test_db, norm_dup_url)
    assert is_new3 is False
    assert job3.id == job1.id

