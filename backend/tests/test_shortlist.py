import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.user import User
from app.models.job import Job
from app.services.shortlist_service import ShortlistService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    user = User(email="test@user.com", password_hash="hash", full_name="Tester")
    session.add(user)
    session.commit()

    job = Job(
        source="mock",
        external_job_id="j-1",
        title="Java Dev",
        company="Co",
        description="Desc",
        content_hash="hash123",
    )
    session.add(job)
    session.commit()

    yield session
    session.close()


def test_auto_shortlist_threshold(db):
    user = db.query(User).first()
    job = db.query(Job).first()

    # Below threshold (e.g. 65 < 70)
    entry_none = ShortlistService.auto_shortlist_if_eligible(
        db, user.id, job.id, resume_id=1, match_score=65.0, threshold=70.0
    )
    assert entry_none is None

    # At or above threshold (e.g. 85 >= 70)
    entry_added = ShortlistService.auto_shortlist_if_eligible(
        db, user.id, job.id, resume_id=1, match_score=85.0, threshold=70.0
    )
    assert entry_added is not None
    assert entry_added.status == "shortlisted"
    assert entry_added.match_score == 85.0


def test_shortlist_manual_update_and_delete(db):
    user = db.query(User).first()
    job = db.query(Job).first()

    entry = ShortlistService.update_status(db, user.id, job.id, status="saved", notes="My dream job")
    assert entry.status == "saved"
    assert entry.notes == "My dream job"

    # Remove
    deleted = ShortlistService.remove_from_shortlist(db, user.id, job.id)
    assert deleted is True

