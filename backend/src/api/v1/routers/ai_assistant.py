import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User, Candidate, Job
from src.services.ai_assistant import ai_assistant_service

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


class InterviewQuestionRequest(BaseModel):
    job_id: uuid.UUID
    candidate_id: Optional[uuid.UUID] = None
    seniority: str = "mid"
    count: int = 10


@router.get("/search")
async def ai_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = await ai_assistant_service.search_candidates(db, q, user.organization_id, limit)
    return {"query": q, "results": results}


@router.get("/summarize/{candidate_id}")
async def summarize_resume(
    candidate_id: uuid.UUID,
    force: bool = Query(False, description="Force regeneration"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    candidate = await db.get(Candidate, candidate_id)
    if not candidate or candidate.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    summary = await ai_assistant_service.summarize_resume(candidate, force_regenerate=force)
    return {"candidate_id": str(candidate_id), "summary": summary}


@router.get("/analyze-jd/{job_id}")
async def analyze_jd(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(Job, job_id)
    if not job or job.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    analysis = await ai_assistant_service.analyze_job_description(job)
    return {"job_id": str(job_id), "analysis": analysis}


@router.post("/interview-questions")
async def interview_questions(
    req: InterviewQuestionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(Job, req.job_id)
    if not job or job.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = None
    if req.candidate_id:
        candidate = await db.get(Candidate, req.candidate_id)
        if not candidate or candidate.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Candidate not found")
    questions = await ai_assistant_service.generate_interview_questions(
        job, candidate, seniority=req.seniority, count=req.count
    )
    return {"questions": questions}


@router.get("/skill-gap/{candidate_id}/{job_id}")
async def skill_gap(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    candidate = await db.get(Candidate, candidate_id)
    if not candidate or candidate.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    job = await db.get(Job, job_id)
    if not job or job.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    analysis = await ai_assistant_service.analyze_skill_gap(candidate, job)
    return {"candidate_id": str(candidate_id), "job_id": str(job_id), "analysis": analysis}
