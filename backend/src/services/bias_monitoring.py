from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai import BiasReport


class BiasMonitoringService:
    """Service for computing fairness metrics and generating bias reports.

    Supported metrics:
        - Demographic parity: P(hired|group_a) vs P(hired|group_b)
        - Disparate impact ratio: min(p_a, p_b) / max(p_a, p_b)
        - Statistical parity difference: p_a - p_b

    A bias report is flagged when the metric value exceeds the configured threshold.
    """

    DEFAULT_THRESHOLD = 0.1

    async def compute_demographic_parity(
        self,
        session: AsyncSession,
        *,
        group_a: str,
        group_b: str,
        rate_a: float,
        rate_b: float,
        organization_id: uuid.UUID | None = None,
        model_version_id: uuid.UUID | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> BiasReport:
        diff = abs(rate_a - rate_b)
        is_flagged = diff > threshold
        report = BiasReport(
            organization_id=organization_id,
            model_version_id=model_version_id,
            metric_type="demographic_parity",
            metric_value=diff,
            group_a=group_a,
            group_b=group_b,
            threshold=threshold,
            is_flagged=is_flagged,
            details={"rate_a": rate_a, "rate_b": rate_b},
        )
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report

    async def compute_disparate_impact(
        self,
        session: AsyncSession,
        *,
        group_a: str,
        group_b: str,
        rate_a: float,
        rate_b: float,
        organization_id: uuid.UUID | None = None,
        model_version_id: uuid.UUID | None = None,
        threshold: float = 0.8,
    ) -> BiasReport:
        ratio = (
            min(rate_a, rate_b) / max(rate_a, rate_b)
            if max(rate_a, rate_b) > 0
            else 1.0
        )
        is_flagged = ratio < threshold
        report = BiasReport(
            organization_id=organization_id,
            model_version_id=model_version_id,
            metric_type="disparate_impact",
            metric_value=ratio,
            group_a=group_a,
            group_b=group_b,
            threshold=threshold,
            is_flagged=is_flagged,
            details={"rate_a": rate_a, "rate_b": rate_b, "ratio": ratio},
        )
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report

    async def list_reports(
        self,
        session: AsyncSession,
        *,
        organization_id: uuid.UUID | None = None,
        flagged_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[BiasReport], int]:
        stmt = select(BiasReport)
        count_stmt = select(func.count(BiasReport.id))
        if organization_id is not None:
            stmt = stmt.where(BiasReport.organization_id == organization_id)
            count_stmt = count_stmt.where(BiasReport.organization_id == organization_id)
        if flagged_only:
            stmt = stmt.where(BiasReport.is_flagged == True)
            count_stmt = count_stmt.where(BiasReport.is_flagged == True)
        total = (await session.execute(count_stmt)).scalar_one()
        rows = (
            (
                await session.execute(
                    stmt.order_by(BiasReport.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return rows, total


bias_monitoring_service = BiasMonitoringService()
