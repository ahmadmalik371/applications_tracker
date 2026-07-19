import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.admin import SaaSPlan, FeatureFlag, Subscription
from src.services.subscription import subscription_service
from src.services.feature_flags import feature_flag_service


@pytest.mark.asyncio
async def test_saas_plan_creation(session: AsyncSession):
    plan = SaaSPlan(
        id=uuid.uuid4(),
        name="Test Plan",
        tier="Professional",
        price_cents=4900,
        max_users=50,
        max_resume_processing=500,
        max_ai_requests=5000,
        max_storage_mb=5000,
    )
    session.add(plan)
    await session.commit()
    assert plan.id is not None
    assert plan.tier == "Professional"


@pytest.mark.asyncio
async def test_feature_flag_default_enabled(session: AsyncSession):
    flag = FeatureFlag(
        id=uuid.uuid4(),
        key="test_flag",
        name="Test Flag",
        module="ai",
        is_enabled=True,
    )
    session.add(flag)
    await session.commit()

    result = await feature_flag_service.is_enabled(session, "test_flag")
    assert result is True


@pytest.mark.asyncio
async def test_feature_flag_unknown_key_defaults_true(session: AsyncSession):
    result = await feature_flag_service.is_enabled(session, "nonexistent_flag")
    assert result is True


@pytest.mark.asyncio
async def test_feature_flag_org_override(session: AsyncSession):
    org_id = uuid.uuid4()
    flag = FeatureFlag(
        id=uuid.uuid4(),
        key="override_test",
        name="Override Test",
        module="ai",
        is_enabled=True,
    )
    session.add(flag)
    await session.commit()

    await feature_flag_service.set_override(session, org_id, "override_test", False)
    result = await feature_flag_service.is_enabled(session, "override_test", org_id)
    assert result is False

    result_no_org = await feature_flag_service.is_enabled(session, "override_test")
    assert result_no_org is True


@pytest.mark.asyncio
async def test_subscription_quota_check(session: AsyncSession):
    org_id = uuid.uuid4()
    plan = SaaSPlan(
        id=uuid.uuid4(),
        name="Quota Plan",
        max_users=10,
        max_ai_requests=100,
    )
    session.add(plan)
    await session.commit()

    sub = Subscription(
        id=uuid.uuid4(),
        organization_id=org_id,
        plan_id=plan.id,
        status="Active",
        usage_ai_requests=99,
    )
    session.add(sub)
    await session.commit()

    has_quota = await subscription_service.check_quota(session, org_id, "ai_requests")
    assert has_quota is True

    sub.usage_ai_requests = 100
    await session.commit()
    has_quota = await subscription_service.check_quota(session, org_id, "ai_requests")
    assert has_quota is False
