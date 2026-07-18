import pytest
import uuid
from src.services.workflow import WorkflowService
from src.models import Application


@pytest.fixture
def workflow_service():
    return WorkflowService()


@pytest.mark.asyncio
async def test_create_and_list_stages(workflow_service, session):
    """Creating a stage then listing returns it."""
    org_id = uuid.uuid4()
    await workflow_service.create_stage(session, org_id, "Applied", order=0)
    await workflow_service.create_stage(session, org_id, "Phone Screen", order=1)
    await session.commit()

    stages = await workflow_service.get_stages(session, org_id)
    assert len(stages) == 2
    assert stages[0].name == "Applied"
    assert stages[1].name == "Phone Screen"


@pytest.mark.asyncio
async def test_transition_application_records_history(workflow_service, session):
    """Transitioning an application creates a history entry."""
    org_id = uuid.uuid4()
    job_id = uuid.uuid4()
    candidate_id = uuid.uuid4()

    app = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        status="Applied",
        organization_id=org_id,
    )
    session.add(app)
    await session.flush()

    result = await workflow_service.transition_application(
        session, app.id, "Screening", changed_by_id=uuid.uuid4(), note="Moved to screening"
    )
    await session.commit()

    assert result["from_stage"] == "Applied"
    assert result["to_stage"] == "Screening"

    history = await workflow_service.get_application_history(session, app.id)
    assert len(history) == 1
    assert history[0]["to_stage"] == "Screening"
    assert history[0]["note"] == "Moved to screening"


@pytest.mark.asyncio
async def test_transition_nonexistent_application_raises(workflow_service, session):
    """Transitioning a non-existent application raises ValueError."""
    with pytest.raises(ValueError, match="Application not found"):
        await workflow_service.transition_application(
            session, uuid.uuid4(), "Screening"
        )
