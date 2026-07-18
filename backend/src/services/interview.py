import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Interview, InterviewPanelist, InterviewFeedback


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
        location: Optional[str] = None,
        meeting_link: Optional[str] = None,
        panelist_ids: Optional[List[uuid.UUID]] = None,
        created_by_id: Optional[uuid.UUID] = None,
    ) -> Interview:
        from datetime import datetime
        dt = datetime.fromisoformat(scheduled_at) if isinstance(scheduled_at, str) else scheduled_at

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
    ) -> List[Interview]:
        result = await session.execute(
            select(Interview)
            .where(Interview.application_id == application_id)
            .order_by(desc(Interview.scheduled_at))
        )
        return list(result.scalars().all())

    async def update_status(
        self, session: AsyncSession, interview_id: uuid.UUID, status: str
    ) -> Interview:
        result = await session.execute(select(Interview).where(Interview.id == interview_id))
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
        strengths: Optional[str] = None,
        weaknesses: Optional[str] = None,
        recommendation: Optional[str] = None,
        notes: Optional[str] = None,
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
    ) -> List[InterviewFeedback]:
        result = await session.execute(
            select(InterviewFeedback)
            .where(InterviewFeedback.interview_id == interview_id)
            .order_by(desc(InterviewFeedback.created_at))
        )
        return list(result.scalars().all())

    async def get_panelists(
        self, session: AsyncSession, interview_id: uuid.UUID
    ) -> List[InterviewPanelist]:
        result = await session.execute(
            select(InterviewPanelist).where(InterviewPanelist.interview_id == interview_id)
        )
        return list(result.scalars().all())
