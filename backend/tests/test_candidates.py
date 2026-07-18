import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Candidate, Job, Application, Organization, User, Role
from src.services.candidates import (
    create_job, get_job, list_jobs, update_job, delete_job,
    create_candidate, get_candidate, list_candidates, update_candidate, delete_candidate,
    create_application, get_application, list_applications, update_application,
)
from src.services.embedding import generate_mock_embedding, compute_similarity


@pytest.mark.asyncio
async def test_create_job(db: AsyncSession, test_org: Organization):
    """Test job creation."""
    job = await create_job(
        db,
        organization_id=test_org.id,
        created_by_id=uuid4(),
        title="Software Engineer",
        description="We are looking for a talented software engineer",
        location="San Francisco",
        employment_type="Full-time"
    )
    
    assert job is not None
    assert job.title == "Software Engineer"
    assert job.organization_id == test_org.id
    assert job.status == "Draft"


@pytest.mark.asyncio
async def test_create_candidate(db: AsyncSession, test_org: Organization):
    """Test candidate creation."""
    candidate = await create_candidate(
        db,
        organization_id=test_org.id,
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890"
    )
    
    assert candidate is not None
    assert candidate.email == "john.doe@example.com"
    assert candidate.organization_id == test_org.id
    assert candidate.status == "New"


@pytest.mark.asyncio
async def test_create_application(db: AsyncSession, test_org: Organization):
    """Test application creation."""
    job = await create_job(
        db,
        organization_id=test_org.id,
        created_by_id=uuid4(),
        title="Software Engineer",
    )
    
    candidate = await create_candidate(
        db,
        organization_id=test_org.id,
        email="john.doe@example.com",
    )
    
    application = await create_application(
        db,
        organization_id=test_org.id,
        job_id=job.id,
        candidate_id=candidate.id,
    )
    
    assert application is not None
    assert application.job_id == job.id
    assert application.candidate_id == candidate.id
    assert application.status == "Applied"


@pytest.mark.asyncio
async def test_list_jobs(db: AsyncSession, test_org: Organization):
    """Test listing jobs."""
    # Create multiple jobs
    for i in range(3):
        await create_job(
            db,
            organization_id=test_org.id,
            created_by_id=uuid4(),
            title=f"Job {i}",
        )
    
    jobs = await list_jobs(db, organization_id=test_org.id, limit=10)
    assert len(jobs) >= 3


@pytest.mark.asyncio
async def test_update_candidate(db: AsyncSession, test_org: Organization):
    """Test updating candidate."""
    candidate = await create_candidate(
        db,
        organization_id=test_org.id,
        email="john@example.com",
        first_name="John"
    )
    
    updated = await update_candidate(
        db,
        candidate.id,
        first_name="Jane",
        status="Review"
    )
    
    assert updated.first_name == "Jane"
    assert updated.status == "Review"


@pytest.mark.asyncio
async def test_delete_candidate(db: AsyncSession, test_org: Organization):
    """Test deleting candidate."""
    candidate = await create_candidate(
        db,
        organization_id=test_org.id,
        email="john@example.com",
    )
    
    result = await delete_candidate(db, candidate.id)
    assert result is True
    
    deleted = await get_candidate(db, candidate.id)
    assert deleted is None


def test_mock_embedding_generation():
    """Test mock embedding generation."""
    embedding = generate_mock_embedding("Software Engineer with Python experience")
    
    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # Default dimension


def test_embedding_similarity():
    """Test embedding similarity computation."""
    import asyncio
    
    text1 = "Python developer"
    text2 = "Python developer"
    text3 = "Product manager"
    
    emb1 = generate_mock_embedding(text1)
    emb2 = generate_mock_embedding(text2)
    emb3 = generate_mock_embedding(text3)
    
    # Same text should have high similarity
    async def compute():
        sim_same = await compute_similarity(emb1, emb2)
        sim_different = await compute_similarity(emb1, emb3)
        return sim_same, sim_different
    
    sim_same, sim_different = asyncio.run(compute())
    
    # Exact same embedding should have similarity of 1.0
    assert sim_same == 1.0


def test_parse_resume_skills():
    """Test skill extraction from resume text."""
    from src.services.parsing import extract_skills
    
    text = """
    Professional Python and JavaScript developer with 5+ years of experience.
    Expert in Django, Flask, and FastAPI frameworks.
    Experience with AWS, Docker, and Kubernetes.
    """
    
    skills = extract_skills(text)
    
    assert "python" in skills
    assert "javascript" in skills
    assert "django" in skills
    assert "aws" in skills


def test_parse_experience_level():
    """Test experience level extraction."""
    from src.services.parsing import extract_experience_level
    
    text1 = "I have 1 year of software development experience"
    text2 = "5+ years of professional experience"
    text3 = "15 years in the industry"
    
    level1 = extract_experience_level(text1)
    level2 = extract_experience_level(text2)
    level3 = extract_experience_level(text3)
    
    assert level1 == "Entry Level"
    assert level2 == "Mid Level"
    assert level3 == "Lead/Principal"
