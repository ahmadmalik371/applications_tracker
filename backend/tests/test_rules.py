import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Rule, Candidate, Job
from src.services.rules import RuleEvaluationService
import uuid


@pytest.fixture
def rule_service():
    return RuleEvaluationService()


@pytest.mark.asyncio
async def test_experience_rule_greater_than(rule_service: RuleEvaluationService, session: AsyncSession):
    """Test experience rule with greater than operator."""
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data={
            "experience": [
                {"title": "Senior Engineer", "duration": "5 years"}
            ]
        }
    )
    
    rule = Rule(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        name="Minimum 3 years experience",
        rule_type="experience",
        operator="greater_than",
        condition_value={"years": 3},
        score_impact=10,
        is_blocking=False,
    )
    
    job = Job(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        title="Senior Position",
    )
    
    passed, reason, score_impact = await rule_service.evaluate_rule(session, rule, candidate, job)
    assert passed is True
    assert score_impact == 10


@pytest.mark.asyncio
async def test_skills_rule_contains(rule_service: RuleEvaluationService, session: AsyncSession):
    """Test skills rule with contains operator."""
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]
        }
    )
    
    rule = Rule(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        name="Must have Python",
        rule_type="skills",
        operator="contains",
        condition_value={"skills": ["Python"]},
        score_impact=15,
        is_blocking=True,
    )
    
    job = Job(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        title="Backend Engineer",
    )
    
    passed, reason, score_impact = await rule_service.evaluate_rule(session, rule, candidate, job)
    assert passed is True
    assert score_impact == 15


@pytest.mark.asyncio
async def test_skills_rule_missing(rule_service: RuleEvaluationService, session: AsyncSession):
    """Test skills rule when required skill is missing."""
    candidate = Candidate(
        id=uuid.uuid4(),
        email="test@example.com",
        organization_id=uuid.uuid4(),
        parsed_data={
            "skills": ["JavaScript", "React"]
        }
    )
    
    rule = Rule(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        name="Must have Python",
        rule_type="skills",
        operator="contains",
        condition_value={"skills": ["Python"]},
        score_impact=15,
        is_blocking=True,
    )
    
    job = Job(
        id=uuid.uuid4(),
        organization_id=candidate.organization_id,
        title="Backend Engineer",
    )
    
    passed, reason, score_impact = await rule_service.evaluate_rule(session, rule, candidate, job)
    assert passed is False
    assert score_impact == 0
