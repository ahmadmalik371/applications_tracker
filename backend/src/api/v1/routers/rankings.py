import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.dependencies import get_current_user, get_db
from src.models import User, Candidate, Job
from src.services.ranking import RankingService


router = APIRouter(prefix="/api/v1/rankings", tags=["rankings"])
ranking_service = RankingService()


# Pydantic schemas
class CandidateRankingResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    candidate_email: str
    match_score: float
    confidence: float
    features: dict
    embedding_similarity: float
    breakdown: dict


class JobRankingResponse(BaseModel):
    job_id: str
    job_title: str
    job_location: Optional[str]
    match_score: float
    confidence: float
    features: dict
    embedding_similarity: float
    breakdown: dict


# Endpoints
@router.get("/candidates/for-job/{job_id}", response_model=List[CandidateRankingResponse])
async def rank_candidates_for_job(
    job_id: uuid.UUID,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Rank all candidates for a specific job.
    
    Returns candidates sorted by match score (highest first).
    """
    # Verify job exists and belongs to user's organization
    job_result = await session.execute(
        select(Job).where(Job.id == job_id).where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Rank candidates
    ranked = await ranking_service.rank_candidates_for_job(
        session, job_id, current_user.organization_id, limit
    )

    return ranked


@router.get("/jobs/for-candidate/{candidate_id}", response_model=List[JobRankingResponse])
async def rank_jobs_for_candidate(
    candidate_id: uuid.UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Rank all published jobs for a specific candidate.
    
    Returns jobs sorted by match score (highest first).
    """
    # Verify candidate exists and belongs to user's organization
    candidate_result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id).where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Rank jobs
    ranked = await ranking_service.rank_jobs_for_candidate(
        session, candidate_id, current_user.organization_id, limit
    )

    return ranked


@router.get("/match-score/{candidate_id}/{job_id}", response_model=dict)
async def get_match_score(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get detailed match score for a candidate-job pair.
    
    Returns score, confidence, features breakdown, and explanations.
    """
    # Verify candidate and job exist and belong to user's organization
    candidate_result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id).where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_result = await session.execute(
        select(Job).where(Job.id == job_id).where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate match score
    score_data = await ranking_service.calculate_match_score(candidate, job)

    return {
        "candidate_id": str(candidate.id),
        "candidate_email": candidate.email,
        "job_id": str(job.id),
        "job_title": job.title,
        **score_data,
    }
