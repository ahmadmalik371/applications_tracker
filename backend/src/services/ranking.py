import uuid
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Candidate, Job, Application
from src.services.features import FeatureExtractor
from src.services.embedding import EmbeddingService


class RankingService:
    """Service for ranking candidates against jobs using features and embeddings."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.embedding_service = EmbeddingService()

    async def calculate_match_score(
        self,
        candidate: Candidate,
        job: Job,
        embedding_weight: float = 0.3,
        feature_weight: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score for a candidate-job pair.
        
        Returns:
        {
            "match_score": 0-100,
            "confidence": 0-1,
            "features": {...},
            "embedding_similarity": 0-1,
            "breakdown": {...}
        }
        """
        # Extract features
        features = self.feature_extractor.extract_candidate_features(candidate, job)

        # Calculate feature score (average of all normalized features)
        feature_score = sum(features.values()) / len(features) if features else 0.0

        # Calculate embedding similarity
        embedding_similarity = await self._calculate_embedding_similarity(candidate, job)

        # Combine scores
        match_score = (
            feature_weight * feature_score + embedding_weight * embedding_similarity
        ) * 100

        # Calculate confidence (how sure we are about this match)
        confidence = self._calculate_confidence(candidate, job, features)

        return {
            "match_score": round(match_score, 2),
            "confidence": round(confidence, 2),
            "features": {k: round(v, 2) for k, v in features.items()},
            "embedding_similarity": round(embedding_similarity, 2),
            "breakdown": {
                "feature_score": round(feature_score, 2),
                "feature_weight": feature_weight,
                "embedding_weight": embedding_weight,
            },
        }

    async def rank_candidates_for_job(
        self,
        session: AsyncSession,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        limit: int = 100,
    ) -> list[Dict[str, Any]]:
        """
        Rank all candidates for a specific job.
        
        Returns sorted list of candidates with match scores.
        """
        # Fetch job
        job_result = await session.execute(
            select(Job).where(Job.id == job_id).where(Job.organization_id == organization_id)
        )
        job = job_result.scalar_one_or_none()
        if not job:
            return []

        # Fetch all active candidates
        candidates_result = await session.execute(
            select(Candidate).where(Candidate.organization_id == organization_id).limit(limit)
        )
        candidates = candidates_result.scalars().all()

        # Score each candidate
        ranked = []
        for candidate in candidates:
            score_data = await self.calculate_match_score(candidate, job)
            ranked.append({
                "candidate_id": str(candidate.id),
                "candidate_name": f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                "candidate_email": candidate.email,
                **score_data,
            })

        # Sort by match score descending
        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked

    async def rank_jobs_for_candidate(
        self,
        session: AsyncSession,
        candidate_id: uuid.UUID,
        organization_id: uuid.UUID,
        limit: int = 50,
    ) -> list[Dict[str, Any]]:
        """
        Rank all jobs for a specific candidate.
        
        Returns sorted list of jobs with match scores.
        """
        # Fetch candidate
        candidate_result = await session.execute(
            select(Candidate).where(Candidate.id == candidate_id).where(Candidate.organization_id == organization_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        if not candidate:
            return []

        # Fetch all active jobs
        jobs_result = await session.execute(
            select(Job).where(Job.organization_id == organization_id).where(Job.is_published == True).limit(limit)
        )
        jobs = jobs_result.scalars().all()

        # Score each job
        ranked = []
        for job in jobs:
            score_data = await self.calculate_match_score(candidate, job)
            ranked.append({
                "job_id": str(job.id),
                "job_title": job.title,
                "job_location": job.location,
                **score_data,
            })

        # Sort by match score descending
        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked

    async def _calculate_embedding_similarity(
        self, candidate: Candidate, job: Job
    ) -> float:
        """Calculate cosine similarity between candidate and job embeddings."""
        if not candidate.embedding or not job.embedding:
            return 0.5  # Default neutral similarity if embeddings are missing

        # Embeddings are stored as vectors; calculate cosine similarity
        similarity = self._cosine_similarity(candidate.embedding, job.embedding)
        return max(0.0, min(1.0, similarity))  # Clamp to 0-1

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.5

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
        magnitude2 = sum(b ** 2 for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.5

        return dot_product / (magnitude1 * magnitude2)

    def _calculate_confidence(
        self, candidate: Candidate, job: Job, features: Dict[str, float]
    ) -> float:
        """Calculate confidence in the match score (0-1)."""
        confidence_factors = []

        # Factor 1: Data completeness for candidate
        if candidate.parsed_data:
            parsed_fields = sum(
                1 for field in ["skills", "experience", "education"]
                if candidate.parsed_data.get(field)
            )
            confidence_factors.append(parsed_fields / 3.0)
        else:
            confidence_factors.append(0.2)

        # Factor 2: Embedding availability
        if candidate.embedding and job.embedding:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.6)

        # Factor 3: Feature stability (how many features are not zero)
        non_zero_features = sum(1 for v in features.values() if v > 0)
        confidence_factors.append(non_zero_features / len(features) if features else 0.5)

        # Average confidence factors
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
