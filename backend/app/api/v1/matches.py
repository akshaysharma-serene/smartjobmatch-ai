import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import JobMatch
from app.models.preference import JobSearchPreferences
from app.schemas.match import JobMatchOut, RunMatchRequest, MatchAnalytics, MissingSkills, MatchExplanation
from app.services.job_matcher import JobMatcherService
from app.services.shortlist_service import ShortlistService
from app.schemas.resume import ResumeParsedData
from app.api.v1.jobs import serialize_job

router = APIRouter(prefix="/matches", tags=["Matches"])


def serialize_match(match: JobMatch, job: Optional[Job] = None) -> JobMatchOut:
    m_skills = json.loads(match.matched_skills_json) if match.matched_skills_json else []
    miss_skills = json.loads(match.missing_skills_json) if match.missing_skills_json else {"required": [], "preferred": []}
    expl = json.loads(match.explanation_json) if match.explanation_json else {
        "summary": "", "strengths": [], "gaps": [], "experience_compatibility": "", "location_compatibility": "", "suggested_keywords": [], "breakdown_notes": {}
    }

    job_out = serialize_job(job or match.job, match.overall_score) if (job or match.job) else None

    return JobMatchOut(
        id=match.id,
        user_id=match.user_id,
        resume_id=match.resume_id,
        job_id=match.job_id,
        overall_score=match.overall_score,
        skill_score=match.skill_score,
        semantic_score=match.semantic_score,
        experience_score=match.experience_score,
        title_score=match.title_score,
        location_score=match.location_score,
        education_score=match.education_score,
        matched_skills=m_skills,
        missing_skills=MissingSkills(**miss_skills),
        explanation=MatchExplanation(**expl),
        calculated_at=match.calculated_at,
        job=job_out,
    )


@router.post("/run")
def run_matches(
    req: RunMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if req.resume_id:
        resume = db.query(Resume).filter(Resume.id == req.resume_id, Resume.user_id == current_user.id).first()
    else:
        resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()

    if not resume:
        raise HTTPException(status_code=400, detail="No active resume found. Please upload a resume first.")

    parsed_dict = json.loads(resume.parsed_data_json)
    parsed_resume = ResumeParsedData(**parsed_dict)

    pref = db.query(JobSearchPreferences).filter(JobSearchPreferences.user_id == current_user.id).first()
    weights = json.loads(pref.scoring_weights_json) if pref and pref.scoring_weights_json else None
    roles = json.loads(pref.keywords_json) if pref and pref.keywords_json else None
    work_modes = json.loads(pref.work_modes_json) if pref and pref.work_modes_json else None
    threshold = pref.minimum_match_score if pref else 70.0

    job_query = db.query(Job).filter(Job.status == "active")
    if req.job_ids:
        job_query = job_query.filter(Job.id.in_(req.job_ids))
    jobs = job_query.all()

    results = []
    for j in jobs:
        eval_res = JobMatcherService.evaluate_match(
            parsed_resume=parsed_resume,
            resume_raw_text=resume.extracted_text,
            job=j,
            custom_weights=weights,
            target_roles=roles,
            preferred_work_modes=work_modes,
        )

        match = db.query(JobMatch).filter(
            JobMatch.user_id == current_user.id,
            JobMatch.resume_id == resume.id,
            JobMatch.job_id == j.id,
        ).first()

        if match:
            match.overall_score = eval_res["overall_score"]
            match.skill_score = eval_res["skill_score"]
            match.semantic_score = eval_res["semantic_score"]
            match.experience_score = eval_res["experience_score"]
            match.title_score = eval_res["title_score"]
            match.location_score = eval_res["location_score"]
            match.education_score = eval_res["education_score"]
            match.matched_skills_json = json.dumps(eval_res["matched_skills"])
            match.missing_skills_json = json.dumps(eval_res["missing_skills"])
            match.explanation_json = json.dumps(eval_res["explanation"])
            db.commit()
            db.refresh(match)
        else:
            match = JobMatch(
                user_id=current_user.id,
                resume_id=resume.id,
                job_id=j.id,
                overall_score=eval_res["overall_score"],
                skill_score=eval_res["skill_score"],
                semantic_score=eval_res["semantic_score"],
                experience_score=eval_res["experience_score"],
                title_score=eval_res["title_score"],
                location_score=eval_res["location_score"],
                education_score=eval_res["education_score"],
                matched_skills_json=json.dumps(eval_res["matched_skills"]),
                missing_skills_json=json.dumps(eval_res["missing_skills"]),
                explanation_json=json.dumps(eval_res["explanation"]),
            )
            db.add(match)
            db.commit()
            db.refresh(match)

        # Auto-shortlist
        ShortlistService.auto_shortlist_if_eligible(
            db=db,
            user_id=current_user.id,
            job_id=j.id,
            resume_id=resume.id,
            match_score=eval_res["overall_score"],
            threshold=threshold,
        )
        results.append(serialize_match(match, j))

    return {
        "status": "success",
        "total_matched": len(results),
        "matches": results,
    }


@router.get("", response_model=List[JobMatchOut])
def get_matches(
    resume_id: Optional[int] = None,
    min_score: Optional[float] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(JobMatch).filter(JobMatch.user_id == current_user.id)
    if resume_id:
        query = query.filter(JobMatch.resume_id == resume_id)
    else:
        active_resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()
        if active_resume:
            query = query.filter(JobMatch.resume_id == active_resume.id)

    if min_score is not None:
        query = query.filter(JobMatch.overall_score >= min_score)

    matches = query.order_by(desc(JobMatch.overall_score)).limit(limit).all()
    return [serialize_match(m) for m in matches]


@router.get("/analytics", response_model=MatchAnalytics)
def get_match_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active_resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_active == True).first()
    if not active_resume:
        return MatchAnalytics(
            total_matched=0,
            excellent_matches=0,
            strong_matches=0,
            potential_matches=0,
            low_matches=0,
            average_score=0.0,
            top_matched_skills=[],
            top_missing_skills=[],
            score_distribution=[],
        )

    matches = db.query(JobMatch).filter(
        JobMatch.user_id == current_user.id,
        JobMatch.resume_id == active_resume.id,
    ).all()

    if not matches:
        return MatchAnalytics(
            total_matched=0,
            excellent_matches=0,
            strong_matches=0,
            potential_matches=0,
            low_matches=0,
            average_score=0.0,
            top_matched_skills=[],
            top_missing_skills=[],
            score_distribution=[],
        )

    scores = [m.overall_score for m in matches]
    excellent = sum(1 for s in scores if s >= 85.0)
    strong = sum(1 for s in scores if 70.0 <= s < 85.0)
    potential = sum(1 for s in scores if 55.0 <= s < 70.0)
    low = sum(1 for s in scores if s < 55.0)
    avg_score = round(sum(scores) / len(scores), 1)

    # Skills counts
    matched_counts = {}
    missing_counts = {}
    for m in matches:
        ms = json.loads(m.matched_skills_json) if m.matched_skills_json else []
        for s in ms:
            matched_counts[s] = matched_counts.get(s, 0) + 1

        miss = json.loads(m.missing_skills_json) if m.missing_skills_json else {}
        for s in miss.get("required", []) + miss.get("preferred", []):
            missing_counts[s] = missing_counts.get(s, 0) + 1

    top_matched = [{"skill": k, "count": v} for k, v in sorted(matched_counts.items(), key=lambda x: x[1], reverse=True)[:8]]
    top_missing = [{"skill": k, "count": v} for k, v in sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:8]]

    # Distribution buckets for chart
    dist_buckets = [
        {"range": "90-100%", "count": sum(1 for s in scores if s >= 90)},
        {"range": "80-89%", "count": sum(1 for s in scores if 80 <= s < 90)},
        {"range": "70-79%", "count": sum(1 for s in scores if 70 <= s < 80)},
        {"range": "60-69%", "count": sum(1 for s in scores if 60 <= s < 70)},
        {"range": "50-59%", "count": sum(1 for s in scores if 50 <= s < 60)},
        {"range": "<50%", "count": sum(1 for s in scores if s < 50)},
    ]

    return MatchAnalytics(
        total_matched=len(matches),
        excellent_matches=excellent,
        strong_matches=strong,
        potential_matches=potential,
        low_matches=low,
        average_score=avg_score,
        top_matched_skills=top_matched,
        top_missing_skills=top_missing,
        score_distribution=dist_buckets,
    )


@router.get("/{match_id}", response_model=JobMatchOut)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(JobMatch).filter(JobMatch.id == match_id, JobMatch.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found")
    return serialize_match(match)

