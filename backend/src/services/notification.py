import json
import uuid

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import EmailTemplate, Notification


class NotificationService:
    """Service for creating, dispatching, and tracking notifications."""

    async def create_notification(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        title: str,
        message: str,
        user_id: uuid.UUID | None = None,
        channel: str = "in_app",
        metadata: dict | None = None,
    ) -> Notification:
        notification = Notification(
            organization_id=organization_id,
            user_id=user_id,
            channel=channel,
            title=title,
            message=message,
            status="pending",
            metadata_=json.dumps(metadata) if metadata else None,
        )
        session.add(notification)
        await session.flush()
        return notification

    async def get_user_notifications(
        self, session: AsyncSession, user_id: uuid.UUID, limit: int = 50
    ) -> list[Notification]:
        result = await session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_read(
        self, session: AsyncSession, notification_id: uuid.UUID
    ) -> Notification | None:
        result = await session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification:
            notification.read = True
            await session.flush()
        return notification

    async def mark_all_read(self, session: AsyncSession, user_id: uuid.UUID) -> int:
        result = await session.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.read == False)
            .values(read=True)
        )
        return result.rowcount

    async def get_unread_count(self, session: AsyncSession, user_id: uuid.UUID) -> int:
        from sqlalchemy import func

        result = await session.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .where(Notification.read == False)
        )
        return result.scalar() or 0


class EmailTemplateService:
    """Service for managing database-stored email templates with variable substitution."""

    async def create_template(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        name: str,
        subject: str,
        body: str,
        variables: list[str] | None = None,
    ) -> EmailTemplate:
        template = EmailTemplate(
            organization_id=organization_id,
            name=name,
            subject=subject,
            body=body,
            variables=json.dumps(variables) if variables else None,
        )
        session.add(template)
        await session.flush()
        return template

    async def list_templates(
        self, session: AsyncSession, organization_id: uuid.UUID
    ) -> list[EmailTemplate]:
        result = await session.execute(
            select(EmailTemplate)
            .where(EmailTemplate.organization_id == organization_id)
            .where(EmailTemplate.is_active == True)
            .order_by(desc(EmailTemplate.created_at))
        )
        return list(result.scalars().all())

    async def get_template(
        self, session: AsyncSession, template_id: uuid.UUID
    ) -> EmailTemplate | None:
        result = await session.execute(
            select(EmailTemplate).where(EmailTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def render_template(
        self, session: AsyncSession, template_id: uuid.UUID, variables: dict[str, str]
    ) -> dict[str, str]:
        """Render an email template by substituting {{variable}} placeholders."""
        template = await self.get_template(session, template_id)
        if not template:
            raise ValueError("Template not found")

        subject = template.subject
        body = template.body
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        return {"subject": subject, "body": body}
