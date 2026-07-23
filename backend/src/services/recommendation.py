from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Job
from src.services.ranking import RankingService
from src.services.search import hybrid_search_candidates


class RecommendationEngine:
    """Candidate recommendation engine combining semantic search, skill matching,
    AI ranking, and hiring pattern signals."""

    def __init__(self):
        self.ranking_service = RankingService()

    async def recommend_candidates(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        job_result = await session.execute(
            select(Job)
            .where(Job.id == job_id)
            .where(Job.organization_id == organization_id)
        )
        job = job_result.scalar_one_or_none()
        if not job:
            return []

        ranked = await self.ranking_service.rank_candidates_for_job(
            session, job_id, organization_id, limit=limit * 3
        )

        if job.description:
            semantic = await hybrid_search_candidates(
                session, job.description, organization_id, limit=limit
            )
            semantic_ids = {r.get("candidate_id") for r in semantic}
            for r in ranked:
                r["semantic_match"] = r.get("candidate_id") in semantic_ids

        return ranked[:limit]


recommendation_engine = RecommendationEngine()
