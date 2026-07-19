import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from src.models.audit import AuditLog
from src.services.audit import audit_service


@pytest.mark.asyncio
async def test_audit_log_creation(session: AsyncSession):
    entry = await audit_service.log(
        session,
        action="login",
        resource_type="auth",
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        ip_address="192.168.1.1",
        metadata={"method": "password"},
    )
    assert entry.id is not None
    assert entry.action == "login"
    assert entry.ip_address == "192.168.1.1"


@pytest.mark.asyncio
async def test_audit_log_search_by_action(session: AsyncSession):
    org_id = uuid.uuid4()
    for action in ["login", "job_create", "login"]:
        await audit_service.log(
            session, action=action, resource_type="test",
            organization_id=org_id,
        )

    rows, total = await audit_service.search(
        session, organization_id=org_id, action="login"
    )
    assert total == 2
    assert all(r.action == "login" for r in rows)


@pytest.mark.asyncio
async def test_audit_log_search_by_date_range(session: AsyncSession):
    org_id = uuid.uuid4()
    await audit_service.log(
        session, action="test", resource_type="test", organization_id=org_id,
    )

    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2030, 1, 1, tzinfo=timezone.utc)
    rows, total = await audit_service.search(
        session, organization_id=org_id, start=start, end=end
    )
    assert total >= 1

    future_start = datetime(2031, 1, 1, tzinfo=timezone.utc)
    rows, total = await audit_service.search(
        session, organization_id=org_id, start=future_start
    )
    assert total == 0
