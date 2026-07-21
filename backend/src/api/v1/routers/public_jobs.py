"""
Public-facing job board and candidate application endpoints.
No authentication required - candidates can browse jobs and apply.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.models import Job
from src.services.candidates import create_application, create_candidate
from src.services.upload import save_resume_file

router = APIRouter(prefix="/public", tags=["Public"])


class PublicJobResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    status: str
    score: float | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/jobs", response_model=list[PublicJobResponse])
async def list_public_jobs(
    db: AsyncSession = Depends(get_db),
):
    """List all published/open jobs for the public job board."""
    result = await db.execute(
        select(Job)
        .where(Job.status == "Open")
        .where(Job.is_published == True)
        .order_by(desc(Job.created_at))
    )
    jobs = result.scalars().all()
    return [
        PublicJobResponse(
            id=str(j.id),
            title=j.title,
            description=j.description,
            location=j.location,
            employment_type=j.employment_type,
            status=j.status,
            created_at=j.created_at,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}", response_model=PublicJobResponse)
async def get_public_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single published job by ID."""
    result = await db.execute(
        select(Job).where(Job.id == job_id).where(Job.is_published == True)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return PublicJobResponse(
        id=str(job.id),
        title=job.title,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        status=job.status,
        created_at=job.created_at,
    )


@router.post(
    "/jobs/{job_id}/apply",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_job(
    job_id: uuid.UUID,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    resume: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Public application endpoint - candidates can apply with resume upload."""
    # Verify job exists and is open
    result = await db.execute(
        select(Job).where(Job.id == job_id).where(Job.is_published == True)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Create candidate
    candidate = await create_candidate(
        db,
        organization_id=job.organization_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
    )

    # Save resume
    resume_url, file_size = await save_resume_file(resume, str(candidate.id))

    # Update candidate with resume URL
    from src.services.candidates import update_candidate

    await update_candidate(db, candidate.id, resume_url=resume_url)

    # Create application
    application = await create_application(
        db,
        organization_id=job.organization_id,
        job_id=job_id,
        candidate_id=candidate.id,
    )

    await db.commit()
    await db.refresh(application)

    # Trigger async resume parsing and scoring
    from src.tasks import parse_resume_task

    parse_resume_task.delay(str(candidate.id), resume_url, str(job_id))

    return ApplicationResponse(
        id=str(application.id),
        candidate_id=str(candidate.id),
        job_id=str(job_id),
        status=application.status,
        score=application.score,
        created_at=application.created_at,
    )
