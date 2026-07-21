import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import Candidate, Job, Rule, User
from src.services.rules import RuleEvaluationService

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])
rule_service = RuleEvaluationService()


# Pydantic schemas
class RuleCreate(BaseModel):
    name: str
    description: str | None = None
    rule_type: str  # RuleType
    operator: str  # RuleOperator
    condition_value: dict
    score_impact: int = 0
    is_blocking: bool = False
    priority: int = 0


class RuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    operator: str | None = None
    condition_value: dict | None = None
    score_impact: int | None = None
    is_blocking: bool | None = None
    priority: int | None = None
    is_active: bool | None = None


class RuleResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None
    rule_type: str
    operator: str
    condition_value: dict
    score_impact: int
    is_blocking: bool
    is_active: bool
    priority: int

    class Config:
        from_attributes = True


class CandidateRuleEvaluationResponse(BaseModel):
    overall_passed: bool
    blocking_rules_failed: list[str]
    total_score_impact: int
    rules_passed: int
    rules_failed: int
    details: list[dict]


# Endpoints
@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a new rule for the organization."""
    # Permission check: user must be admin or recruiter
    if current_user.role not in ["admin", "recruiter"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    rule = Rule(
        organization_id=current_user.organization_id,
        name=rule_data.name,
        description=rule_data.description,
        rule_type=rule_data.rule_type,
        operator=rule_data.operator,
        condition_value=rule_data.condition_value,
        score_impact=rule_data.score_impact,
        is_blocking=rule_data.is_blocking,
        priority=rule_data.priority,
        created_by_id=current_user.id,
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.get("", response_model=list[RuleResponse])
async def list_rules(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all rules for the organization."""
    result = await session.execute(
        select(Rule)
        .where(Rule.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
    )
    rules = result.scalars().all()
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get a specific rule."""
    result = await session.execute(
        select(Rule)
        .where(Rule.id == rule_id)
        .where(Rule.organization_id == current_user.organization_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    rule_data: RuleUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update a rule."""
    result = await session.execute(
        select(Rule)
        .where(Rule.id == rule_id)
        .where(Rule.organization_id == current_user.organization_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(rule, key, value)

    await session.commit()
    await session.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Delete a rule."""
    result = await session.execute(
        select(Rule)
        .where(Rule.id == rule_id)
        .where(Rule.organization_id == current_user.organization_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    await session.delete(rule)
    await session.commit()


@router.post(
    "/evaluate/candidate/{candidate_id}/job/{job_id}",
    response_model=CandidateRuleEvaluationResponse,
)
async def evaluate_candidate_against_job(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Evaluate all organization rules against a candidate for a specific job."""
    # Fetch candidate and job
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_result = await session.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.organization_id == current_user.organization_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Evaluate
    evaluation_result = await rule_service.evaluate_candidate_against_job(
        session, candidate, job, current_user.organization_id
    )
    await session.commit()
    return evaluation_result
