import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Application, WorkflowStage, ApplicationWorkflowHistory
from src.models.application import ApplicationStage


class WorkflowService:
    """Service for managing configurable hiring workflows."""

    async def get_stages(
        self, session: AsyncSession, organization_id: uuid.UUID
    ) -> List[WorkflowStage]:
        result = await session.execute(
            select(WorkflowStage)
            .where(WorkflowStage.organization_id == organization_id)
            .where(WorkflowStage.is_active == True)
            .order_by(WorkflowStage.order.asc())
        )
        return list(result.scalars().all())

    async def create_stage(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        name: str,
        order: int = 0,
        is_rejection_stage: bool = False,
        is_hired_stage: bool = False,
        color: Optional[str] = None,
    ) -> WorkflowStage:
        stage = WorkflowStage(
            organization_id=organization_id,
            name=name,
            order=order,
            is_rejection_stage=is_rejection_stage,
            is_hired_stage=is_hired_stage,
            color=color,
        )
        session.add(stage)
        await session.flush()
        return stage

    async def transition_application(
        self,
        session: AsyncSession,
        application_id: uuid.UUID,
        to_stage: str,
        changed_by_id: Optional[uuid.UUID] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Move an application to a new stage and record the transition."""
        app_result = await session.execute(
            select(Application).where(Application.id == application_id)
        )
        application = app_result.scalar_one_or_none()
        if not application:
            raise ValueError("Application not found")

        from_stage = application.status
        application.status = to_stage

        history = ApplicationWorkflowHistory(
            application_id=application_id,
            from_stage=from_stage,
            to_stage=to_stage,
            changed_by_id=changed_by_id,
            note=note,
        )
        session.add(history)
        await session.flush()

        return {
            "application_id": str(application_id),
            "from_stage": from_stage,
            "to_stage": to_stage,
            "history_id": str(history.id),
        }

    async def get_application_history(
        self, session: AsyncSession, application_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        result = await session.execute(
            select(ApplicationWorkflowHistory)
            .where(ApplicationWorkflowHistory.application_id == application_id)
            .order_by(desc(ApplicationWorkflowHistory.created_at))
        )
        rows = result.scalars().all()
        return [
            {
                "id": str(h.id),
                "from_stage": h.from_stage,
                "to_stage": h.to_stage,
                "changed_by_id": str(h.changed_by_id) if h.changed_by_id else None,
                "note": h.note,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in rows
        ]
