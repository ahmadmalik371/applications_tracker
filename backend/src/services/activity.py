from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.activity import ActivityTimeline


class ActivityService:
    """Service for recording and querying activity timeline events."""

    async def record(
        self,
        session: AsyncSession,
        *,
        entity_type: str,
        entity_id: uuid.UUID,
        action: str,
        organization_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        summary: str | None = None,
        details: dict | None = None,
    ) -> ActivityTimeline:
        entry = ActivityTimeline(
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            actor_id=actor_id,
            action=action,
            summary=summary,
            details=details,
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry

    async def get_timeline(
        self,
        session: AsyncSession,
        *,
        entity_type: str,
        entity_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[ActivityTimeline], int]:
        stmt = select(ActivityTimeline).where(
            ActivityTimeline.entity_type == entity_type,
            ActivityTimeline.entity_id == entity_id,
        )
        count_stmt = select(func.count(ActivityTimeline.id)).where(
            ActivityTimeline.entity_type == entity_type,
            ActivityTimeline.entity_id == entity_id,
        )
        if organization_id is not None:
            stmt = stmt.where(ActivityTimeline.organization_id == organization_id)
            count_stmt = count_stmt.where(
                ActivityTimeline.organization_id == organization_id
            )

        total = (await session.execute(count_stmt)).scalar_one()
        rows = (
            (
                await session.execute(
                    stmt.order_by(ActivityTimeline.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return rows, total


activity_service = ActivityService()
