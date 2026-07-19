import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, require_role, get_db
from src.models import (
    User, Organization, Job, Candidate, SaaSPlan, Subscription,
    FeatureFlag, PlatformSetting, SystemAnnouncement, GlobalRole,
)
from src.services.feature_flags import feature_flag_service
from src.services.subscription import subscription_service

router = APIRouter(prefix="/admin", tags=["Super Admin"])


# --- Schemas ---
class SaaSPlanOut(BaseModel):
    id: str
    name: str
    tier: str
    price_cents: int
    max_users: int
    max_resume_processing: int
    max_ai_requests: int
    max_storage_mb: int
    is_active: bool

    class Config:
        from_attributes = True


class FeatureFlagOut(BaseModel):
    id: str
    key: str
    name: str
    module: str
    is_enabled: bool

    class Config:
        from_attributes = True


class FeatureFlagUpdate(BaseModel):
    is_enabled: bool


class OrgFeatureFlagOverrideIn(BaseModel):
    flag_key: str
    is_enabled: bool


class PlatformSettingIn(BaseModel):
    key: str
    value: dict
    description: Optional[str] = None
    is_public: bool = False


class SystemAnnouncementIn(BaseModel):
    title: str
    body: str
    severity: str = "info"
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class DashboardStatsOut(BaseModel):
    organizations: int
    users: int
    jobs: int
    candidates: int
    active_subscriptions: int


# --- Endpoints ---
@router.get("/stats", response_model=DashboardStatsOut)
async def admin_stats(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    orgs = (await db.execute(select(func.count(Organization.id)))).scalar_one()
    users = (await db.execute(select(func.count(User.id)))).scalar_one()
    jobs = (await db.execute(select(func.count(Job.id)))).scalar_one()
    candidates = (await db.execute(select(func.count(Candidate.id)))).scalar_one()
    subs = (await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "Active")
    )).scalar_one()
    return DashboardStatsOut(
        organizations=orgs, users=users, jobs=jobs, candidates=candidates,
        active_subscriptions=subs,
    )


@router.get("/plans", response_model=List[SaaSPlanOut])
async def list_plans(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    plans = await subscription_service.list_plans(db)
    return [
        SaaSPlanOut(
            id=str(p.id), name=p.name, tier=p.tier, price_cents=p.price_cents,
            max_users=p.max_users, max_resume_processing=p.max_resume_processing,
            max_ai_requests=p.max_ai_requests, max_storage_mb=p.max_storage_mb,
            is_active=p.is_active,
        ) for p in plans
    ]


@router.get("/feature-flags", response_model=List[FeatureFlagOut])
async def list_feature_flags(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    flags = await feature_flag_service.list_flags(db)
    return [
        FeatureFlagOut(
            id=str(f.id), key=f.key, name=f.name, module=f.module, is_enabled=f.is_enabled
        ) for f in flags
    ]


@router.put("/feature-flags/{key}", response_model=FeatureFlagOut)
async def update_feature_flag(
    key: str,
    update: FeatureFlagUpdate,
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    flag = await feature_flag_service.set_flag(db, key, update.is_enabled)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return FeatureFlagOut(
        id=str(flag.id), key=flag.key, name=flag.name, module=flag.module,
        is_enabled=flag.is_enabled,
    )


@router.post("/orgs/{org_id}/feature-flags", response_model=dict)
async def set_org_flag_override(
    org_id: uuid.UUID,
    override: OrgFeatureFlagOverrideIn,
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await feature_flag_service.set_override(
        db, org_id, override.flag_key, override.is_enabled
    )
    if not result:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {"ok": True}


@router.get("/platform-settings", response_model=List[dict])
async def list_platform_settings(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PlatformSetting))
    return [
        {"id": str(s.id), "key": s.key, "value": s.value, "is_public": s.is_public}
        for s in result.scalars().all()
    ]


@router.post("/platform-settings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_platform_setting(
    setting: PlatformSettingIn,
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    ps = PlatformSetting(
        key=setting.key, value=setting.value,
        description=setting.description, is_public=setting.is_public,
    )
    db.add(ps)
    await db.commit()
    return {"id": str(ps.id), "key": ps.key}


@router.get("/announcements", response_model=List[dict])
async def list_announcements(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SystemAnnouncement))
    return [
        {
            "id": str(a.id), "title": a.title, "body": a.body,
            "severity": a.severity, "is_active": a.is_active,
        }
        for a in result.scalars().all()
    ]


@router.post("/announcements", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    ann: SystemAnnouncementIn,
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    a = SystemAnnouncement(
        title=ann.title, body=ann.body, severity=ann.severity,
        is_active=ann.is_active, starts_at=ann.starts_at, ends_at=ann.ends_at,
    )
    db.add(a)
    await db.commit()
    return {"id": str(a.id)}


@router.get("/global-roles", response_model=List[dict])
async def list_global_roles(
    user: User = Depends(require_role("Super Admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GlobalRole))
    return [
        {"id": str(r.id), "name": r.name, "description": r.description,
         "is_system": r.is_system}
        for r in result.scalars().all()
    ]
