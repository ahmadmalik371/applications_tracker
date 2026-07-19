import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.audit import audit_service
from src.services.activity import activity_service

router = APIRouter(prefix="/audit", tags=["Audit & Activity"])


class AuditLogOut(BaseModel):
    id: str
    user_id: Optional[str]
    organization_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    occurred_at: str
    metadata: Optional[dict]


@router.get("/logs")
async def search_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await audit_service.search(
        db, organization_id=user.organization_id,
        action=action, resource_type=resource_type,
        start=start, end=end, skip=skip, limit=limit,
    )
    return {
        "total": total,
        "items": [
            {
                "id": str(r.id),
                "user_id": str(r.user_id) if r.user_id else None,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "ip_address": r.ip_address,
                "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
                "metadata": r.event_metadata,
            }
            for r in rows
        ],
    }


@router.get("/timeline/{entity_type}/{entity_id}")
async def get_activity_timeline(
    entity_type: str,
    entity_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await activity_service.get_timeline(
        db, entity_type=entity_type, entity_id=entity_id,
        organization_id=user.organization_id, skip=skip, limit=limit,
    )
    return {
        "total": total,
        "items": [
            {
                "id": str(r.id),
                "entity_type": r.entity_type,
                "entity_id": str(r.entity_id),
                "action": r.action,
                "summary": r.summary,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }
