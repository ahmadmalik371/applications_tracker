from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit import AuditLog


class AuditService:
    """Service for recording and querying audit log events."""

    async def log(
        self,
        session: AsyncSession,
        *,
        action: str,
        resource_type: str,
        user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=metadata,
            occurred_at=datetime.now(timezone.utc),
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry

    async def search(
        self,
        session: AsyncSession,
        *,
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[AuditLog], int]:
        stmt = select(AuditLog)
        count_stmt = select(func.count(AuditLog.id))

        if organization_id is not None:
            stmt = stmt.where(AuditLog.organization_id == organization_id)
            count_stmt = count_stmt.where(AuditLog.organization_id == organization_id)
        if user_id is not None:
            stmt = stmt.where(AuditLog.user_id == user_id)
            count_stmt = count_stmt.where(AuditLog.user_id == user_id)
        if action is not None:
            stmt = stmt.where(AuditLog.action == action)
            count_stmt = count_stmt.where(AuditLog.action == action)
        if resource_type is not None:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
            count_stmt = count_stmt.where(AuditLog.resource_type == resource_type)
        if start is not None:
            stmt = stmt.where(AuditLog.occurred_at >= start)
            count_stmt = count_stmt.where(AuditLog.occurred_at >= start)
        if end is not None:
            stmt = stmt.where(AuditLog.occurred_at <= end)
            count_stmt = count_stmt.where(AuditLog.occurred_at <= end)

        total = (await session.execute(count_stmt)).scalar_one()
        rows = (
            await session.execute(
                stmt.order_by(AuditLog.occurred_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return rows, total


audit_service = AuditService()
