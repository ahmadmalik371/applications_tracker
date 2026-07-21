import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import Candidate, Job, RankingHistory, User
from src.services.explainability import ExplainabilityService
from src.services.ranking import RankingService

router = APIRouter(prefix="/api/v1/rankings", tags=["rankings"])
ranking_service = RankingService()
explainability_service = ExplainabilityService()


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
    job_location: str | None
    match_score: float
    confidence: float
    features: dict
    embedding_similarity: float
    breakdown: dict


class ExplanationResponse(BaseModel):
    summary: str
    match_score: float
    confidence: float
    strengths: list[str]
    weaknesses: list[str]
    skill_analysis: dict
    recommendations: list[str]
    next_steps: list[str]


class ReRankRequest(BaseModel):
    embedding_weight: float = 0.3
    feature_weight: float = 0.7


class CompareRequest(BaseModel):
    candidate_ids: list[str]
    job_id: str


class RankingHistoryResponse(BaseModel):
    id: str
    job_id: str
    embedding_weight: float
    feature_weight: float
    candidate_count: int
    top_score: float | None
    created_at: str
    results: list

    class Config:
        from_attributes = True


class PaginatedRankingResponse(BaseModel):
    items: list[CandidateRankingResponse]
    total: int
    skip: int
    limit: int


# Endpoints
@router.get(
    "/candidates/for-job/{job_id}", response_model=list[CandidateRankingResponse]
)
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
        select(Job)
        .where(Job.id == job_id)
        .where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Rank candidates
    ranked = await ranking_service.rank_candidates_for_job(
        session, job_id, current_user.organization_id, limit
    )

    return ranked


@router.get(
    "/jobs/for-candidate/{candidate_id}", response_model=list[JobRankingResponse]
)
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
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
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
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_result = await session.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.organization_id == current_user.organization_id)
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


@router.get("/explain/{candidate_id}/{job_id}", response_model=ExplanationResponse)
async def get_explanation(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get AI-generated explanation for candidate-job match.

    Returns summary, strengths, weaknesses, skill analysis, and recommendations.
    """
    # Verify candidate and job exist and belong to user's organization
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_result = await session.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate score and generate explanation
    score_data = await ranking_service.calculate_match_score(candidate, job)
    explanation = await explainability_service.generate_explanation(
        candidate, job, score_data
    )

    return explanation


# Re-rank with custom weights
@router.post(
    "/candidates/re-rank/{job_id}", response_model=list[CandidateRankingResponse]
)
async def re_rank_candidates_for_job(
    job_id: uuid.UUID,
    request: ReRankRequest,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Re-rank candidates for a job using custom embedding/feature weights."""
    job_result = await session.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates_result = await session.execute(
        select(Candidate)
        .where(Candidate.organization_id == current_user.organization_id)
        .limit(limit)
    )
    candidates = candidates_result.scalars().all()

    ranked = []
    for candidate in candidates:
        score_data = await ranking_service.calculate_match_score(
            candidate, job, request.embedding_weight, request.feature_weight
        )
        ranked.append(
            {
                "candidate_id": str(candidate.id),
                "candidate_name": f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                "candidate_email": candidate.email,
                **score_data,
            }
        )

    ranked.sort(key=lambda x: x["match_score"], reverse=True)

    # Persist a ranking history snapshot
    snapshot = RankingHistory(
        job_id=job.id,
        organization_id=current_user.organization_id,
        triggered_by_id=current_user.id,
        embedding_weight=request.embedding_weight,
        feature_weight=request.feature_weight,
        candidate_count=len(ranked),
        top_score=ranked[0]["match_score"] if ranked else None,
        results=ranked[:50],
    )
    session.add(snapshot)
    await session.commit()

    return ranked


# Ranking history
@router.get("/history/{job_id}", response_model=list[RankingHistoryResponse])
async def get_ranking_history(
    job_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve ranking history snapshots for a job."""
    result = await session.execute(
        select(RankingHistory)
        .where(RankingHistory.job_id == job_id)
        .where(RankingHistory.organization_id == current_user.organization_id)
        .order_by(RankingHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "job_id": str(s.job_id),
            "embedding_weight": s.embedding_weight,
            "feature_weight": s.feature_weight,
            "candidate_count": s.candidate_count,
            "top_score": s.top_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "results": s.results,
        }
        for s in snapshots
    ]


# Comparison
@router.post("/compare", response_model=dict)
async def compare_candidates(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Compare multiple candidates side by side for a job."""
    try:
        candidate_ids = [uuid.UUID(cid) for cid in request.candidate_ids]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid candidate id format")

    if len(candidate_ids) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 candidates are required for comparison"
        )

    result = await ranking_service.compare_candidates(
        session,
        candidate_ids,
        uuid.UUID(request.job_id),
        current_user.organization_id,
    )
    return result


# Filtering
@router.get("/filter/{job_id}", response_model=list[CandidateRankingResponse])
async def filter_ranked_candidates(
    job_id: uuid.UUID,
    min_score: float | None = Query(None, ge=0, le=100),
    max_score: float | None = Query(None, ge=0, le=100),
    required_skills: list[str] | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Rank candidates for a job then filter by score band and required skills."""
    ranked = await ranking_service.filter_ranked_candidates(
        session,
        job_id,
        current_user.organization_id,
        min_score=min_score,
        max_score=max_score,
        required_skills=required_skills,
        limit=limit,
    )
    return ranked


# Export
@router.get("/export/{job_id}")
async def export_rankings(
    job_id: uuid.UUID,
    fmt: str = Query("csv", pattern="^(csv|json)$"),
    limit: int = Query(500, ge=1, le=2000),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Export ranked candidates for a job as CSV or JSON."""
    ranked = await ranking_service.rank_candidates_for_job(
        session, job_id, current_user.organization_id, limit=limit
    )
    payload = RankingService.export_rankings(ranked, fmt=fmt)

    if fmt == "json":
        return PlainTextResponse(payload, media_type="application/json")
    return PlainTextResponse(
        payload,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rankings_{job_id}.csv"},
    )


# Paginated ranking
@router.get("/candidates/paginated/{job_id}", response_model=PaginatedRankingResponse)
async def rank_candidates_paginated(
    job_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Rank candidates for a job with pagination metadata."""
    ranked = await ranking_service.rank_candidates_for_job(
        session, job_id, current_user.organization_id, limit=10000
    )
    total = len(ranked)
    page = ranked[skip : skip + limit]
    return {"items": page, "total": total, "skip": skip, "limit": limit}
