from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from uuid import UUID

from src.api.dependencies import get_current_user, require_role, get_db
from src.api.v1.schemas.candidates import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdate
)
from src.models import User
from src.services.candidates import (
    create_application, get_application, list_applications, update_application, get_job, get_candidate
)

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application_endpoint(
    request: ApplicationCreate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter", "Hiring Manager")),
    db=Depends(get_db),
):
    job = await get_job(db, request.job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    candidate = await get_candidate(db, request.candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    application = await create_application(
        db,
        organization_id=current_user.organization_id,
        job_id=request.job_id,
        candidate_id=request.candidate_id,
    )
    return application


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application_endpoint(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    application = await get_application(db, application_id)
    if not application or application.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.get("", response_model=list[ApplicationResponse])
async def list_applications_endpoint(
    job_id: Optional[UUID] = Query(None),
    candidate_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    applications = await list_applications(
        db, 
        organization_id=current_user.organization_id,
        job_id=job_id,
        candidate_id=candidate_id,
        status=status,
        limit=limit, 
        offset=skip
    )
    return applications


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application_endpoint(
    application_id: UUID,
    request: ApplicationUpdate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter", "Hiring Manager")),
    db=Depends(get_db),
):
    application = await get_application(db, application_id)
    if not application or application.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    
    updated_application = await update_application(db, application_id, **request.dict(exclude_unset=True))
    return updated_application
