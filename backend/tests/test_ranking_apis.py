import pytest
import uuid
from src.models import Candidate, Job
from src.services.ranking import RankingService


@pytest.fixture
def ranking_service():
    return RankingService()


@pytest.fixture
def job_id():
    return uuid.uuid4()


@pytest.fixture
def org_id():
    return uuid.uuid4()


@pytest.fixture
def candidate_a():
    return Candidate(
        id=uuid.uuid4(),
        email="a@example.com",
        first_name="Alice",
        last_name="Anderson",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience": [{"title": "Engineer", "duration": "4 years"}],
            "education": [{"degree": "Bachelor of Science in CS"}],
            "location": "San Francisco, CA",
        },
    )


@pytest.fixture
def candidate_b():
    return Candidate(
        id=uuid.uuid4(),
        email="b@example.com",
        first_name="Bob",
        last_name="Brown",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["HTML", "CSS"],
            "experience": [{"title": "Intern", "duration": "1 year"}],
            "education": [{"degree": "Bachelor of Arts"}],
            "location": "New York, NY",
        },
    )


def test_export_rankings_csv(ranking_service, candidate_a, candidate_b):
    """CSV export produces a header row and one row per candidate."""
    ranked = [
        {"candidate_id": str(candidate_a.id), "match_score": 80.0},
        {"candidate_id": str(candidate_b.id), "match_score": 40.0},
    ]
    csv_out = RankingService.export_rankings(ranked, fmt="csv")
    assert "candidate_id" in csv_out
    assert str(candidate_a.id) in csv_out
    assert "80.0" in csv_out


def test_export_rankings_json(ranking_service, candidate_a):
    """JSON export returns valid JSON with the candidate data."""
    ranked = [{"candidate_id": str(candidate_a.id), "match_score": 80.0}]
    json_out = RankingService.export_rankings(ranked, fmt="json")
    assert str(candidate_a.id) in json_out
    assert "match_score" in json_out


def test_export_rankings_empty(ranking_service):
    """Exporting an empty list returns an empty string."""
    assert RankingService.export_rankings([], fmt="csv") == ""


@pytest.mark.asyncio
async def test_filter_ranked_candidates_min_score(
    ranking_service, candidate_a, candidate_b, job_id, org_id, monkeypatch
):
    """filter_ranked_candidates honors the min_score threshold."""
    async def fake_rank(self, session, jid, oid, limit=100):
        return [
            {"candidate_id": str(candidate_a.id), "match_score": 80.0, "features": {"skills": ["python"]}},
            {"candidate_id": str(candidate_b.id), "match_score": 40.0, "features": {"skills": ["html"]}},
        ]
    monkeypatch.setattr(RankingService, "rank_candidates_for_job", fake_rank)

    result = await ranking_service.filter_ranked_candidates(
        session=None, job_id=job_id, organization_id=org_id, min_score=60.0
    )
    assert len(result) == 1
    assert result[0]["match_score"] == 80.0


@pytest.mark.asyncio
async def test_filter_ranked_candidates_required_skills(
    ranking_service, candidate_a, candidate_b, job_id, org_id, monkeypatch
):
    """filter_ranked_candidates filters by required skills."""
    async def fake_rank(self, session, jid, oid, limit=100):
        return [
            {"candidate_id": str(candidate_a.id), "match_score": 80.0, "features": {"skills": ["python", "fastapi"]}},
            {"candidate_id": str(candidate_b.id), "match_score": 40.0, "features": {"skills": ["html"]}},
        ]
    monkeypatch.setattr(RankingService, "rank_candidates_for_job", fake_rank)

    result = await ranking_service.filter_ranked_candidates(
        session=None, job_id=job_id, organization_id=org_id, required_skills=["python"]
    )
    assert len(result) == 1
    assert result[0]["candidate_id"] == str(candidate_a.id)
