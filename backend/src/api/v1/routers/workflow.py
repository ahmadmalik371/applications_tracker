import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.workflow import WorkflowService

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])
workflow_service = WorkflowService()


class StageCreate(BaseModel):
    name: str
    order: int = 0
    is_rejection_stage: bool = False
    is_hired_stage: bool = False
    color: str | None = None


class StageResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    order: int
    is_rejection_stage: bool
    is_hired_stage: bool
    color: str | None
    is_active: bool

    class Config:
        from_attributes = True


class TransitionRequest(BaseModel):
    to_stage: str
    note: str | None = None


class HistoryResponse(BaseModel):
    id: str
    from_stage: str | None
    to_stage: str
    changed_by_id: str | None
    note: str | None
    created_at: str | None


@router.get("/stages", response_model=list[StageResponse])
async def list_stages(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all workflow stages for the organization."""
    stages = await workflow_service.get_stages(session, current_user.organization_id)
    return stages


@router.post(
    "/stages", response_model=StageResponse, status_code=status.HTTP_201_CREATED
)
async def create_stage(
    stage_data: StageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a new workflow stage."""
    stage = await workflow_service.create_stage(
        session,
        current_user.organization_id,
        stage_data.name,
        stage_data.order,
        stage_data.is_rejection_stage,
        stage_data.is_hired_stage,
        stage_data.color,
    )
    await session.commit()
    await session.refresh(stage)
    return stage


@router.post("/applications/{application_id}/transition")
async def transition_application(
    application_id: uuid.UUID,
    request: TransitionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Move an application to a new workflow stage."""
    try:
        result = await workflow_service.transition_application(
            session,
            application_id,
            request.to_stage,
            changed_by_id=current_user.id,
            note=request.note,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/applications/{application_id}/history", response_model=list[HistoryResponse]
)
async def get_application_history(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get the full transition history for an application."""
    return await workflow_service.get_application_history(session, application_id)
