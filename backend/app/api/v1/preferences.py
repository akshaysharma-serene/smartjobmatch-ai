import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.preference import JobSearchPreferences
from app.schemas.preference import PreferenceOut, PreferenceUpdate
from app.db.init_db import DEFAULT_ROLES, DEFAULT_LOCATIONS, DEFAULT_WORK_MODES, DEFAULT_WEIGHTS

router = APIRouter(prefix="/preferences", tags=["Preferences"])


def serialize_pref(pref: JobSearchPreferences) -> PreferenceOut:
    return PreferenceOut(
        id=pref.id,
        user_id=pref.user_id,
        keywords=json.loads(pref.keywords_json) if pref.keywords_json else DEFAULT_ROLES,
        locations=json.loads(pref.locations_json) if pref.locations_json else DEFAULT_LOCATIONS,
        work_modes=json.loads(pref.work_modes_json) if pref.work_modes_json else DEFAULT_WORK_MODES,
        minimum_experience=pref.minimum_experience,
        maximum_experience=pref.maximum_experience,
        minimum_match_score=pref.minimum_match_score,
        scoring_weights=json.loads(pref.scoring_weights_json) if pref.scoring_weights_json else DEFAULT_WEIGHTS,
        sync_frequency=pref.sync_frequency or "every_6_hours",
        created_at=pref.created_at,
        updated_at=pref.updated_at,
    )


@router.get("", response_model=PreferenceOut)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = db.query(JobSearchPreferences).filter(JobSearchPreferences.user_id == current_user.id).first()
    if not pref:
        pref = JobSearchPreferences(
            user_id=current_user.id,
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
    return serialize_pref(pref)


@router.put("", response_model=PreferenceOut)
def update_preferences(
    payload: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = db.query(JobSearchPreferences).filter(JobSearchPreferences.user_id == current_user.id).first()
    if not pref:
        pref = JobSearchPreferences(
            user_id=current_user.id,
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

    now = datetime.now(timezone.utc)
    if payload.keywords is not None:
        pref.keywords_json = json.dumps(payload.keywords)
    if payload.locations is not None:
        pref.locations_json = json.dumps(payload.locations)
    if payload.work_modes is not None:
        pref.work_modes_json = json.dumps(payload.work_modes)
    if payload.minimum_experience is not None:
        pref.minimum_experience = payload.minimum_experience
    if payload.maximum_experience is not None:
        pref.maximum_experience = payload.maximum_experience
    if payload.minimum_match_score is not None:
        pref.minimum_match_score = payload.minimum_match_score
    if payload.scoring_weights is not None:
        pref.scoring_weights_json = json.dumps(payload.scoring_weights)
    if payload.sync_frequency is not None:
        pref.sync_frequency = payload.sync_frequency

    pref.updated_at = now
    db.commit()
    db.refresh(pref)
    return serialize_pref(pref)

