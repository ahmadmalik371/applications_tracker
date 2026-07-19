import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.model_version import model_version_service
from src.services.bias_monitoring import bias_monitoring_service
from src.services.feedback import feedback_service


@pytest.mark.asyncio
async def test_model_version_create_and_deploy(session: AsyncSession):
    mv = await model_version_service.create_version(
        session, name="ranking_model", version="1.0.0",
        metrics={"precision": 0.85},
    )
    assert mv.is_active is False

    deployed = await model_version_service.deploy(session, mv.id)
    assert deployed.is_active is True


@pytest.mark.asyncio
async def test_model_rollback(session: AsyncSession):
    v1 = await model_version_service.create_version(
        session, name="ranking_model", version="1.0.0"
    )
    v2 = await model_version_service.create_version(
        session, name="ranking_model", version="2.0.0"
    )
    await model_version_service.deploy(session, v1.id)
    assert v1.is_active is True

    await model_version_service.deploy(session, v2.id)
    assert v2.is_active is True

    rollback = await model_version_service.rollback(session, v1.id)
    assert rollback.id == v1.id
    assert rollback.is_active is True


@pytest.mark.asyncio
async def test_add_evaluation(session: AsyncSession):
    mv = await model_version_service.create_version(
        session, name="test_model", version="1.0"
    )
    ev = await model_version_service.add_evaluation(
        session, model_version_id=mv.id,
        precision=0.9, recall=0.8, f1=0.85, roc_auc=0.92,
        map_at_k=0.78, ndcg=0.81, latency_ms=45.0,
    )
    assert ev.precision == 0.9
    assert ev.f1 == 0.85


@pytest.mark.asyncio
async def test_bias_report_demographic_parity(session: AsyncSession):
    report = await bias_monitoring_service.compute_demographic_parity(
        session, group_a="male", group_b="female",
        rate_a=0.6, rate_b=0.3, threshold=0.1,
    )
    assert report.metric_value == 0.3
    assert report.is_flagged is True


@pytest.mark.asyncio
async def test_bias_report_disparate_impact(session: AsyncSession):
    report = await bias_monitoring_service.compute_disparate_impact(
        session, group_a="group_a", group_b="group_b",
        rate_a=0.5, rate_b=0.8, threshold=0.8,
    )
    assert report.metric_value == 0.625
    assert report.is_flagged is True


@pytest.mark.asyncio
async def test_feedback_recording(session: AsyncSession):
    org_id = uuid.uuid4()
    recruiter_id = uuid.uuid4()
    fb = await feedback_service.record_feedback(
        session, organization_id=org_id, recruiter_id=recruiter_id,
        rating="good", note="Great match",
    )
    assert fb.rating == "good"

    rows, total = await feedback_service.get_feedback(
        session, organization_id=org_id
    )
    assert total == 1
    assert rows[0].note == "Great match"

    summary = await feedback_service.feedback_summary(session, org_id)
    assert summary.get("good") == 1
