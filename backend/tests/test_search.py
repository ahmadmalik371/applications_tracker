import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from src.services.search import hybrid_search_candidates


@pytest.mark.asyncio
async def test_hybrid_search_empty_query():
    """Empty query returns no results."""
    session = MagicMock()
    result = await hybrid_search_candidates(session, "", uuid.uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_hybrid_search_keyword_match(monkeypatch):
    """Hybrid search returns candidates matching keyword terms."""
    from src.models import Candidate

    candidate = MagicMock(spec=Candidate)
    candidate.id = uuid.uuid4()
    candidate.first_name = "Alice"
    candidate.last_name = "Smith"
    candidate.email = "alice@example.com"
    candidate.status = "New"
    candidate.embedded = None
    candidate.parsed_data = {
        "skills": ["Python", "FastAPI"],
        "experience": [{"title": "Engineer", "company": "Corp", "duration": "3 years"}],
        "education": [{"degree": "BSc CS"}],
        "location": "San Francisco",
    }

    scalars = MagicMock()
    scalars.all.return_value = [candidate]
    result = MagicMock()
    result.scalars.return_value = scalars
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)

    results = await hybrid_search_candidates(session, "python", uuid.uuid4())

    assert len(results) == 1
    assert results[0]["candidate_name"] == "Alice Smith"
    assert results[0]["keyword_score"] > 0
    assert "Python" in results[0]["skills"]


@pytest.mark.asyncio
async def test_hybrid_search_no_match():
    """Candidates not matching the query are excluded."""
    from src.models import Candidate

    candidate = MagicMock(spec=Candidate)
    candidate.id = uuid.uuid4()
    candidate.first_name = "Bob"
    candidate.last_name = "Jones"
    candidate.email = "bob@example.com"
    candidate.status = "New"
    candidate.embedded = None
    candidate.parsed_data = {"skills": ["Java"], "experience": [], "education": [], "location": ""}

    scalars = MagicMock()
    scalars.all.return_value = [candidate]
    result = MagicMock()
    result.scalars.return_value = scalars
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)

    results = await hybrid_search_candidates(session, "python rust", uuid.uuid4())
    assert len(results) == 0
