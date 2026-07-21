import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Interview, InterviewFeedback, InterviewPanelist


class InterviewService:
    """Service for scheduling and managing interviews."""

    async def schedule_interview(
        self,
        session: AsyncSession,
        application_id: uuid.UUID,
        organization_id: uuid.UUID,
        interview_type: str,
        scheduled_at: str,
        duration_minutes: int = 60,
        location: str | None = None,
        meeting_link: str | None = None,
        panelist_ids: list[uuid.UUID] | None = None,
        created_by_id: uuid.UUID | None = None,
    ) -> Interview:
        from datetime import datetime

        dt = (
            datetime.fromisoformat(scheduled_at)
            if isinstance(scheduled_at, str)
            else scheduled_at
        )

        interview = Interview(
            application_id=application_id,
            organization_id=organization_id,
            interview_type=interview_type,
            scheduled_at=dt,
            duration_minutes=duration_minutes,
            location=location,
            meeting_link=meeting_link,
            created_by_id=created_by_id,
        )
        session.add(interview)
        await session.flush()

        if panelist_ids:
            for pid in panelist_ids:
                panelist = InterviewPanelist(
                    interview_id=interview.id,
                    user_id=pid,
                )
                session.add(panelist)
            await session.flush()

        return interview

    async def get_interviews_for_application(
        self, session: AsyncSession, application_id: uuid.UUID
    ) -> list[Interview]:
        result = await session.execute(
            select(Interview)
            .where(Interview.application_id == application_id)
            .order_by(desc(Interview.scheduled_at))
        )
        return list(result.scalars().all())

    async def update_status(
        self, session: AsyncSession, interview_id: uuid.UUID, status: str
    ) -> Interview:
        result = await session.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        if not interview:
            raise ValueError("Interview not found")
        interview.status = status
        await session.flush()
        return interview

    async def submit_feedback(
        self,
        session: AsyncSession,
        interview_id: uuid.UUID,
        panelist_id: uuid.UUID,
        rating: int,
        strengths: str | None = None,
        weaknesses: str | None = None,
        recommendation: str | None = None,
        notes: str | None = None,
    ) -> InterviewFeedback:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        feedback = InterviewFeedback(
            interview_id=interview_id,
            panelist_id=panelist_id,
            rating=rating,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            notes=notes,
        )
        session.add(feedback)
        await session.flush()
        return feedback

    async def get_feedback(
        self, session: AsyncSession, interview_id: uuid.UUID
    ) -> list[InterviewFeedback]:
        result = await session.execute(
            select(InterviewFeedback)
            .where(InterviewFeedback.interview_id == interview_id)
            .order_by(desc(InterviewFeedback.created_at))
        )
        return list(result.scalars().all())

    async def get_panelists(
        self, session: AsyncSession, interview_id: uuid.UUID
    ) -> list[InterviewPanelist]:
        result = await session.execute(
            select(InterviewPanelist).where(
                InterviewPanelist.interview_id == interview_id
            )
        )
        return list(result.scalars().all())
