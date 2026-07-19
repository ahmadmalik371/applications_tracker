from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai import AIRecommendationFeedback, FeedbackRating


class FeedbackService:
    """Service for recording and querying recruiter feedback on AI recommendations."""

    async def record_feedback(
        self,
        session: AsyncSession,
        *,
        organization_id: uuid.UUID,
        recruiter_id: uuid.UUID,
        rating: str,
        candidate_id: Optional[uuid.UUID] = None,
        job_id: Optional[uuid.UUID] = None,
        ranking_score: Optional[float] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> AIRecommendationFeedback:
        fb = AIRecommendationFeedback(
            organization_id=organization_id,
            recruiter_id=recruiter_id,
            candidate_id=candidate_id,
            job_id=job_id,
            ranking_score=ranking_score,
            rating=rating,
            note=note,
            context=context,
        )
        session.add(fb)
        await session.commit()
        await session.refresh(fb)
        return fb

    async def get_feedback(
        self,
        session: AsyncSession,
        *,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[AIRecommendationFeedback], int]:
        stmt = select(AIRecommendationFeedback).where(
            AIRecommendationFeedback.organization_id == organization_id
        )
        count_stmt = select(func.count(AIRecommendationFeedback.id)).where(
            AIRecommendationFeedback.organization_id == organization_id
        )
        total = (await session.execute(count_stmt)).scalar_one()
        rows = (
            await session.execute(
                stmt.order_by(AIRecommendationFeedback.created_at.desc())
                .offset(skip).limit(limit)
            )
        ).scalars().all()
        return rows, total

    async def feedback_summary(
        self, session: AsyncSession, organization_id: uuid.UUID
    ) -> dict:
        rows = (
            await session.execute(
                select(AIRecommendationFeedback.rating, func.count())
                .where(AIRecommendationFeedback.organization_id == organization_id)
                .group_by(AIRecommendationFeedback.rating)
            )
        ).all()
        return {rating: count for rating, count in rows}


feedback_service = FeedbackService()
