import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.feedback import feedback_service
from src.services.model_version import model_version_service
from src.services.bias_monitoring import bias_monitoring_service

router = APIRouter(prefix="/ml", tags=["ML Management"])


# --- Feedback ---
class FeedbackIn(BaseModel):
    rating: str
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    ranking_score: Optional[float] = None
    note: Optional[str] = None


@router.post("/feedback")
async def record_feedback(
    req: FeedbackIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fb = await feedback_service.record_feedback(
        db,
        organization_id=user.organization_id,
        recruiter_id=user.id,
        rating=req.rating,
        candidate_id=uuid.UUID(req.candidate_id) if req.candidate_id else None,
        job_id=uuid.UUID(req.job_id) if req.job_id else None,
        ranking_score=req.ranking_score,
        note=req.note,
    )
    return {"id": str(fb.id), "rating": fb.rating}


@router.get("/feedback")
async def list_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await feedback_service.get_feedback(
        db, organization_id=user.organization_id, skip=skip, limit=limit
    )
    return {
        "total": total,
        "items": [
            {
                "id": str(r.id), "rating": r.rating, "note": r.note,
                "candidate_id": str(r.candidate_id) if r.candidate_id else None,
                "job_id": str(r.job_id) if r.job_id else None,
                "ranking_score": r.ranking_score,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/feedback/summary")
async def feedback_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await feedback_service.feedback_summary(db, user.organization_id)


# --- Model Versions ---
class ModelVersionIn(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    metrics: Optional[dict] = None
    config: Optional[dict] = None


class EvaluationIn(BaseModel):
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    map_at_k: Optional[float] = None
    ndcg: Optional[float] = None
    latency_ms: Optional[float] = None


@router.get("/models")
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await model_version_service.list_versions(db, skip, limit)
    return {
        "total": total,
        "items": [
            {
                "id": str(m.id), "name": m.name, "version": m.version,
                "is_active": m.is_active,
                "deployed_at": m.deployed_at.isoformat() if m.deployed_at else None,
                "metrics": m.metrics,
            }
            for m in rows
        ],
    }


@router.post("/models", status_code=status.HTTP_201_CREATED)
async def create_model(
    req: ModelVersionIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mv = await model_version_service.create_version(
        db, name=req.name, version=req.version,
        description=req.description, metrics=req.metrics, config=req.config,
    )
    return {"id": str(mv.id), "name": mv.name, "version": mv.version}


@router.post("/models/{model_id}/deploy")
async def deploy_model(
    model_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mv = await model_version_service.deploy(db, model_id)
    if not mv:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"id": str(mv.id), "is_active": mv.is_active}


@router.post("/models/{model_id}/rollback")
async def rollback_model(
    model_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mv = await model_version_service.rollback(db, model_id)
    if not mv:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"id": str(mv.id), "is_active": mv.is_active}


@router.post("/models/{model_id}/evaluations")
async def add_evaluation(
    model_id: uuid.UUID,
    req: EvaluationIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ev = await model_version_service.add_evaluation(
        db, model_version_id=model_id,
        precision=req.precision, recall=req.recall, f1=req.f1,
        roc_auc=req.roc_auc, map_at_k=req.map_at_k, ndcg=req.ndcg,
        latency_ms=req.latency_ms,
    )
    return {"id": str(ev.id), "model_version_id": str(ev.model_version_id)}


@router.get("/models/{model_id}/evaluations")
async def list_evaluations(
    model_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await model_version_service.list_evaluations(db, model_id)
    return {
        "items": [
            {
                "id": str(e.id), "precision": e.precision, "recall": e.recall,
                "f1": e.f1, "roc_auc": e.roc_auc, "map_at_k": e.map_at_k,
                "ndcg": e.ndcg, "latency_ms": e.latency_ms,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in rows
        ]
    }


# --- Bias Monitoring ---
class BiasReportIn(BaseModel):
    metric_type: str
    group_a: str
    group_b: str
    rate_a: float
    rate_b: float
    threshold: Optional[float] = None


@router.post("/bias-reports")
async def create_bias_report(
    req: BiasReportIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.metric_type == "demographic_parity":
        report = await bias_monitoring_service.compute_demographic_parity(
            db, group_a=req.group_a, group_b=req.group_b,
            rate_a=req.rate_a, rate_b=req.rate_b,
            organization_id=user.organization_id,
            threshold=req.threshold or bias_monitoring_service.DEFAULT_THRESHOLD,
        )
    elif req.metric_type == "disparate_impact":
        report = await bias_monitoring_service.compute_disparate_impact(
            db, group_a=req.group_a, group_b=req.group_b,
            rate_a=req.rate_a, rate_b=req.rate_b,
            organization_id=user.organization_id,
            threshold=req.threshold or 0.8,
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown metric type")
    return {
        "id": str(report.id), "metric_type": report.metric_type,
        "metric_value": report.metric_value, "is_flagged": report.is_flagged,
    }


@router.get("/bias-reports")
async def list_bias_reports(
    flagged_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await bias_monitoring_service.list_reports(
        db, organization_id=user.organization_id,
        flagged_only=flagged_only, skip=skip, limit=limit,
    )
    return {
        "total": total,
        "items": [
            {
                "id": str(r.id), "metric_type": r.metric_type,
                "metric_value": r.metric_value, "group_a": r.group_a,
                "group_b": r.group_b, "is_flagged": r.is_flagged,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }
