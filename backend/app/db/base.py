# Import all the models, so that Base has them before being
# imported by Alembic or initialization scripts
from app.db.session import Base
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import JobMatch
from app.models.shortlist import ShortlistedJob
from app.models.application import JobApplication
from app.models.preference import JobSearchPreferences

__all__ = [
    "Base",
    "User",
    "Resume",
    "Job",
    "JobMatch",
    "ShortlistedJob",
    "JobApplication",
    "JobSearchPreferences",
]

