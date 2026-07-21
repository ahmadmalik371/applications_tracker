import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Application, Candidate, Job


async def create_job(
    session: AsyncSession,
    organization_id: uuid.UUID,
    created_by_id: uuid.UUID,
    title: str,
    description: str | None = None,
    location: str | None = None,
    employment_type: str | None = None,
) -> Job:
    job = Job(
        title=title,
        description=description,
        location=location,
        employment_type=employment_type,
        organization_id=organization_id,
        created_by_id=created_by_id,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def list_jobs(
    session: AsyncSession, organization_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> list[Job]:
    result = await session.execute(
        select(Job)
        .where(Job.organization_id == organization_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_job(session: AsyncSession, job_id: uuid.UUID, **kwargs) -> Job | None:
    job = await get_job(session, job_id)
    if not job:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)

    await session.commit()
    await session.refresh(job)
    return job


async def delete_job(session: AsyncSession, job_id: uuid.UUID) -> bool:
    job = await get_job(session, job_id)
    if not job:
        return False
    await session.delete(job)
    await session.commit()
    return True


async def create_candidate(
    session: AsyncSession,
    organization_id: uuid.UUID,
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
) -> Candidate:
    candidate = Candidate(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        organization_id=organization_id,
    )
    session.add(candidate)
    await session.commit()
    await session.refresh(candidate)
    return candidate


async def get_candidate(
    session: AsyncSession, candidate_id: uuid.UUID
) -> Candidate | None:
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    return result.scalar_one_or_none()


async def list_candidates(
    session: AsyncSession, organization_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> list[Candidate]:
    result = await session.execute(
        select(Candidate)
        .where(Candidate.organization_id == organization_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_candidate(
    session: AsyncSession, candidate_id: uuid.UUID, **kwargs
) -> Candidate | None:
    candidate = await get_candidate(session, candidate_id)
    if not candidate:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(candidate, key):
            setattr(candidate, key, value)

    await session.commit()
    await session.refresh(candidate)
    return candidate


async def delete_candidate(session: AsyncSession, candidate_id: uuid.UUID) -> bool:
    candidate = await get_candidate(session, candidate_id)
    if not candidate:
        return False
    await session.delete(candidate)
    await session.commit()
    return True


async def create_application(
    session: AsyncSession,
    organization_id: uuid.UUID,
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
) -> Application:
    application = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        organization_id=organization_id,
    )
    session.add(application)
    await session.commit()
    await session.refresh(application)
    return application


async def get_application(
    session: AsyncSession, application_id: uuid.UUID
) -> Application | None:
    result = await session.execute(
        select(Application).where(Application.id == application_id)
    )
    return result.scalar_one_or_none()


async def list_applications(
    session: AsyncSession, organization_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> list[Application]:
    result = await session.execute(
        select(Application)
        .where(Application.organization_id == organization_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_application(
    session: AsyncSession, application_id: uuid.UUID, **kwargs
) -> Application | None:
    application = await get_application(session, application_id)
    if not application:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(application, key):
            setattr(application, key, value)

    await session.commit()
    await session.refresh(application)
    return application
