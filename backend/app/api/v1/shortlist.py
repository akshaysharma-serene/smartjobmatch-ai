from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.shortlist import ShortlistedJob
from app.models.match import JobMatch
from app.models.resume import Resume
from app.schemas.shortlist import ShortlistOut, ShortlistCreate, ShortlistUpdate
from app.api.v1.jobs import serialize_job
from app.api.v1.matches import serialize_match
from app.services.shortlist_service import ShortlistService

router = APIRouter(prefix="/shortlist", tags=["Shortlist"])


def serialize_shortlist(entry: ShortlistedJob, db: Session, user_id: int) -> ShortlistOut:
    job_out = serialize_job(entry.job, entry.match_score)
    # Fetch active match
    match = db.query(JobMatch).filter(
        JobMatch.user_id == user_id,
        JobMatch.job_id == entry.job_id,
    ).first()
    match_out = serialize_match(match, entry.job) if match else None

    return ShortlistOut(
        id=entry.id,
        user_id=entry.user_id,
        job_id=entry.job_id,
        resume_id=entry.resume_id,
        status=entry.status,
        match_score=entry.match_score,
        notes=entry.notes,
        shortlisted_at=entry.shortlisted_at,
        updated_at=entry.updated_at,
        job=job_out,
        match=match_out,
    )


@router.get("", response_model=List[ShortlistOut])
def get_shortlisted_jobs(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ShortlistedJob).filter(ShortlistedJob.user_id == current_user.id)
    if status_filter:
        query = query.filter(ShortlistedJob.status == status_filter)
    else:
        # Default view excludes rejected
        query = query.filter(ShortlistedJob.status != "rejected")

    entries = query.order_by(desc(ShortlistedJob.match_score)).all()
    return [serialize_shortlist(e, db, current_user.id) for e in entries]


@router.post("/{job_id}", response_model=ShortlistOut)
def add_to_shortlist(
    job_id: int,
    payload: Optional[ShortlistCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req_status = payload.status if payload and payload.status else "shortlisted"
    req_notes = payload.notes if payload else None

    entry = ShortlistService.update_status(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
        status=req_status,
        notes=req_notes,
    )
    return serialize_shortlist(entry, db, current_user.id)


@router.patch("/{job_id}", response_model=ShortlistOut)
def update_shortlist_entry(
    job_id: int,
    payload: ShortlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = ShortlistService.update_status(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
        status=payload.status or "shortlisted",
        notes=payload.notes,
    )
    return serialize_shortlist(entry, db, current_user.id)


@router.delete("/{job_id}")
def delete_shortlist_entry(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = ShortlistService.remove_from_shortlist(db, current_user.id, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shortlist record not found")
    return {"message": "Job removed from shortlist successfully"}

