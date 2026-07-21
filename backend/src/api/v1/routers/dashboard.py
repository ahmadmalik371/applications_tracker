import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User, Candidate, Job, Application
from src.models.application import ApplicationStage
from src.models.job import JobStatus


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Aggregate metrics for the recruiter dashboard widgets."""
    org_id = current_user.organization_id

    # Active jobs
    active_jobs_result = await session.execute(
        select(func.count(Job.id))
        .where(Job.organization_id == org_id)
        .where(Job.status == JobStatus.OPEN.value)
    )
    active_jobs = active_jobs_result.scalar() or 0

    # Total jobs
    total_jobs_result = await session.execute(
        select(func.count(Job.id)).where(Job.organization_id == org_id)
    )
    total_jobs = total_jobs_result.scalar() or 0

    # Total candidates
    total_candidates_result = await session.execute(
        select(func.count(Candidate.id)).where(Candidate.organization_id == org_id)
    )
    total_candidates = total_candidates_result.scalar() or 0

    # New candidates (status = New)
    new_candidates_result = await session.execute(
        select(func.count(Candidate.id))
        .where(Candidate.organization_id == org_id)
        .where(Candidate.status == "New")
    )
    new_candidates = new_candidates_result.scalar() or 0

    # Total applications
    total_applications_result = await session.execute(
        select(func.count(Application.id)).where(Application.organization_id == org_id)
    )
    total_applications = total_applications_result.scalar() or 0

    # Applications by stage (pipeline)
    pipeline_result = await session.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.organization_id == org_id)
        .group_by(Application.status)
    )
    pipeline = {row[0]: row[1] for row in pipeline_result.all()}

    # Recent jobs (latest 5)
    recent_jobs_result = await session.execute(
        select(Job)
        .where(Job.organization_id == org_id)
        .order_by(desc(Job.created_at))
        .limit(5)
    )
    recent_jobs = [
        {
            "id": str(j.id),
            "title": j.title,
            "status": j.status,
            "location": j.location,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in recent_jobs_result.scalars().all()
    ]

    # Recent candidates (latest 5)
    recent_candidates_result = await session.execute(
        select(Candidate)
        .where(Candidate.organization_id == org_id)
        .order_by(desc(Candidate.created_at))
        .limit(5)
    )
    recent_candidates = [
        {
            "id": str(c.id),
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in recent_candidates_result.scalars().all()
    ]

    return {
        "active_jobs": active_jobs,
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "new_candidates": new_candidates,
        "total_applications": total_applications,
        "pipeline": pipeline,
        "recent_jobs": recent_jobs,
        "recent_candidates": recent_candidates,
    }
