import json
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.preference import JobSearchPreferences
from app.core.security import hash_password

DEFAULT_ROLES = [
    "Senior Java Developer",
    "Java Backend Developer",
    "Java Software Engineer",
    "Spring Boot Developer",
    "Microservices Engineer",
    "Full-Stack Developer — Java + React",
    "Full-Stack Software Engineer",
    "Cloud-Native Java Engineer",
]

DEFAULT_LOCATIONS = ["Bengaluru, Karnataka, India", "Remote"]
DEFAULT_WORK_MODES = ["Remote", "Hybrid", "On-site"]

DEFAULT_WEIGHTS = {
    "technical_skills": 0.35,
    "semantic_similarity": 0.25,
    "experience": 0.15,
    "job_title": 0.10,
    "location_work_mode": 0.10,
    "education_certifications": 0.05,
}


def init_db(db: Session) -> User:
    Base.metadata.create_all(bind=engine)

    # Ensure default user exists
    user = db.query(User).filter(User.email == "akshay@smartjobmatch.ai").first()
    if not user:
        user = User(
            email="akshay@smartjobmatch.ai",
            password_hash=hash_password("SmartJobMatch2026!"),
            full_name="Akshay Sharma",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Ensure preferences exist for this user
    pref = db.query(JobSearchPreferences).filter(JobSearchPreferences.user_id == user.id).first()
    if not pref:
        pref = JobSearchPreferences(
            user_id=user.id,
            keywords_json=json.dumps(DEFAULT_ROLES),
            locations_json=json.dumps(DEFAULT_LOCATIONS),
            work_modes_json=json.dumps(DEFAULT_WORK_MODES),
            minimum_experience=4.0,
            maximum_experience=10.0,
            minimum_match_score=70.0,
            scoring_weights_json=json.dumps(DEFAULT_WEIGHTS),
            sync_frequency="every_6_hours",
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return user

