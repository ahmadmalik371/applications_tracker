import pytest
import uuid
from src.models import Candidate, Job
from src.services.features import FeatureExtractor
from src.services.ranking import RankingService


@pytest.fixture
def feature_extractor():
    return FeatureExtractor()


@pytest.fixture
def ranking_service():
    return RankingService()


@pytest.fixture
def sample_candidate():
    """Create a sample candidate with parsed data."""
    return Candidate(
        id=uuid.uuid4(),
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration": "3 years",
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupX",
                    "duration": "2 years",
                },
            ],
            "education": [
                {"degree": "Bachelor of Science in Computer Science"}
            ],
            "location": "San Francisco, CA",
        },
    )


@pytest.fixture
def sample_job():
    """Create a sample job posting."""
    return Job(
        id=uuid.uuid4(),
        title="Senior Backend Engineer",
        description="Looking for a Senior Backend Engineer with 5+ years of experience. Must have Python, FastAPI, and PostgreSQL experience. AWS and Docker are nice to have.",
        location="San Francisco, CA",
        organization_id=uuid.uuid4(),
        is_published=True,
    )


def test_experience_match_within_range(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test experience match calculation."""
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert "experience_match" in features
    assert 0 <= features["experience_match"] <= 1


def test_skills_match_high(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test skills match when candidate has required skills."""
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert "skills_match" in features
    assert features["skills_match"] > 0.5  # Should be high match


def test_location_match(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test location match when candidate and job are in same location."""
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert "location_match" in features
    assert features["location_match"] == 1.0  # Perfect match


def test_location_mismatch(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test location mismatch penalty."""
    sample_job.location = "New York, NY"
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert features["location_match"] < 1.0


def test_education_level(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test education level extraction."""
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert "education_level" in features
    assert features["education_level"] > 0  # Should have some education


def test_skill_diversity(
    feature_extractor: FeatureExtractor,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test skill diversity calculation."""
    features = feature_extractor.extract_candidate_features(sample_candidate, sample_job)
    assert "skill_diversity" in features
    # Candidate has 5 skills, so should be 5/10 = 0.5
    assert features["skill_diversity"] == 0.5


@pytest.mark.asyncio
async def test_calculate_match_score(
    ranking_service: RankingService,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test overall match score calculation."""
    score_data = await ranking_service.calculate_match_score(sample_candidate, sample_job)
    
    assert "match_score" in score_data
    assert "confidence" in score_data
    assert "features" in score_data
    assert "embedding_similarity" in score_data
    
    assert 0 <= score_data["match_score"] <= 100
    assert 0 <= score_data["confidence"] <= 1


@pytest.mark.asyncio
async def test_match_score_reasonable_range(
    ranking_service: RankingService,
    sample_candidate: Candidate,
    sample_job: Job,
):
    """Test that match score is in reasonable range for well-matched pair."""
    score_data = await ranking_service.calculate_match_score(sample_candidate, sample_job)
    
    # Candidate should have high match with this job (same location, has required skills)
    assert score_data["match_score"] > 50  # At least moderate match
