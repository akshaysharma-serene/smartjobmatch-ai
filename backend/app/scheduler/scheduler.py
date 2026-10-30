import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import SessionLocal
from app.services.job_sync_service import JobSyncService
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_sync_task():
    logger.info("Starting background scheduled job synchronization...")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            try:
                stats = await JobSyncService.run_sync_pipeline(db, user.id)
                logger.info(f"Scheduled sync complete for user {user.email}: {stats}")
            except Exception as e:
                logger.error(f"Error syncing jobs for user {user.email}: {e}")
    finally:
        db.close()


def start_scheduler():
    if not settings.ENABLE_SCHEDULED_SYNC:
        logger.info("Scheduled synchronization is disabled in settings.")
        return

    hours = settings.SYNC_SCHEDULE_HOURS or 6
    scheduler.add_job(
        scheduled_sync_task,
        "interval",
        hours=hours,
        id="job_sync_task",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"APScheduler started: syncing jobs every {hours} hours.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")

