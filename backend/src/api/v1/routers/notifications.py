import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.notification import EmailTemplateService, NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()
template_service = EmailTemplateService()


# --- Notification schemas ---


class NotificationCreate(BaseModel):
    title: str
    message: str
    channel: str = "in_app"
    user_id: str | None = None
    metadata: dict | None = None


class NotificationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None
    channel: str
    title: str
    message: str
    status: str
    read: bool
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# --- Email template schemas ---


class TemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    variables: list[str] | None = None


class TemplateResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    subject: str
    body: str
    variables: str | None
    is_active: bool
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RenderRequest(BaseModel):
    variables: dict


# --- Notification endpoints ---


@router.post(
    "", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    req: NotificationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a notification."""
    notif = await notification_service.create_notification(
        session,
        current_user.organization_id,
        req.title,
        req.message,
        user_id=uuid.UUID(req.user_id) if req.user_id else current_user.id,
        channel=req.channel,
        metadata=req.metadata,
    )
    await session.commit()
    await session.refresh(notif)
    return notif


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    return await notification_service.get_user_notifications(
        session, current_user.id, limit
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get unread notification count."""
    count = await notification_service.get_unread_count(session, current_user.id)
    return {"unread": count}


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    notif = await notification_service.mark_as_read(session, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    await session.commit()
    return {"id": str(notif.id), "read": True}


@router.patch("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    count = await notification_service.mark_all_read(session, current_user.id)
    await session.commit()
    return {"marked_read": count}


# --- Email template endpoints ---

templates_router = APIRouter(prefix="/email-templates", tags=["email-templates"])


@templates_router.post(
    "", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_template(
    req: TemplateCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create an email template."""
    template = await template_service.create_template(
        session,
        current_user.organization_id,
        req.name,
        req.subject,
        req.body,
        req.variables,
    )
    await session.commit()
    await session.refresh(template)
    return template


@templates_router.get("", response_model=list[TemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List email templates for the organization."""
    return await template_service.list_templates(session, current_user.organization_id)


@templates_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get a specific email template."""
    template = await template_service.get_template(session, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@templates_router.post("/{template_id}/render")
async def render_template(
    template_id: uuid.UUID,
    req: RenderRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Render an email template with variable substitution."""
    try:
        result = await template_service.render_template(
            session, template_id, req.variables
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
