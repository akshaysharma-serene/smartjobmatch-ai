import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.models.job import Job
from app.models.preference import JobSearchPreferences
from app.core.security import hash_password

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Seed user
    u = User(email="test@smartjobmatch.ai", password_hash=hash_password("Pass123!"), full_name="Test User")
    db.add(u)
    db.commit()
    db.refresh(u)
    p = JobSearchPreferences(
        user_id=u.id,
        keywords_json='["Senior Java Developer"]',
        locations_json='["Bengaluru, Karnataka, India"]',
        work_modes_json='["Hybrid"]',
        minimum_match_score=70.0,
        scoring_weights_json='{"technical_skills": 0.35, "semantic_similarity": 0.25, "experience": 0.15, "job_title": 0.10, "location_work_mode": 0.10, "education_certifications": 0.05}',
        sync_frequency="every_6_hours",
    )
    db.add(p)
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=test_engine)


def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "app_name" in data


def test_auth_login():
    res = client.post("/api/auth/login", json={"email": "test@smartjobmatch.ai", "password": "Pass123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_preferences_get_and_put():
    res_get = client.get("/api/preferences")
    assert res_get.status_code == 200
    assert "Senior Java Developer" in res_get.json()["keywords"]

    # Update preferences
    res_put = client.put("/api/preferences", json={"minimum_match_score": 75.0, "sync_frequency": "daily"})
    assert res_put.status_code == 200
    assert res_put.json()["minimum_match_score"] == 75.0


def test_job_import_and_list():
    res_import = client.post("/api/jobs/import", json={
        "title": "Cloud-Native Java Engineer",
        "company": "TestCorp",
        "description": "Building Java microservices with Spring Boot and AWS.",
        "location": "Bengaluru",
        "work_mode": "Hybrid",
    })
    assert res_import.status_code == 200
    job_id = res_import.json()["id"]

    res_list = client.get("/api/jobs")
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 1
