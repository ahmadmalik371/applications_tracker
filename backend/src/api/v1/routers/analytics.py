import uuid
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User, Candidate, Job, Application
from src.models.application import ApplicationStage
from src.models.job import JobStatus


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/funnel")
async def hiring_funnel(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Funnel metrics: application counts by stage."""
    org_id = current_user.organization_id
    result = await session.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.organization_id == org_id)
        .group_by(Application.status)
    )
    stages = {row[0]: row[1] for row in result.all()}

    total = sum(stages.values()) or 1
    return {
        "stages": stages,
        "total": sum(stages.values()),
        "conversion_rates": {
            stage: round(count / total * 100, 1) for stage, count in stages.items()
        },
    }


@router.get("/time-to-hire")
async def time_to_hire(
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Average time from application to hired, in days."""
    org_id = current_user.organization_id
    since = datetime.utcnow() - timedelta(days=days)

    result = await session.execute(
        select(
            Application.created_at,
            Application.updated_at,
        )
        .where(Application.organization_id == org_id)
        .where(Application.status == ApplicationStage.HIRED.value)
        .where(Application.updated_at >= since)
    )
    rows = result.all()

    times = []
    for created, updated in rows:
        if created and updated:
            delta = (updated - created).days
            times.append(delta)

    avg = sum(times) / len(times) if times else 0
    return {
        "average_days": round(avg, 1),
        "count": len(times),
        "min_days": min(times) if times else 0,
        "max_days": max(times) if times else 0,
        "period_days": days,
    }


@router.get("/source-tracking")
async def source_tracking(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Candidate counts by source (parsed from metadata)."""
    org_id = current_user.organization_id
    result = await session.execute(
        select(Candidate.parsed_data).where(Candidate.organization_id == org_id)
    )
    sources: Dict[str, int] = {}
    for (parsed,) in result.all():
        if parsed and isinstance(parsed, dict):
            source = parsed.get("source", "unknown")
        else:
            source = "unknown"
        sources[source] = sources.get(source, 0) + 1

    return {"sources": sources, "total": sum(sources.values())}


@router.get("/ai-accuracy")
async def ai_accuracy(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Compare AI scores with actual outcomes (hired vs rejected)."""
    org_id = current_user.organization_id
    result = await session.execute(
        select(Application.score, Application.status)
        .where(Application.organization_id == org_id)
        .where(Application.score.isnot(None))
    )
    rows = result.all()

    if not rows:
        return {"avg_score_hired": 0, "avg_score_rejected": 0, "count": 0}

    hired_scores = [r[0] for r in rows if r[1] == ApplicationStage.HIRED.value]
    rejected_scores = [r[0] for r in rows if r[1] == ApplicationStage.REJECTED.value]

    avg_hired = sum(hired_scores) / len(hired_scores) if hired_scores else 0
    avg_rejected = sum(rejected_scores) / len(rejected_scores) if rejected_scores else 0

    return {
        "avg_score_hired": round(avg_hired, 1),
        "avg_score_rejected": round(avg_rejected, 1),
        "hired_count": len(hired_scores),
        "rejected_count": len(rejected_scores),
        "count": len(rows),
    }
