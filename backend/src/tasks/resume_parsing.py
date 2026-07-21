"""
Celery task for parsing uploaded resumes, extracting candidate info,
scoring against job requirements, and updating the database.
"""
import logging
import uuid
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


def _score_candidate_against_job(
    candidate_data: dict,
    job_data: dict,
) -> tuple[float, dict]:
    """
    Score a candidate against a job based on extracted resume data.
    Returns (score, breakdown).
    """
    score = 0.0
    breakdown = {}

    # Skills match (up to 40 points)
    candidate_skills = set(s.lower() for s in candidate_data.get("skills", []))
    job_skills = set(s.lower() for s in job_data.get("skills", []))
    if job_skills:
        matched_skills = candidate_skills & job_skills
        skill_score = (len(matched_skills) / len(job_skills)) * 40
        breakdown["skills"] = round(skill_score, 1)
        score += skill_score
    else:
        breakdown["skills"] = 0

    # Experience match (up to 30 points)
    candidate_years = candidate_data.get("years_experience", 0)
    required_years = job_data.get("required_experience", 0)
    if required_years > 0:
        exp_ratio = min(candidate_years / required_years, 1.5)
        exp_score = min(exp_ratio * 30, 30)
        breakdown["experience"] = round(exp_score, 1)
        score += exp_score
    else:
        breakdown["experience"] = 15  # No requirement, partial credit

    # Education match (up to 20 points)
    candidate_edu = candidate_data.get("education", "").lower()
    required_edu = job_data.get("required_education", "").lower()
    if required_edu and candidate_edu:
        edu_score = 20 if required_edu in candidate_edu else 5
        breakdown["education"] = edu_score
        score += edu_score
    else:
        breakdown["education"] = 10

    # Location match (up to 10 points)
    candidate_loc = candidate_data.get("location", "").lower()
    job_loc = job_data.get("location", "").lower()
    if job_loc and candidate_loc:
        loc_score = 10 if job_loc in candidate_loc or candidate_loc in job_loc else 3
        breakdown["location"] = loc_score
        score += loc_score
    else:
        breakdown["location"] = 5

    return round(min(score, 100), 1), breakdown


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    queue="parsing",
    acks_late=True,
)
def parse_resume_task(
    self,
    candidate_id: str,
    resume_url: str,
    job_id: Optional[str] = None,
):
    """
    Parse a candidate's resume, extract structured data, score against job,
    and update the database.
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            _parse_resume_async(candidate_id, resume_url, job_id)
        )
        return result
    finally:
        loop.close()


async def _parse_resume_async(
    candidate_id: str,
    resume_url: str,
    job_id: Optional[str] = None,
):
    """Async implementation of resume parsing."""
    async with AsyncSessionLocal() as db:
        try:
            cid = uuid.UUID(candidate_id)

            # Get candidate
            from src.models import Candidate
            result = await db.execute(select(Candidate).where(Candidate.id == cid))
            candidate = result.scalar_one_or_none()
            if not candidate:
                logger.error("Candidate %s not found", candidate_id)
                return {"error": "Candidate not found"}

            # Simulate resume parsing (in production, call an AI service)
            # Extract basic info from the resume URL/file
            parsed_data = {
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
                "years_experience": 5,
                "education": "Bachelor's Degree in Computer Science",
                "location": candidate.resume_url or "",
                "summary": "Experienced software engineer with full-stack expertise.",
            }

            # Update candidate with parsed data
            from src.services.candidates import update_candidate
            await update_candidate(
                db,
                cid,
                skills_summary=", ".join(parsed_data["skills"]),
                parsed_summary=parsed_data["summary"],
            )

            # If job_id provided, score the candidate against the job
            score = None
            breakdown = None
            if job_id:
                jid = uuid.UUID(job_id)
                from src.models import Job
                result = await db.execute(select(Job).where(Job.id == jid))
                job = result.scalar_one_or_none()
                if job:
                    job_data = {
                        "skills": job.skills_required or [],
                        "required_experience": job.years_experience_required or 0,
                        "required_education": job.education_required or "",
                        "location": job.location or "",
                    }
                    score, breakdown = _score_candidate_against_job(parsed_data, job_data)

                    # Update application with score
                    from src.models import Application
                    from src.models.application import ApplicationStage
                    result = await db.execute(
                        select(Application)
                        .where(Application.candidate_id == cid)
                        .where(Application.job_id == jid)
                    )
                    application = result.scalar_one_or_none()
                    if application:
                        application.score = score
                        application.status = ApplicationStage.SCREENING.value
                        await db.commit()

            # Create notification for recruiters
            from src.services.notification import NotificationService
            notif_service = NotificationService()
            await notif_service.create_notification(
                db,
                candidate.organization_id,
                "New Application Processed",
                f"AI has processed {candidate.first_name} {candidate.last_name}'s application"
                + (f" with score {score}/100" if score else ""),
                channel="in_app",
            )
            await db.commit()

            logger.info(
                "Parsed resume for candidate %s (score=%s)",
                candidate_id, score,
            )

            return {
                "candidate_id": candidate_id,
                "parsed": parsed_data,
                "score": score,
                "breakdown": breakdown,
            }

        except Exception as e:
            logger.error("Failed to parse resume for %s: %s", candidate_id, str(e))
            raise self.retry(exc=e)