import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Candidate, Job
from src.services.ai_assistant import ai_assistant_service


@pytest.fixture
def sample_parsed_data():
    return {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "React"],
        "experience": [{"title": "Senior Engineer", "duration": "5 years"}],
        "education": [{"degree": "BSc Computer Science"}],
        "summary": "Experienced backend engineer.",
    }


@pytest.mark.asyncio
async def test_resume_summarization(sample_parsed_data):
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data=sample_parsed_data,
    )
    summary = await ai_assistant_service.summarize_resume(candidate)
    assert "professional_summary" in summary
    assert "Python" in summary["skills"]
    assert len(summary["strengths"]) > 0


@pytest.mark.asyncio
async def test_resume_summarization_caching(sample_parsed_data):
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data={**sample_parsed_data, "_summary_cache_key": "stub"},
    )
    summary = await ai_assistant_service.summarize_resume(candidate)
    assert summary["professional_summary"] == "Experienced backend engineer."


@pytest.mark.asyncio
async def test_jd_analysis_missing_skills_section():
    job = Job(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Engineer",
        description="We need someone awesome.",
    )
    analysis = await ai_assistant_service.analyze_job_description(job)
    assert "missing_skills_section" in analysis["issues"]
    assert analysis["score"] < 100


@pytest.mark.asyncio
async def test_jd_analysis_non_inclusive_language():
    job = Job(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Engineer",
        description="We are looking for a rockstar ninja. Requirements: Python. 5 years experience. Salary: $100k.",
    )
    analysis = await ai_assistant_service.analyze_job_description(job)
    assert "non_inclusive_language" in analysis["issues"]


@pytest.mark.asyncio
async def test_interview_question_generation():
    job = Job(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Backend Engineer",
        description="Python, FastAPI, PostgreSQL",
    )
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=job.organization_id,
        parsed_data={"skills": ["Python", "FastAPI"]},
    )
    questions = await ai_assistant_service.generate_interview_questions(
        job, candidate, seniority="senior"
    )
    assert "technical" in questions
    assert "behavioral" in questions
    assert "leadership" in questions
    assert "problem_solving" in questions
    assert any("Python" in q for q in questions["technical"])


@pytest.mark.asyncio
async def test_skill_gap_analysis():
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data={"skills": ["Python", "FastAPI", "React"]},
    )
    job = Job(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        title="Full Stack Engineer",
        description="We need Python, FastAPI, PostgreSQL, Docker, AWS",
    )
    analysis = await ai_assistant_service.analyze_skill_gap(candidate, job)
    assert "python" in analysis["strong_skills"]
    assert "docker" in analysis["missing_skills"]
    assert 0 <= analysis["readiness_score"] <= 100
    assert len(analysis["learning_suggestions"]) > 0
