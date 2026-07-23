from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.admin import FeatureFlag, OrgFeatureFlagOverride


class FeatureFlagService:
    """Service for checking and managing feature flags with org-level overrides."""

    async def is_enabled(
        self,
        session: AsyncSession,
        key: str,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        flag = await self._get_flag(session, key)
        if not flag:
            return True

        if organization_id is not None:
            override = await self._get_override(session, organization_id, flag.id)
            if override is not None:
                return override.is_enabled

        return flag.is_enabled

    async def get_flag(self, session: AsyncSession, key: str) -> FeatureFlag | None:
        return await self._get_flag(session, key)

    async def list_flags(self, session: AsyncSession) -> list[FeatureFlag]:
        result = await session.execute(
            select(FeatureFlag).order_by(FeatureFlag.module, FeatureFlag.name)
        )
        return list(result.scalars().all())

    async def set_flag(
        self, session: AsyncSession, key: str, is_enabled: bool
    ) -> FeatureFlag | None:
        flag = await self._get_flag(session, key)
        if not flag:
            return None
        flag.is_enabled = is_enabled
        await session.commit()
        await session.refresh(flag)
        return flag

    async def set_override(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        flag_key: str,
        is_enabled: bool,
    ) -> OrgFeatureFlagOverride | None:
        flag = await self._get_flag(session, flag_key)
        if not flag:
            return None
        override = await self._get_override(session, organization_id, flag.id)
        if override is None:
            override = OrgFeatureFlagOverride(
                organization_id=organization_id,
                feature_flag_id=flag.id,
                is_enabled=is_enabled,
            )
            session.add(override)
        else:
            override.is_enabled = is_enabled
        await session.commit()
        await session.refresh(override)
        return override

    async def _get_flag(self, session: AsyncSession, key: str) -> FeatureFlag | None:
        result = await session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        return result.scalar_one_or_none()

    async def _get_override(
        self, session: AsyncSession, organization_id: uuid.UUID, flag_id: uuid.UUID
    ) -> OrgFeatureFlagOverride | None:
        result = await session.execute(
            select(OrgFeatureFlagOverride).where(
                OrgFeatureFlagOverride.organization_id == organization_id,
                OrgFeatureFlagOverride.feature_flag_id == flag_id,
            )
        )
        return result.scalar_one_or_none()


feature_flag_service = FeatureFlagService()
