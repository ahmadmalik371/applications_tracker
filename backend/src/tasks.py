import asyncio
import json

from src.core.celery_app import app
from src.core.database import AsyncSessionLocal
from src.services.candidates import update_candidate
from src.services.embedding import generate_candidate_embedding, generate_job_embedding
from src.services.parsing import parse_resume_from_file


@app.task(bind=True, max_retries=3, queue="parsing")
def parse_resume_task(self, candidate_id: str, resume_url: str):
    """Celery task to parse resume asynchronously."""
    try:
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        parsed_data = loop.run_until_complete(parse_resume_from_file(resume_url))

        # Store parsed data
        loop.run_until_complete(_store_parsed_resume_data(candidate_id, parsed_data))

        # Trigger embedding generation
        generate_candidate_embedding_task.delay(candidate_id, json.dumps(parsed_data))

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "parsed_data": parsed_data,
        }
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            from src.core.celery_app import send_to_dlq

            send_to_dlq.delay(
                "parse_resume_task",
                self.request.id,
                [candidate_id, resume_url],
                {},
                str(exc),
            )
            return {"status": "failed", "error": str(exc)}
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@app.task(bind=True, max_retries=3, queue="embeddings")
def generate_candidate_embedding_task(self, candidate_id: str, parsed_data_json: str):
    """Celery task to generate candidate embedding."""
    try:
        loop = asyncio.get_event_loop()
        parsed_data = json.loads(parsed_data_json)

        # Generate embedding
        embedding = loop.run_until_complete(generate_candidate_embedding(parsed_data))

        # Store embedding
        loop.run_until_complete(_store_candidate_embedding(candidate_id, embedding))

        return {
            "status": "success",
            "candidate_id": candidate_id,
            "embedding_generated": True,
        }
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            from src.core.celery_app import send_to_dlq

            send_to_dlq.delay(
                "generate_candidate_embedding_task",
                self.request.id,
                [candidate_id, parsed_data_json],
                {},
                str(exc),
            )
            return {"status": "failed", "error": str(exc)}
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@app.task(bind=True, max_retries=3, queue="embeddings")
def generate_job_embedding_task(self, job_id: str, job_description: str):
    """Celery task to generate job embedding."""
    try:
        loop = asyncio.get_event_loop()

        # Generate embedding
        embedding = loop.run_until_complete(generate_job_embedding(job_description))

        # Store embedding
        loop.run_until_complete(_store_job_embedding(job_id, embedding))

        return {"status": "success", "job_id": job_id, "embedding_generated": True}
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            from src.core.celery_app import send_to_dlq

            send_to_dlq.delay(
                "generate_job_embedding_task",
                self.request.id,
                [job_id, job_description],
                {},
                str(exc),
            )
            return {"status": "failed", "error": str(exc)}
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


async def _store_parsed_resume_data(candidate_id: str, parsed_data: dict):
    """Store parsed resume data in database."""
    async with AsyncSessionLocal() as session:
        try:
            # Convert parsed_data to JSON string for storage
            parsed_json = json.dumps(parsed_data)

            # Update candidate with parsed data
            await update_candidate(session, candidate_id, parsed_data=parsed_json)
        except Exception as e:
            raise ValueError(f"Failed to store parsed resume data: {str(e)}")


async def _store_candidate_embedding(candidate_id: str, embedding: list):
    """Store candidate embedding in database."""
    async with AsyncSessionLocal() as session:
        try:
            # Update candidate with embedding
            await update_candidate(session, candidate_id, embedded=embedding)
        except Exception as e:
            raise ValueError(f"Failed to store candidate embedding: {str(e)}")


async def _store_job_embedding(job_id: str, embedding: list):
    """Store job embedding in database."""
    from src.services.candidates import update_job

    async with AsyncSessionLocal() as session:
        try:
            # Update job with embedding
            await update_job(session, job_id, embedding=embedding)
        except Exception as e:
            raise ValueError(f"Failed to store job embedding: {str(e)}")
