from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai import ModelEvaluation, ModelVersion


class ModelVersionService:
    """Service for tracking ML model versions, deployments, and rollbacks."""

    async def create_version(
        self,
        session: AsyncSession,
        *,
        name: str,
        version: str,
        description: str | None = None,
        trained_at: datetime | None = None,
        metrics: dict | None = None,
        config: dict | None = None,
    ) -> ModelVersion:
        mv = ModelVersion(
            name=name,
            version=version,
            description=description,
            trained_at=trained_at,
            metrics=metrics,
            config=config,
        )
        session.add(mv)
        await session.commit()
        await session.refresh(mv)
        return mv

    async def list_versions(
        self, session: AsyncSession, skip: int = 0, limit: int = 50
    ) -> tuple[Sequence[ModelVersion], int]:
        total = (
            await session.execute(select(func.count(ModelVersion.id)))
        ).scalar_one()
        rows = (
            (
                await session.execute(
                    select(ModelVersion)
                    .order_by(ModelVersion.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return rows, total

    async def get_active(self, session: AsyncSession) -> ModelVersion | None:
        result = await session.execute(
            select(ModelVersion).where(ModelVersion.is_active == True).limit(1)
        )
        return result.scalar_one_or_none()

    async def deploy(
        self, session: AsyncSession, version_id: uuid.UUID
    ) -> ModelVersion | None:
        mv = await session.get(ModelVersion, version_id)
        if not mv:
            return None
        await session.execute(update(ModelVersion).values(is_active=False))
        mv.is_active = True
        mv.deployed_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(mv)
        return mv

    async def rollback(
        self, session: AsyncSession, version_id: uuid.UUID
    ) -> ModelVersion | None:
        """Rollback to a previous model version by activating it."""
        return await self.deploy(session, version_id)

    async def add_evaluation(
        self,
        session: AsyncSession,
        *,
        model_version_id: uuid.UUID,
        precision: float | None = None,
        recall: float | None = None,
        f1: float | None = None,
        roc_auc: float | None = None,
        map_at_k: float | None = None,
        ndcg: float | None = None,
        latency_ms: float | None = None,
        notes: dict | None = None,
    ) -> ModelEvaluation:
        ev = ModelEvaluation(
            model_version_id=model_version_id,
            precision=precision,
            recall=recall,
            f1=f1,
            roc_auc=roc_auc,
            map_at_k=map_at_k,
            ndcg=ndcg,
            latency_ms=latency_ms,
            notes=notes,
        )
        session.add(ev)
        await session.commit()
        await session.refresh(ev)
        return ev

    async def list_evaluations(
        self, session: AsyncSession, model_version_id: uuid.UUID
    ) -> Sequence[ModelEvaluation]:
        result = await session.execute(
            select(ModelEvaluation)
            .where(ModelEvaluation.model_version_id == model_version_id)
            .order_by(ModelEvaluation.created_at.desc())
        )
        return result.scalars().all()


model_version_service = ModelVersionService()
