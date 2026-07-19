from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.admin import SaaSPlan, Subscription, SubscriptionStatus


class SubscriptionService:
    """Service for managing organization subscriptions and quota checks.

    Designed to be Stripe-ready: Stripe IDs are stored on the subscription record
    but no payment gateway integration is wired up yet.
    """

    async def get_plan(self, session: AsyncSession, plan_name: str) -> Optional[SaaSPlan]:
        result = await session.execute(select(SaaSPlan).where(SaaSPlan.name == plan_name))
        return result.scalar_one_or_none()

    async def list_plans(self, session: AsyncSession) -> list[SaaSPlan]:
        result = await session.execute(
            select(SaaSPlan).where(SaaSPlan.is_active == True).order_by(SaaSPlan.price_cents)
        )
        return list(result.scalars().all())

    async def get_subscription(
        self, session: AsyncSession, organization_id: uuid.UUID
    ) -> Optional[Subscription]:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_subscription(
        self,
        session: AsyncSession,
        *,
        organization_id: uuid.UUID,
        plan_id: uuid.UUID,
        status: str = SubscriptionStatus.ACTIVE.value,
        stripe_subscription_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None,
    ) -> Subscription:
        sub = Subscription(
            organization_id=organization_id,
            plan_id=plan_id,
            status=status,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
        )
        session.add(sub)
        await session.commit()
        await session.refresh(sub)
        return sub

    async def check_quota(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        resource: str,
    ) -> bool:
        """Check if org has remaining quota for the given resource.

        resource is one of: 'users', 'resume_processing', 'ai_requests', 'storage_mb'.
        """
        sub = await self.get_subscription(session, organization_id)
        if not sub:
            return True

        plan = await session.get(SaaSPlan, sub.plan_id)
        if not plan:
            return True

        limits = {
            "users": (plan.max_users, sub.usage_users),
            "resume_processing": (plan.max_resume_processing, sub.usage_resume_processing),
            "ai_requests": (plan.max_ai_requests, sub.usage_ai_requests),
            "storage_mb": (plan.max_storage_mb, sub.usage_storage_mb),
        }
        if resource not in limits:
            return True
        limit, used = limits[resource]
        return used < limit

    async def increment_usage(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        resource: str,
        amount: int = 1,
    ) -> Optional[Subscription]:
        sub = await self.get_subscription(session, organization_id)
        if not sub:
            return None
        attr_map = {
            "users": "usage_users",
            "resume_processing": "usage_resume_processing",
            "ai_requests": "usage_ai_requests",
            "storage_mb": "usage_storage_mb",
        }
        attr = attr_map.get(resource)
        if not attr:
            return sub
        current = getattr(sub, attr) or 0
        setattr(sub, attr, current + amount)
        await session.commit()
        await session.refresh(sub)
        return sub


subscription_service = SubscriptionService()
