from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.application import JobApplication
from app.models.job import Job
from app.schemas.application import ApplicationOut, ApplicationCreate, ApplicationUpdate
from app.api.v1.jobs import serialize_job

router = APIRouter(prefix="/applications", tags=["Applications"])


def serialize_application(app_entry: JobApplication) -> ApplicationOut:
    return ApplicationOut(
        id=app_entry.id,
        user_id=app_entry.user_id,
        job_id=app_entry.job_id,
        application_status=app_entry.application_status,
        applied_at=app_entry.applied_at,
        follow_up_date=app_entry.follow_up_date,
        notes=app_entry.notes,
        created_at=app_entry.created_at,
        updated_at=app_entry.updated_at,
        job=serialize_job(app_entry.job),
    )


@router.get("", response_model=List[ApplicationOut])
def get_applications(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    if status_filter:
        query = query.filter(JobApplication.application_status == status_filter)
    apps = query.order_by(desc(JobApplication.updated_at)).all()
    return [serialize_application(a) for a in apps]


@router.post("", response_model=ApplicationOut)
def create_or_update_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == payload.job_id,
    ).first()

    now = datetime.now(timezone.utc)
    if existing:
        existing.application_status = payload.application_status
        if payload.applied_at:
            existing.applied_at = payload.applied_at
        elif payload.application_status == "Applied" and not existing.applied_at:
            existing.applied_at = now
        if payload.follow_up_date:
            existing.follow_up_date = payload.follow_up_date
        if payload.notes is not None:
            existing.notes = payload.notes
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return serialize_application(existing)

    new_app = JobApplication(
        user_id=current_user.id,
        job_id=payload.job_id,
        application_status=payload.application_status,
        applied_at=payload.applied_at or (now if payload.application_status == "Applied" else None),
        follow_up_date=payload.follow_up_date,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return serialize_application(new_app)


@router.patch("/{application_id}", response_model=ApplicationOut)
def patch_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_entry = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id,
    ).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application record not found")

    now = datetime.now(timezone.utc)
    if payload.application_status is not None:
        app_entry.application_status = payload.application_status
        if payload.application_status == "Applied" and not app_entry.applied_at:
            app_entry.applied_at = now
    if payload.applied_at is not None:
        app_entry.applied_at = payload.applied_at
    if payload.follow_up_date is not None:
        app_entry.follow_up_date = payload.follow_up_date
    if payload.notes is not None:
        app_entry.notes = payload.notes

    app_entry.updated_at = now
    db.commit()
    db.refresh(app_entry)
    return serialize_application(app_entry)

