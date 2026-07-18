import pytest
import uuid
from src.models import Candidate, Job
from src.services.explainability import ExplainabilityService


@pytest.fixture
def explainability_service():
    return ExplainabilityService()


@pytest.fixture
def strong_match_candidate():
    """Create a candidate with strong match profile."""
    return Candidate(
        id=uuid.uuid4(),
        email="senior@example.com",
        first_name="Jane",
        last_name="Smith",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Kubernetes"],
            "experience": [
                {"title": "Senior Engineer", "company": "Google", "duration": "5 years"},
                {"title": "Engineer", "company": "StartupY", "duration": "3 years"},
            ],
            "education": [{"degree": "Master of Science in Computer Science"}],
            "location": "San Francisco, CA",
        },
    )


@pytest.fixture
def weak_match_candidate():
    """Create a candidate with weak match profile."""
    return Candidate(
        id=uuid.uuid4(),
        email="junior@example.com",
        first_name="Bob",
        last_name="Jones",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["HTML", "CSS", "JavaScript"],
            "experience": [
                {"title": "Junior Developer", "company": "SmallCo", "duration": "1 year"},
            ],
            "education": [{"degree": "Bachelor of Science in Computer Science"}],
            "location": "New York, NY",
        },
    )


@pytest.fixture
def senior_job():
    """Create a senior position job posting."""
    return Job(
        id=uuid.uuid4(),
        title="Senior Backend Engineer",
        description="Looking for a Senior Backend Engineer with 5+ years of experience. Must have Python, FastAPI, PostgreSQL. AWS, Docker, and Kubernetes are required.",
        location="San Francisco, CA",
        organization_id=uuid.uuid4(),
        is_published=True,
    )


@pytest.mark.asyncio
async def test_generate_explanation_strong_match(
    explainability_service: ExplainabilityService,
    strong_match_candidate: Candidate,
    senior_job: Job,
):
    """Test explanation generation for strong match."""
    score_data = {
        "match_score": 85.5,
        "confidence": 0.9,
        "features": {
            "experience_match": 0.9,
            "skills_match": 0.95,
            "education_match": 0.85,
            "location_match": 1.0,
            "experience_recency": 0.9,
            "skill_diversity": 0.8,
            "education_level": 0.9,
        },
        "embedding_similarity": 0.85,
        "breakdown": {},
    }

    explanation = await explainability_service.generate_explanation(
        strong_match_candidate, senior_job, score_data
    )

    assert "summary" in explanation
    assert explanation["match_score"] == 85.5
    assert explanation["confidence"] == 0.9
    assert len(explanation["strengths"]) > 0
    assert "Excellent match" in explanation["summary"]


@pytest.mark.asyncio
async def test_generate_explanation_weak_match(
    explainability_service: ExplainabilityService,
    weak_match_candidate: Candidate,
    senior_job: Job,
):
    """Test explanation generation for weak match."""
    score_data = {
        "match_score": 35.0,
        "confidence": 0.5,
        "features": {
            "experience_match": 0.2,
            "skills_match": 0.3,
            "education_match": 0.6,
            "location_match": 0.2,
            "experience_recency": 0.5,
            "skill_diversity": 0.3,
            "education_level": 0.7,
        },
        "embedding_similarity": 0.4,
        "breakdown": {},
    }

    explanation = await explainability_service.generate_explanation(
        weak_match_candidate, senior_job, score_data
    )

    assert len(explanation["weaknesses"]) > 0
    assert explanation["match_score"] == 35.0


@pytest.mark.asyncio
async def test_skill_analysis(
    explainability_service: ExplainabilityService,
    strong_match_candidate: Candidate,
    senior_job: Job,
):
    """Test skill analysis generation."""
    score_data = {
        "match_score": 80.0,
        "confidence": 0.8,
        "features": {},
        "embedding_similarity": 0.8,
        "breakdown": {},
    }

    explanation = await explainability_service.generate_explanation(
        strong_match_candidate, senior_job, score_data
    )

    skill_analysis = explanation["skill_analysis"]
    assert "matched" in skill_analysis
    assert "missing" in skill_analysis
    assert "bonus" in skill_analysis


@pytest.mark.asyncio
async def test_recommendations_high_match(
    explainability_service: ExplainabilityService,
    strong_match_candidate: Candidate,
    senior_job: Job,
):
    """Test recommendations for high match."""
    explanation = await explainability_service.generate_explanation(
        strong_match_candidate,
        senior_job,
        {
            "match_score": 85.0,
            "confidence": 0.9,
            "features": {},
            "embedding_similarity": 0.85,
            "breakdown": {},
        },
    )

    recommendations = explanation["recommendations"]
    assert any("interview" in r.lower() for r in recommendations)
    assert len(recommendations) > 0


@pytest.mark.asyncio
async def test_next_steps(
    explainability_service: ExplainabilityService,
    strong_match_candidate: Candidate,
    senior_job: Job,
):
    """Test next steps generation."""
    explanation = await explainability_service.generate_explanation(
        strong_match_candidate,
        senior_job,
        {
            "match_score": 80.0,
            "confidence": 0.8,
            "features": {},
            "embedding_similarity": 0.8,
            "breakdown": {},
        },
    )

    next_steps = explanation["next_steps"]
    assert isinstance(next_steps, list)
    assert len(next_steps) > 0
