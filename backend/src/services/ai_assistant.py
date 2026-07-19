"""AI Assistant Architecture

This module defines the AI Assistant service layer that orchestrates multiple
AI capabilities used throughout the ATS platform. Each capability is implemented
as a dedicated method on the AIAssistantService class:

    - search_candidates: Natural-language candidate search
    - summarize_resume: Resume summarization with caching
    - analyze_job_description: JD quality analysis with improvement suggestions
    - generate_interview_questions: Question generation across categories
    - analyze_skill_gap: Candidate-vs-job skill gap analysis
    - compare_candidates: AI-assisted candidate comparison

The architecture is model-agnostic: the service accepts candidate/job objects and
returns structured dictionaries. In production, each method would delegate to an
LLM provider (OpenAI, HuggingFace, etc.); the current implementation uses
deterministic heuristics so the system is fully testable without external API keys.

See docs/ARCHITECTURE.md for the full component diagram.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Candidate, Job
from src.services.embedding import EmbeddingService
from src.services.features import FeatureExtractor


class AIAssistantService:
    """Orchestrator for AI assistant capabilities."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.feature_extractor = FeatureExtractor()

    # ------------------------------------------------------------------
    # Capability: Search
    # ------------------------------------------------------------------
    async def search_candidates(
        self,
        session: AsyncSession,
        query: str,
        organization_id: Any,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Natural-language candidate search.

        Delegates to the hybrid search service for keyword + semantic matching.
        """
        from src.services.search import hybrid_search_candidates

        results = await hybrid_search_candidates(
            session, query, organization_id, limit=limit
        )
        return results

    # ------------------------------------------------------------------
    # Capability: Resume Summarization (Task 8)
    # ------------------------------------------------------------------
    async def summarize_resume(
        self,
        candidate: Candidate,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """Generate a structured resume summary with caching.

        The cache key is derived from the candidate's parsed_data hash so that
        summaries are only regenerated when the underlying resume changes, or
        when force_regenerate is True.
        """
        parsed = candidate.parsed_data or {}
        cache_key = self._summary_cache_key(candidate.id, parsed)

        if not force_regenerate and candidate.parsed_data and parsed.get("_summary_cache_key") == cache_key:
            cached = parsed.get("_summary")
            if cached:
                return cached

        summary = self._build_resume_summary(parsed)
        summary["_summary_cache_key"] = cache_key
        return summary

    def _build_resume_summary(self, parsed: dict) -> Dict[str, Any]:
        skills = parsed.get("skills", [])
        experience = parsed.get("experience", [])
        education = parsed.get("education", [])
        summary_text = parsed.get("summary", "")

        highlights: List[str] = []
        if skills:
            highlights.append(f"Skilled in {', '.join(skills[:5])}")
        if experience:
            top = experience[0] if isinstance(experience, list) else None
            if isinstance(top, dict) and top.get("title"):
                highlights.append(f"Most recent role: {top.get('title')}")
        if education:
            edu = education[0] if isinstance(education, list) else None
            if isinstance(edu, dict) and edu.get("degree"):
                highlights.append(f"Holds a {edu.get('degree')}")

        strengths = [s for s in skills[:3]] if skills else []
        weaknesses: List[str] = []
        if not skills:
            weaknesses.append("No skills listed")
        if not experience:
            weaknesses.append("No experience entries")
        if not education:
            weaknesses.append("No education entries")

        return {
            "professional_summary": summary_text or "No summary provided.",
            "highlights": highlights,
            "skills": skills,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

    @staticmethod
    def _summary_cache_key(candidate_id: Any, parsed: dict) -> str:
        raw = json.dumps(parsed, sort_keys=True, default=str)
        return hashlib.sha256(f"{candidate_id}:{raw}".encode()).hexdigest()

    # ------------------------------------------------------------------
    # Capability: Job Description Analysis (Task 9)
    # ------------------------------------------------------------------
    async def analyze_job_description(self, job: Job) -> Dict[str, Any]:
        """Analyze a JD for missing skills, duplicates, readability, inclusive
        language, and experience/salary checks. Returns improvement suggestions."""
        text = (job.description or "").lower()
        issues: List[str] = []
        suggestions: List[str] = []

        # Missing skills section
        if "requirements" not in text and "qualifications" not in text and "skills" not in text:
            issues.append("missing_skills_section")
            suggestions.append("Add a clear 'Requirements' or 'Skills' section.")

        # Duplicate phrases (simple check)
        words = text.split()
        if len(words) > 0:
            from collections import Counter
            dupes = [w for w, c in Counter(words).items() if c > 5 and len(w) > 4]
            if dupes:
                issues.append("duplicate_phrases")
                suggestions.append(f"Reduce repetition of: {', '.join(dupes[:3])}.")

        # Readability (rough word/sentence ratio)
        sentences = max(text.count(".") + text.count("!") + text.count("?"), 1)
        words_per_sentence = len(words) / sentences
        if words_per_sentence > 25:
            issues.append("low_readability")
            suggestions.append("Use shorter sentences to improve readability.")

        # Inclusive language check
        non_inclusive = ["rockstar", "ninja", "guru", "young", "recent graduate"]
        found_biased = [w for w in non_inclusive if w in text]
        if found_biased:
            issues.append("non_inclusive_language")
            suggestions.append(f"Replace biased terms: {', '.join(found_biased)}.")

        # Experience / salary checks
        if "years" not in text and "experience" not in text:
            issues.append("missing_experience_requirement")
            suggestions.append("Specify required years of experience.")
        if "salary" not in text and "compensation" not in text:
            issues.append("missing_salary_info")
            suggestions.append("Include salary range or compensation info to attract diverse candidates.")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "readability": {"words_per_sentence": round(words_per_sentence, 1)},
            "score": max(0, 100 - len(issues) * 15),
        }

    # ------------------------------------------------------------------
    # Capability: Interview Question Generation (Task 10)
    # ------------------------------------------------------------------
    async def generate_interview_questions(
        self,
        job: Job,
        candidate: Optional[Candidate] = None,
        seniority: str = "mid",
        count: int = 10,
    ) -> Dict[str, List[str]]:
        """Generate interview questions across four categories."""
        parsed = candidate.parsed_data or {} if candidate else {}
        skills = parsed.get("skills", [])
        job_title = job.title or "the role"

        technical: List[str] = []
        for skill in skills[:5]:
            technical.append(f"Describe your experience with {skill}.")
        technical.append(f"How would you approach the main responsibilities of {job_title}?")

        behavioral = [
            "Tell me about a time you faced a significant challenge at work.",
            "Describe a situation where you had a conflict with a teammate.",
            "Give an example of a goal you set and how you achieved it.",
        ]

        leadership = [
            "Describe a project you led from start to finish.",
            "How do you prioritize tasks when everything seems urgent?",
        ]
        if seniority in ("senior", "lead"):
            leadership.append("How do you mentor junior team members?")

        problem_solving = [
            "Walk me through how you debug a complex production issue.",
            "How would you design a system to handle 10x current traffic?",
        ]

        return {
            "technical": technical[:count],
            "behavioral": behavioral,
            "leadership": leadership,
            "problem_solving": problem_solving,
        }

    # ------------------------------------------------------------------
    # Capability: Skill Gap Analysis (Task 11)
    # ------------------------------------------------------------------
    async def analyze_skill_gap(
        self,
        candidate: Candidate,
        job: Job,
    ) -> Dict[str, Any]:
        """Compare candidate skills against job requirements."""
        parsed = candidate.parsed_data or {}
        candidate_skills = {s.lower() for s in parsed.get("skills", [])}

        job_skills = set()
        if job.description:
            import re
            common_skills = [
                "python", "java", "javascript", "typescript", "react", "node",
                "sql", "postgresql", "docker", "kubernetes", "aws", "fastapi",
                "django", "flask", "git", "linux", "go", "rust", "c++",
            ]
            desc_lower = job.description.lower()
            job_skills = {s for s in common_skills if s in desc_lower}

        missing = job_skills - candidate_skills
        strong = candidate_skills & job_skills
        extra = candidate_skills - job_skills

        if job_skills:
            readiness = round(len(strong) / len(job_skills) * 100, 1)
        else:
            readiness = 100.0

        suggestions = [f"Consider learning {s}." for s in sorted(missing)]

        return {
            "missing_skills": sorted(missing),
            "strong_skills": sorted(strong),
            "extra_skills": sorted(extra),
            "readiness_score": readiness,
            "learning_suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # Capability: Candidate Comparison
    # ------------------------------------------------------------------
    async def compare_candidates(
        self,
        candidates: List[Candidate],
        job: Job,
    ) -> Dict[str, Any]:
        """AI-assisted comparison of multiple candidates for a job."""
        from src.services.ranking import RankingService

        ranking_service = RankingService()
        rows = []
        for candidate in candidates:
            score_data = await ranking_service.calculate_match_score(candidate, job)
            summary = self._build_resume_summary(candidate.parsed_data or {})
            rows.append({
                "candidate_id": str(candidate.id),
                "candidate_name": f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                "match_score": score_data["match_score"],
                "confidence": score_data["confidence"],
                "strengths": summary.get("strengths", []),
                "weaknesses": summary.get("weaknesses", []),
            })
        rows.sort(key=lambda x: x["match_score"], reverse=True)
        return {"job_id": str(job.id), "job_title": job.title, "candidates": rows}


ai_assistant_service = AIAssistantService()
