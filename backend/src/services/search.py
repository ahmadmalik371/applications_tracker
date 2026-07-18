import uuid
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from src.models import Candidate, Job, Application
from src.services.embedding import compute_similarity


async def find_similar_candidates(
    session: AsyncSession,
    job_id: uuid.UUID,
    organization_id: uuid.UUID,
    limit: int = 10,
) -> List[dict]:
    """
    Find candidates most similar to a job using vector similarity.
    Returns candidates ranked by similarity score.
    """
    try:
        # Get job with embedding
        job_result = await session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job or job.embedding is None:
            # No embedding available for job
            return []
        
        # Get all candidates with embeddings for organization
        candidates_result = await session.execute(
            select(Candidate).where(
                and_(
                    Candidate.organization_id == organization_id,
                    Candidate.embedded.isnot(None)
                )
            )
        )
        candidates = candidates_result.scalars().all()
        
        # Calculate similarity scores
        matches = []
        for candidate in candidates:
            similarity = await compute_similarity(job.embedding, candidate.embedded)
            matches.append({
                'candidate_id': candidate.id,
                'candidate_name': f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                'email': candidate.email,
                'score': round(similarity, 4),
                'status': candidate.status,
            })
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:limit]
    except Exception as e:
        raise ValueError(f"Failed to find similar candidates: {str(e)}")


async def find_matching_jobs(
    session: AsyncSession,
    candidate_id: uuid.UUID,
    organization_id: uuid.UUID,
    limit: int = 10,
) -> List[dict]:
    """
    Find jobs most similar to a candidate using vector similarity.
    Returns jobs ranked by similarity score.
    """
    try:
        # Get candidate with embedding
        candidate_result = await session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        
        if not candidate or candidate.embedded is None:
            # No embedding available for candidate
            return []
        
        # Get all published jobs with embeddings for organization
        jobs_result = await session.execute(
            select(Job).where(
                and_(
                    Job.organization_id == organization_id,
                    Job.embedding.isnot(None),
                    Job.is_published == True
                )
            )
        )
        jobs = jobs_result.scalars().all()
        
        # Calculate similarity scores
        matches = []
        for job in jobs:
            similarity = await compute_similarity(candidate.embedded, job.embedding)
            matches.append({
                'job_id': job.id,
                'title': job.title,
                'location': job.location,
                'score': round(similarity, 4),
                'status': job.status,
            })
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:limit]
    except Exception as e:
        raise ValueError(f"Failed to find matching jobs: {str(e)}")


async def bulk_create_auto_applications(
    session: AsyncSession,
    job_id: uuid.UUID,
    organization_id: uuid.UUID,
    similarity_threshold: float = 0.7,
) -> List[uuid.UUID]:
    """
    Automatically create applications for candidates that exceed similarity threshold.
    """
    try:
        # Get similar candidates
        similar = await find_similar_candidates(session, job_id, organization_id, limit=100)
        
        created_application_ids = []
        
        for match in similar:
            if match['score'] >= similarity_threshold:
                # Check if application already exists
                existing = await session.execute(
                    select(Application).where(
                        and_(
                            Application.job_id == job_id,
                            Application.candidate_id == match['candidate_id']
                        )
                    )
                )
                
                if not existing.scalar_one_or_none():
                    # Create new application
                    app = Application(
                        job_id=job_id,
                        candidate_id=match['candidate_id'],
                        organization_id=organization_id,
                        score=match['score'],
                    )
                    session.add(app)
                    created_application_ids.append(app.id)
        
        if created_application_ids:
            await session.commit()
        
        return created_application_ids
    except Exception as e:
        raise ValueError(f"Failed to bulk create applications: {str(e)}")
