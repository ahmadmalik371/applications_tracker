from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class FeedbackRating(str, enum.Enum):
    GOOD = "good"
    BAD = "bad"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"


class AIRecommendationFeedback(BaseModel):
    __tablename__ = "ai_recommendation_feedback"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    candidate_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("candidates.id", ondelete="SET NULL"), index=True, nullable=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), index=True, nullable=True
    )
    ranking_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rating: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class ModelVersion(BaseModel):
    __tablename__ = "model_versions"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    trained_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class ModelEvaluation(BaseModel):
    __tablename__ = "model_evaluations"

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    map_at_k: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ndcg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class BiasReport(BaseModel):
    __tablename__ = "bias_reports"

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    model_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("model_versions.id", ondelete="SET NULL"), index=True, nullable=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    group_a: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    group_b: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
