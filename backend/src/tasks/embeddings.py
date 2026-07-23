"""
Celery tasks for generating vector embeddings for candidates and jobs.
"""
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    queue="embeddings",
    acks_late=True,
)
def generate_candidate_embedding_task(self, candidate_id: str, resume_text: str = ""):
    """
    Generate vector embedding for a candidate's profile.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            _generate_candidate_embedding_async(candidate_id, resume_text)
        )
        return result
    finally:
        loop.close()


async def _generate_candidate_embedding_async(candidate_id: str, resume_text: str = ""):
    """Async implementation of candidate embedding generation."""
    async with AsyncSessionLocal() as db:
        try:
            cid = uuid.UUID(candidate_id)

            from src.models import Candidate
            result = await db.execute(select(Candidate).where(Candidate.id == cid))
            candidate = result.scalar_one_or_none()
            if not candidate:
                logger.error("Candidate %s not found", candidate_id)
                return {"error": "Candidate not found"}

            # In production, use an embedding model (e.g. OpenAI, Gemini, etc.)
            # For now we generate a placeholder embedding
            import hashlib
            text_to_embed = f"{candidate.first_name} {candidate.last_name} {resume_text or ''}"
            hash_bytes = hashlib.sha256(text_to_embed.encode()).digest()
            # Create a simple 128-dim vector from hash (for demo purposes)
            embedding = [float(b) / 255.0 for b in hash_bytes[:128]]

            # Store embedding (if the model has a vector field)
            # For now we just log it
            logger.info(
                "Generated embedding for candidate %s (dim=%d)",
                candidate_id, len(embedding),
            )

            await db.commit()
            return {
                "candidate_id": candidate_id,
                "embedding_dim": len(embedding),
                "status": "success",
            }

        except Exception as e:
            logger.error("Failed to generate embedding for %s: %s", candidate_id, str(e))
            raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    queue="embeddings",
    acks_late=True,
)
def generate_job_embedding_task(self, job_id: str, description: str = ""):
    """
    Generate vector embedding for a job posting.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            _generate_job_embedding_async(job_id, description)
        )
        return result
    finally:
        loop.close()


async def _generate_job_embedding_async(job_id: str, description: str = ""):
    """Async implementation of job embedding generation."""
    async with AsyncSessionLocal() as db:
        try:
            jid = uuid.UUID(job_id)

            from src.models import Job
            result = await db.execute(select(Job).where(Job.id == jid))
            job = result.scalar_one_or_none()
            if not job:
                logger.error("Job %s not found", job_id)
                return {"error": "Job not found"}

            # In production, use an embedding model (e.g. OpenAI, Gemini, etc.)
            # For now we generate a placeholder embedding
            import hashlib
            text_to_embed = f"{job.title} {description or ''}"
            hash_bytes = hashlib.sha256(text_to_embed.encode()).digest()
            # Create a simple 128-dim vector from hash (for demo purposes)
            embedding = [float(b) / 255.0 for b in hash_bytes[:128]]

            logger.info(
                "Generated embedding for job %s (dim=%d)",
                job_id, len(embedding),
            )

            await db.commit()
            return {
                "job_id": job_id,
                "embedding_dim": len(embedding),
                "status": "success",
            }

        except Exception as e:
            logger.error("Failed to generate embedding for %s: %s", job_id, str(e))
            raise self.retry(exc=e)