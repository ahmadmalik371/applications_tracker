import csv
import io
import json
import uuid
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User, Candidate, Job, Application
from src.services.ranking import RankingService


router = APIRouter(prefix="/reports", tags=["reports"])
ranking_service = RankingService()


@router.get("/candidates/export")
async def export_candidates(
    fmt: str = Query("csv", pattern="^(csv|json)$"),
    limit: int = Query(500, ge=1, le=5000),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Export candidate data as CSV or JSON."""
    result = await session.execute(
        select(Candidate)
        .where(Candidate.organization_id == current_user.organization_id)
        .order_by(desc(Candidate.created_at))
        .limit(limit)
    )
    candidates = result.scalars().all()

    rows = [
        {
            "id": str(c.id),
            "first_name": c.first_name or "",
            "last_name": c.last_name or "",
            "email": c.email,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else "",
        }
        for c in candidates
    ]

    if fmt == "json":
        return PlainTextResponse(json.dumps(rows, indent=2, default=str), media_type="application/json")

    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return PlainTextResponse(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates.csv"},
    )


@router.get("/jobs/{job_id}/rankings/export")
async def export_job_rankings(
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


@router.get("/applications/export")
async def export_applications(
    fmt: str = Query("csv", pattern="^(csv|json)$"),
    limit: int = Query(1000, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Export application data as CSV or JSON."""
    result = await session.execute(
        select(Application)
        .where(Application.organization_id == current_user.organization_id)
        .order_by(desc(Application.created_at))
        .limit(limit)
    )
    apps = result.scalars().all()

    rows = [
        {
            "id": str(a.id),
            "job_id": str(a.job_id),
            "candidate_id": str(a.candidate_id),
            "status": a.status,
            "score": a.score if a.score is not None else "",
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }
        for a in apps
    ]

    if fmt == "json":
        return PlainTextResponse(json.dumps(rows, indent=2, default=str), media_type="application/json")

    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return PlainTextResponse(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )
