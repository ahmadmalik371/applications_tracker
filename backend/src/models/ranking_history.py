from __future__ import annotations

import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class RankingHistory(BaseModel):
    """Snapshot of a ranking run for a job, stored for history/re-rank tracking."""

    __tablename__ = "ranking_history"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    triggered_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    embedding_weight: Mapped[Float] = mapped_column(Float, default=0.3, nullable=False)
    feature_weight: Mapped[Float] = mapped_column(Float, default=0.7, nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    results: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)

    job: Mapped[Optional["Job"]] = relationship("Job")
