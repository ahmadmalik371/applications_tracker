from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.api.dependencies import get_current_user, require_role, get_db
from src.api.v1.schemas.candidates import JobCreate, JobResponse, JobUpdate
from src.models import User
from src.services.candidates import (
    create_job, get_job, list_jobs, update_job, delete_job
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    request: JobCreate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter", "Hiring Manager")),
    db=Depends(get_db),
):
    job = await create_job(
        db,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        title=request.title,
        description=request.description,
        location=request.location,
        department=request.department,
        salary_range=request.salary_range,
        deadline=request.deadline,
        employment_type=request.employment_type,
    )
    
    # Trigger embedding generation for job
    if job.description:
        from src.tasks import generate_job_embedding_task
        generate_job_embedding_task.delay(str(job.id), job.description)
    
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_endpoint(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    job = await get_job(db, job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("", response_model=list[JobResponse])
async def list_jobs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    jobs = await list_jobs(db, organization_id=current_user.organization_id, limit=limit, offset=skip)
    return jobs


@router.put("/{job_id}", response_model=JobResponse)
async def update_job_endpoint(
    job_id: UUID,
    request: JobUpdate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter")),
    db=Depends(get_db),
):
    job = await get_job(db, job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    updated_job = await update_job(db, job_id, **request.dict(exclude_unset=True))
    return updated_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_endpoint(
    job_id: UUID,
    current_user: User = Depends(require_role("Company Admin")),
    db=Depends(get_db),
):
    job = await get_job(db, job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    await delete_job(db, job_id)
