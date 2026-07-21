from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class PlanTier(str, enum.Enum):
    FREE = "Free"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "Active"
    TRIALING = "Trialing"
    PAST_DUE = "Past Due"
    CANCELED = "Canceled"
    EXPIRED = "Expired"


class SaaSPlan(BaseModel):
    __tablename__ = "saas_plans"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    tier: Mapped[str] = mapped_column(
        String(50), default=PlanTier.FREE.value, nullable=False
    )
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    billing_cycle: Mapped[str] = mapped_column(
        String(20), default="monthly", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_resume_processing: Mapped[int] = mapped_column(
        Integer, default=50, nullable=False
    )
    max_ai_requests: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=500, nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="plan")


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("saas_plans.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=SubscriptionStatus.ACTIVE.value, nullable=False
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usage_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_resume_processing: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    usage_ai_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_storage_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped[SaaSPlan] = relationship(back_populates="subscriptions")


class FeatureFlag(BaseModel):
    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class OrgFeatureFlagOverride(BaseModel):
    __tablename__ = "org_feature_flag_overrides"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    feature_flag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("feature_flags.id", ondelete="CASCADE"), index=True, nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "organization_id", "feature_flag_id", name="uix_org_flag_override"
        ),
    )


class PlatformSetting(BaseModel):
    __tablename__ = "platform_settings"

    key: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SystemAnnouncement(BaseModel):
    __tablename__ = "system_announcements"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class GlobalRole(BaseModel):
    __tablename__ = "global_roles"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
