import os
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import SessionLocal, Base, engine
from app.db.init_db import init_db
from app.models.resume import Resume
from app.services.resume_parser import ResumeParserService
from app.services.job_sync_service import JobSyncService
from app.scheduler.scheduler import start_scheduler, stop_scheduler

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.shortlist import router as shortlist_router
from app.api.v1.applications import router as applications_router
from app.api.v1.preferences import router as preferences_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartjobmatch")


async def background_initial_sync(user_id: int):
    logger.info("Running initial job discovery and matching in background...")
    sync_db = SessionLocal()
    try:
        await JobSyncService.run_sync_pipeline(sync_db, user_id)
        logger.info("Initial job discovery and matching completed.")
    except Exception as e:
        logger.warning(f"Initial sync warning: {e}")
    finally:
        sync_db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SmartJobMatch AI backend...")
    db = SessionLocal()
    try:
        user = init_db(db)

        # Auto-seed resume if Full_Stack_Software_Engineer.pdf exists and user has no resume yet
        existing_resume = db.query(Resume).filter(Resume.user_id == user.id).first()
        if not existing_resume:
            potential_paths = [
                Path(__file__).resolve().parent.parent.parent / "Full_Stack_Software_Engineer.pdf",
                Path(__file__).resolve().parent.parent / "Full_Stack_Software_Engineer.pdf",
                Path(r"C:\Users\aksha\Downloads\Full_Stack_Software_Engineer.pdf"),
            ]
            for p in potential_paths:
                if p.exists():
                    try:
                        logger.info(f"Auto-importing candidate resume from {p}...")
                        text = ResumeParserService.extract_text_from_pdf(p.read_bytes())
                        parsed = ResumeParserService.parse_resume(text, p.name)
                        seeded_resume = Resume(
                            user_id=user.id,
                            filename=p.name,
                            extracted_text=text,
                            parsed_data_json=json.dumps(parsed.model_dump()),
                            version=1,
                            is_active=True,
                        )
                        db.add(seeded_resume)
                        db.commit()
                        logger.info("Successfully seeded primary resume!")
                        break
                    except Exception as e:
                        logger.warning(f"Could not auto-seed resume from {p}: {e}")

        # Kick off initial job discovery and matching asynchronously
        asyncio.create_task(background_initial_sync(user.id))
    finally:
        db.close()

    # Start scheduled background synchronizer
    start_scheduler()

    yield

    # Shutdown
    stop_scheduler()
    logger.info("SmartJobMatch AI backend stopped.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Resume-to-Job Matching and Discovery Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(matches_router, prefix="/api")
app.include_router(shortlist_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(preferences_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to SmartJobMatch AI API",
        "docs": "/docs",
        "health": "/api/health",
    }
