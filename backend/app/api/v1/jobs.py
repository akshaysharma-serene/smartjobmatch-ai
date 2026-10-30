import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.match import JobMatch
from app.models.resume import Resume
from app.schemas.job import JobOut, JobListResponse, JobSearchQuery, JobImportRequest
from app.services.job_normalizer import JobNormalizerService
from app.services.deduplication import DeduplicationService
from app.services.job_sync_service import JobSyncService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def serialize_job(job: Job, match_score: Optional[float] = None) -> JobOut:
    req_skills = json.loads(job.required_skills_json) if job.required_skills_json else []
    pref_skills = json.loads(job.preferred_skills_json) if job.preferred_skills_json else []

    return JobOut(
        id=job.id,
        source=job.source,
        external_job_id=job.external_job_id,
        title=job.title,
        company=job.company,
        description=job.description,
        location=job.location,
        work_mode=job.work_mode,
        employment_type=job.employment_type or "Full-time",
        required_skills=req_skills,
        preferred_skills=pref_skills,
        minimum_experience=job.minimum_experience,
        maximum_experience=job.maximum_experience,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency or "INR",
        posted_at=job.posted_at,
        job_url=job.job_url,
        application_url=job.application_url,
        status=job.status,
        content_hash=job.content_hash,
        first_seen_at=job.first_seen_at,
        last_seen_at=job.last_seen_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
        match_score=match_score,
    )


@router.get("", response_model=JobListResponse)
def get_jobs(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("match_score"),  # match_score, posted_at, created_at
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Job)

    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(kw),
                Job.company.ilike(kw),
                Job.description.ilike(kw),
                Job.required_skills_json.ilike(kw),
            )
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if work_mode:
        query = query.filter(Job.work_mode.ilike(f"%{work_mode}%"))

    if source:
        query = query.filter(Job.source == source)

    # Find active resume to join match scores
    active_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()

    all_jobs = query.all()

    # Build score map
    score_map = {}
    if active_resume:
        matches = db.query(JobMatch).filter(
            JobMatch.user_id == current_user.id,
            JobMatch.resume_id == active_resume.id,
        ).all()
        score_map = {m.job_id: m.overall_score for m in matches}

    # Attach score
    decorated = []
    for j in all_jobs:
        score = score_map.get(j.id)
        if min_score is not None:
            if score is None or score < min_score:
                continue
        decorated.append((j, score if score is not None else -1.0))

    # Sort
    is_desc = (sort_order.lower() == "desc")
    if sort_by == "match_score":
        decorated.sort(key=lambda x: x[1], reverse=is_desc)
    elif sort_by == "posted_at":
        decorated.sort(key=lambda x: x[0].posted_at or datetime.min.replace(tzinfo=timezone.utc), reverse=is_desc)
    else:
        decorated.sort(key=lambda x: x[0].created_at, reverse=is_desc)

    total = len(decorated)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    sliced = decorated[start_idx:end_idx]

    items = [serialize_job(j, score if score >= 0 else None) for j, score in sliced]

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/search", response_model=JobListResponse)
def search_jobs(
    search_in: JobSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_jobs(
        keyword=search_in.keyword,
        location=search_in.location,
        work_mode=search_in.work_mode,
        source=search_in.source,
        min_score=search_in.min_score,
        page=search_in.page,
        page_size=search_in.page_size,
        sort_by=search_in.sort_by,
        sort_order=search_in.sort_order,
        db=db,
        current_user=current_user,
    )


@router.get("/sync/status")
def sync_status():
    return JobSyncService.get_sync_status()


@router.post("/sync")
async def trigger_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await JobSyncService.run_sync_pipeline(db, current_user.id)
    return {
        "status": "success",
        "message": "Job discovery synchronization pipeline completed.",
        "results": res,
    }


@router.post("/import", response_model=JobOut)
def import_job(
    import_in: JobImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_dict = {
        "source": import_in.source or "manual",
        "external_job_id": f"manual-{int(datetime.now().timestamp())}",
        "title": import_in.title,
        "company": import_in.company,
        "description": import_in.description,
        "location": import_in.location,
        "work_mode": import_in.work_mode,
        "application_url": import_in.application_url or import_in.job_url,
        "job_url": import_in.job_url,
        "required_skills": import_in.required_skills,
        "preferred_skills": import_in.preferred_skills,
        "minimum_experience": import_in.minimum_experience,
    }
    norm_dict = JobNormalizerService.normalize_job_dict(raw_dict)
    job, is_new = DeduplicationService.upsert_job(db, norm_dict)
    return serialize_job(job)


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check match score for active resume
    active_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    match_score = None
    if active_resume:
        match = db.query(JobMatch).filter(
            JobMatch.user_id == current_user.id,
            JobMatch.resume_id == active_resume.id,
            JobMatch.job_id == job.id,
        ).first()
        if match:
            match_score = match.overall_score

    return serialize_job(job, match_score)

