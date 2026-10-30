import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeOut, ResumeUpdate, ResumeParsedData
from app.services.resume_parser import ResumeParserService
from app.services.job_sync_service import JobSyncService

router = APIRouter(prefix="/resumes", tags=["Resumes"])
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def serialize_resume(resume: Resume) -> ResumeOut:
    parsed = json.loads(resume.parsed_data_json)
    return ResumeOut(
        id=resume.id,
        user_id=resume.user_id,
        filename=resume.filename,
        extracted_text=resume.extracted_text,
        parsed_data=ResumeParsedData(**parsed),
        version=resume.version,
        is_active=resume.is_active,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename = file.filename or "resume.pdf"
    ext = filename.lower().split(".")[-1]
    if ext not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx).",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10 MB limit.",
        )

    # Extract text
    try:
        if ext == "pdf":
            extracted_text = ResumeParserService.extract_text_from_pdf(file_bytes)
        else:
            extracted_text = ResumeParserService.extract_text_from_docx(file_bytes)
    except Exception as e:
        logger.error(f"Error parsing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to read file contents: {str(e)}",
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded resume appeared empty or could not be read as text.",
        )

    # Parse structured resume fields
    parsed_data = ResumeParserService.parse_resume(extracted_text, filename)

    # Handle versions and active status
    existing_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    next_version = len(existing_resumes) + 1

    # Deactivate previous resumes so this one becomes active
    for r in existing_resumes:
        r.is_active = False

    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        extracted_text=extracted_text,
        parsed_data_json=json.dumps(parsed_data.model_dump()),
        version=next_version,
        is_active=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Trigger matching against available jobs asynchronously/inline
    try:
        await JobSyncService.run_sync_pipeline(db, current_user.id)
    except Exception as e:
        logger.warning(f"Post-upload sync warning: {e}")

    return serialize_resume(resume)


@router.get("", response_model=List[ResumeOut])
def get_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.version.desc()).all()
    return [serialize_resume(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return serialize_resume(resume)


@router.put("/{resume_id}", response_model=ResumeOut)
async def update_resume(
    resume_id: int,
    update_in: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if update_in.filename is not None:
        resume.filename = update_in.filename

    if update_in.is_active is True:
        # Deactivate other resumes
        others = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.id != resume_id).all()
        for o in others:
            o.is_active = False
        resume.is_active = True

    if update_in.parsed_data is not None:
        resume.parsed_data_json = json.dumps(update_in.parsed_data.model_dump())

    db.commit()
    db.refresh(resume)

    # If it is active, re-run matching
    if resume.is_active:
        try:
            await JobSyncService.run_sync_pipeline(db, current_user.id)
        except Exception as e:
            logger.warning(f"Post-update sync warning: {e}")

    return serialize_resume(resume)


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}

