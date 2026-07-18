import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.rules import Rule, RuleEvaluation, RuleOperator, RuleType
from src.models import Candidate, Job
from src.services.parsing import extract_years_of_experience


class RuleEvaluationService:
    """Service for evaluating business rules against candidates."""

    async def evaluate_rule(
        self,
        session: AsyncSession,
        rule: Rule,
        candidate: Candidate,
        job: Job,
    ) -> tuple[bool, str, int]:
        """
        Evaluate a single rule against a candidate.
        
        Returns: (passed: bool, reason: str, score_impact: int)
        """
        try:
            passed = await self._evaluate_condition(rule, candidate, job)
            reason = self._generate_reason(rule, candidate, passed)
            
            # Create evaluation record
            evaluation = RuleEvaluation(
                rule_id=rule.id,
                candidate_id=candidate.id,
                job_id=job.id,
                passed=passed,
                reason=reason,
                score_impact=rule.score_impact if passed else 0,
            )
            session.add(evaluation)
            await session.flush()
            
            return passed, reason, rule.score_impact if passed else 0
        except Exception as e:
            return False, f"Rule evaluation error: {str(e)}", 0

    async def evaluate_candidate_against_job(
        self,
        session: AsyncSession,
        candidate: Candidate,
        job: Job,
        organization_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Evaluate all active rules for an organization against a candidate for a job.
        
        Returns:
        {
            "overall_passed": bool,
            "blocking_rules_failed": List[str],
            "total_score_impact": int,
            "rules_passed": int,
            "rules_failed": int,
            "details": [{"rule_name": str, "passed": bool, "reason": str, "score_impact": int}]
        }
        """
        result = await session.execute(
            select(Rule)
            .where(Rule.organization_id == organization_id)
            .where(Rule.is_active == True)
            .order_by(Rule.priority)
        )
        rules = result.scalars().all()

        overall_passed = True
        blocking_rules_failed = []
        total_score_impact = 0
        rules_passed = 0
        rules_failed = 0
        details = []

        for rule in rules:
            passed, reason, score_impact = await self.evaluate_rule(
                session, rule, candidate, job
            )
            
            if passed:
                rules_passed += 1
                total_score_impact += score_impact
            else:
                rules_failed += 1
                if rule.is_blocking:
                    blocking_rules_failed.append(rule.name)
                    overall_passed = False

            details.append({
                "rule_id": str(rule.id),
                "rule_name": rule.name,
                "passed": passed,
                "reason": reason,
                "score_impact": score_impact,
                "is_blocking": rule.is_blocking,
            })

        return {
            "overall_passed": overall_passed and len(blocking_rules_failed) == 0,
            "blocking_rules_failed": blocking_rules_failed,
            "total_score_impact": total_score_impact,
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "details": details,
        }

    async def _evaluate_condition(
        self, rule: Rule, candidate: Candidate, job: Job
    ) -> bool:
        """Evaluate a single rule condition."""
        rule_type = rule.rule_type
        operator = rule.operator
        condition_value = rule.condition_value

        if rule_type == RuleType.EXPERIENCE:
            return self._evaluate_experience(candidate, operator, condition_value)
        elif rule_type == RuleType.SKILLS:
            return self._evaluate_skills(candidate, operator, condition_value)
        elif rule_type == RuleType.EDUCATION:
            return self._evaluate_education(candidate, operator, condition_value)
        elif rule_type == RuleType.LOCATION:
            return self._evaluate_location(candidate, job, operator, condition_value)
        elif rule_type == RuleType.SENIORITY:
            return self._evaluate_seniority(candidate, operator, condition_value)
        else:
            return True  # Unknown rule type passes by default

    def _evaluate_experience(
        self, candidate: Candidate, operator: str, condition_value: Dict[str, Any]
    ) -> bool:
        """Evaluate experience-based rules."""
        if not candidate.parsed_data:
            return False

        candidate_experience = extract_years_of_experience(
            candidate.parsed_data.get("experience", [])
        )
        required_years = condition_value.get("years", 0)

        if operator == RuleOperator.GREATER_THAN:
            return candidate_experience >= required_years
        elif operator == RuleOperator.LESS_THAN:
            return candidate_experience <= required_years
        elif operator == RuleOperator.EQUALS:
            return candidate_experience == required_years
        else:
            return False

    def _evaluate_skills(
        self, candidate: Candidate, operator: str, condition_value: Dict[str, Any]
    ) -> bool:
        """Evaluate skill-based rules."""
        if not candidate.parsed_data:
            return False

        candidate_skills = [
            s.lower() for s in candidate.parsed_data.get("skills", [])
        ]
        required_skills = [s.lower() for s in condition_value.get("skills", [])]

        if operator == RuleOperator.CONTAINS:
            return any(skill in candidate_skills for skill in required_skills)
        elif operator == RuleOperator.IN:
            return all(skill in candidate_skills for skill in required_skills)
        elif operator == RuleOperator.NOT_CONTAINS:
            return not any(skill in candidate_skills for skill in required_skills)
        else:
            return False

    def _evaluate_education(
        self, candidate: Candidate, operator: str, condition_value: Dict[str, Any]
    ) -> bool:
        """Evaluate education-based rules."""
        if not candidate.parsed_data:
            return False

        candidate_education = candidate.parsed_data.get("education", [])
        required_degree = condition_value.get("degree", "").lower()

        education_str = " ".join([str(e) for e in candidate_education]).lower()

        if operator == RuleOperator.CONTAINS:
            return required_degree in education_str
        elif operator == RuleOperator.NOT_CONTAINS:
            return required_degree not in education_str
        else:
            return False

    def _evaluate_location(
        self, candidate: Candidate, job: Job, operator: str, condition_value: Dict[str, Any]
    ) -> bool:
        """Evaluate location-based rules."""
        candidate_location = (candidate.parsed_data or {}).get("location", "").lower() if candidate.parsed_data else ""
        job_location = (job.location or "").lower()
        required_location = condition_value.get("location", "").lower()

        if operator == RuleOperator.EQUALS:
            return candidate_location == required_location
        elif operator == RuleOperator.NOT_EQUALS:
            return candidate_location != required_location
        elif operator == RuleOperator.CONTAINS:
            return required_location in candidate_location
        else:
            return False

    def _evaluate_seniority(
        self, candidate: Candidate, operator: str, condition_value: Dict[str, Any]
    ) -> bool:
        """Evaluate seniority-based rules."""
        if not candidate.parsed_data:
            return False

        seniority_map = {"junior": 1, "mid": 2, "senior": 3, "lead": 4, "principal": 5}

        candidate_exp = extract_years_of_experience(
            candidate.parsed_data.get("experience", [])
        )
        required_seniority = condition_value.get("seniority", "junior").lower()

        candidate_seniority = self._infer_seniority_from_experience(candidate_exp)
        required_level = seniority_map.get(required_seniority, 1)

        if operator == RuleOperator.EQUALS:
            return candidate_seniority == required_level
        elif operator == RuleOperator.GREATER_THAN:
            return candidate_seniority >= required_level
        elif operator == RuleOperator.LESS_THAN:
            return candidate_seniority <= required_level
        else:
            return False

    def _infer_seniority_from_experience(self, years: int) -> int:
        """Infer seniority level from years of experience."""
        if years < 2:
            return 1  # junior
        elif years < 5:
            return 2  # mid
        elif years < 10:
            return 3  # senior
        elif years < 15:
            return 4  # lead
        else:
            return 5  # principal

    def _generate_reason(self, rule: Rule, candidate: Candidate, passed: bool) -> str:
        """Generate a human-readable reason for the rule evaluation."""
        status = "passed" if passed else "failed"
        return f"Rule '{rule.name}' {status} for candidate {candidate.email}"
