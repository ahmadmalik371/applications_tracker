from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_current_user, require_role, get_db
from src.api.v1.schemas.candidates import (
    JobCreate, JobResponse, JobUpdate,
    CandidateCreate, CandidateResponse, CandidateUpdate,
    ApplicationCreate, ApplicationResponse, ApplicationUpdate
)
from src.api.v1.schemas.uploads import ResumeUploadResponse
from src.models import User
from src.services.candidates import (
    create_job, get_job, list_jobs, update_job, delete_job,
    create_candidate, get_candidate, list_candidates, update_candidate, delete_candidate,
    create_application, get_application, list_applications, update_application,
)
from src.services.upload import save_resume_file
from src.services.search import find_similar_candidates, find_matching_jobs, hybrid_search_candidates

router = APIRouter(prefix="/candidates", tags=["Candidates"])




# Candidate endpoints
@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate_endpoint(
    request: CandidateCreate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter")),
    db=Depends(get_db),
):
    candidate = await create_candidate(
        db,
        organization_id=current_user.organization_id,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
    )
    return candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate_endpoint(
    candidate_id: UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    candidate = await get_candidate(db, candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.get("", response_model=list[CandidateResponse])
async def list_candidates_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    candidates = await list_candidates(db, organization_id=current_user.organization_id, limit=limit, offset=skip)
    return candidates


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate_endpoint(
    candidate_id: UUID,
    request: CandidateUpdate,
    current_user: User = Depends(require_role("Company Admin", "Recruiter")),
    db=Depends(get_db),
):
    candidate = await get_candidate(db, candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    updated_candidate = await update_candidate(db, candidate_id, **request.dict(exclude_unset=True))
    return updated_candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate_endpoint(
    candidate_id: UUID,
    current_user: User = Depends(require_role("Company Admin")),
    db=Depends(get_db),
):
    candidate = await get_candidate(db, candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    await delete_candidate(db, candidate_id)





# Resume upload endpoint
@router.post("/{candidate_id}/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    candidate_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("Company Admin", "Recruiter")),
    db=Depends(get_db),
):
    """Upload and validate resume for a candidate."""
    candidate = await get_candidate(db, candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    # Save resume file
    resume_url, file_size = await save_resume_file(file, str(candidate_id))
    
    # Update candidate with resume URL
    updated_candidate = await update_candidate(db, candidate_id, resume_url=resume_url)
    
    # Trigger async parsing task
    from src.tasks import parse_resume_task
    parse_resume_task.delay(str(candidate_id), resume_url)
    
    return ResumeUploadResponse(
        candidate_id=candidate_id,
        resume_url=resume_url,
        file_name=file.filename,
        file_size=file_size,
        uploaded_at=updated_candidate.updated_at,
    )


# Vector search endpoints
@router.get("/jobs/{job_id}/similar-candidates")
async def get_similar_candidates(
    job_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_role("Company Admin", "Recruiter", "Hiring Manager")),
    db=Depends(get_db),
):
    """Get candidates most similar to a job using semantic matching."""
    job = await get_job(db, job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    similar_candidates = await find_similar_candidates(
        db, job_id, current_user.organization_id, limit=limit
    )
    return {"job_id": job_id, "similar_candidates": similar_candidates}


@router.get("/{candidate_id}/matching-jobs")
async def get_matching_jobs(
    candidate_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get jobs most suitable for a candidate using semantic matching."""
    candidate = await get_candidate(db, candidate_id)
    if not candidate or candidate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    
    matching_jobs = await find_matching_jobs(
        db, candidate_id, current_user.organization_id, limit=limit
    )
    return {"candidate_id": candidate_id, "matching_jobs": matching_jobs}


@router.get("/search/hybrid")
async def hybrid_search(
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(20, ge=1, le=100),
    semantic_weight: float = Query(0.6, ge=0, le=1),
    keyword_weight: float = Query(0.4, ge=0, le=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Hybrid candidate search combining PostgreSQL full-text and pgvector semantic similarity."""
    results = await hybrid_search_candidates(
        db,
        q,
        current_user.organization_id,
        limit=limit,
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight,
    )
    return {"query": q, "count": len(results), "results": results}
