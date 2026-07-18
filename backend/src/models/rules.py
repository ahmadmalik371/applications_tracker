import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, UUID, DateTime, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


class RuleType(str, Enum):
    """Enumeration of rule types for screening candidates."""
    EXPERIENCE = "experience"
    SKILLS = "skills"
    EDUCATION = "education"
    LOCATION = "location"
    SENIORITY = "seniority"
    CUSTOM = "custom"


class RuleOperator(str, Enum):
    """Enumeration of operators for rule conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


class Rule(Base):
    """Model for configurable hiring rules per organization."""
    
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    rule_type = Column(String(50), nullable=False)  # RuleType enum
    operator = Column(String(50), nullable=False)  # RuleOperator enum
    condition_value = Column(JSON, nullable=False)  # Flexible JSON for different rule types
    score_impact = Column(Integer, default=0)  # Score impact if rule passes or fails
    is_blocking = Column(Boolean, default=False)  # Whether rule failure blocks candidate
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Execution order
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    organization = relationship("Organization", backref="rules")
    created_by = relationship("User", backref="created_rules")

    def __repr__(self):
        return f"<Rule {self.id}: {self.name}>"


class RuleEvaluation(Base):
    """Model for tracking rule evaluation results on candidates."""
    
    __tablename__ = "rule_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    passed = Column(Boolean, nullable=False)
    reason = Column(String(500), nullable=True)
    score_impact = Column(Integer, default=0)
    
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rule = relationship("Rule", backref="evaluations")
    candidate = relationship("Candidate", backref="rule_evaluations")
    job = relationship("Job", backref="rule_evaluations")

    def __repr__(self):
        return f"<RuleEvaluation {self.id}: rule={self.rule_id} passed={self.passed}>"
