from typing import Any

from src.models import Candidate, Job
from src.services.ranking import RankingService


class ExplainabilityService:
    """Service for generating explainable AI insights about match scores."""

    def __init__(self):
        self.ranking_service = RankingService()

    async def generate_explanation(
        self,
        candidate: Candidate,
        job: Job,
        score_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate human-readable explanation for a candidate-job match.

        Returns:
        {
            "summary": "...",
            "match_score": 0-100,
            "confidence": 0-1,
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "skill_analysis": {"matched": [...], "missing": [...], "bonus": [...]},
            "recommendations": ["..."],
            "next_steps": ["..."]
        }
        """
        strengths = self._identify_strengths(candidate, job, score_data)
        weaknesses = self._identify_weaknesses(candidate, job, score_data)
        skill_analysis = self._analyze_skills(candidate, job)
        recommendations = self._generate_recommendations(
            candidate, job, score_data, strengths, weaknesses
        )

        summary = self._generate_summary(score_data, strengths, weaknesses)

        return {
            "summary": summary,
            "match_score": score_data["match_score"],
            "confidence": score_data["confidence"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill_analysis": skill_analysis,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(score_data, recommendations),
        }

    def _identify_strengths(
        self, candidate: Candidate, job: Job, score_data: dict[str, Any]
    ) -> list[str]:
        """Identify candidate's strengths relative to the job."""
        strengths = []
        features = score_data.get("features", {})

        if features.get("skills_match", 0) > 0.7:
            strengths.append("Has strong match on required skills")

        if features.get("experience_match", 0) > 0.8:
            strengths.append("Experience level aligns well with role requirements")

        if features.get("location_match", 0) == 1.0:
            strengths.append("Located in the desired job location")

        if features.get("education_level", 0) > 0.7:
            strengths.append("Has strong educational background")

        if features.get("skill_diversity", 0) > 0.6:
            strengths.append("Brings diverse skill set to the role")

        if features.get("experience_recency", 0) > 0.8:
            strengths.append("Has recent, relevant work experience")

        if score_data.get("embedding_similarity", 0) > 0.7:
            strengths.append("Career trajectory matches job description semantically")

        return strengths or ["Candidate has relevant qualifications"]

    def _identify_weaknesses(
        self, candidate: Candidate, job: Job, score_data: dict[str, Any]
    ) -> list[str]:
        """Identify potential gaps or weaknesses."""
        weaknesses = []
        features = score_data.get("features", {})

        if features.get("skills_match", 0) < 0.5:
            weaknesses.append("Missing some key required skills")

        if features.get("experience_match", 0) < 0.5:
            if self._infer_candidate_experience(candidate) < self._infer_job_experience(
                job
            ):
                weaknesses.append("May be underqualified based on experience level")
            else:
                weaknesses.append("May be overqualified for this position")

        if features.get("location_match", 0) < 0.5:
            weaknesses.append("Not in preferred job location (may require relocation)")

        if features.get("education_level", 0) < 0.5:
            weaknesses.append("Education level may not meet stated requirements")

        if not candidate.parsed_data:
            weaknesses.append(
                "Resume could not be fully parsed; information may be incomplete"
            )

        if score_data.get("confidence", 0) < 0.5:
            weaknesses.append("Insufficient data to make a strong assessment")

        return weaknesses or ["No significant gaps identified"]

    def _analyze_skills(self, candidate: Candidate, job: Job) -> dict[str, list[str]]:
        """Analyze skill match in detail."""
        candidate_skills = set()
        if candidate.parsed_data:
            candidate_skills = set(
                [s.lower() for s in candidate.parsed_data.get("skills", [])]
            )

        job_description = (job.description or "").lower()

        # Extract required skills (this is a simplified version)
        required_skills = self._extract_skills_from_job(job_description)

        matched_skills = list(candidate_skills & set(required_skills))
        missing_skills = list(set(required_skills) - candidate_skills)
        bonus_skills = list(candidate_skills - set(required_skills))

        return {
            "matched": matched_skills[:5] if matched_skills else [],
            "missing": missing_skills[:3] if missing_skills else [],
            "bonus": bonus_skills[:3] if bonus_skills else [],
        }

    def _generate_recommendations(
        self,
        candidate: Candidate,
        job: Job,
        score_data: dict[str, Any],
        strengths: list[str],
        weaknesses: list[str],
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        match_score = score_data.get("match_score", 0)

        if match_score > 80:
            recommendations.append("Excellent candidate fit. Proceed with interview.")
            recommendations.append(
                "Consider this candidate for team lead consideration if applicable."
            )

        elif match_score > 60:
            recommendations.append(
                "Good candidate fit. Proceed with initial screening."
            )
            recommendations.append(
                "Consider discussing specific skill gaps in first interview."
            )

        elif match_score > 40:
            recommendations.append(
                "Fair match. Phone screen to assess potential and learning ability."
            )
            recommendations.append(
                "Verify claimed skills and recent project experience."
            )

        else:
            recommendations.append("Below threshold match. Consider for future roles.")
            recommendations.append(
                "Save for future matching when experience aligns better."
            )

        # Add specific recommendations based on weaknesses
        if any("skills" in w.lower() for w in weaknesses):
            recommendations.append(
                "Ask about willingness to quickly learn missing skills."
            )

        if any("relocation" in w.lower() for w in weaknesses):
            recommendations.append(
                "Clarify remote work options or relocation assistance."
            )

        return recommendations

    def _generate_summary(
        self, score_data: dict[str, Any], strengths: list[str], weaknesses: list[str]
    ) -> str:
        """Generate a summary statement of the match."""
        match_score = score_data.get("match_score", 0)
        confidence = score_data.get("confidence", 0)

        if match_score > 80:
            match_level = "Excellent match"
        elif match_score > 60:
            match_level = "Good match"
        elif match_score > 40:
            match_level = "Fair match"
        else:
            match_level = "Below threshold match"

        confidence_str = (
            "High confidence"
            if confidence > 0.7
            else "Moderate confidence"
            if confidence > 0.4
            else "Low confidence"
        )

        top_strength = strengths[0] if strengths else "Has relevant background"
        top_weakness = weaknesses[0] if weaknesses else "No significant gaps"

        return f"{match_level} ({match_score:.0f}/100, {confidence_str}). {top_strength}. However, {top_weakness.lower()}."

    def _generate_next_steps(
        self, score_data: dict[str, Any], recommendations: list[str]
    ) -> list[str]:
        """Generate next steps in the hiring process."""
        match_score = score_data.get("match_score", 0)
        next_steps = []

        if match_score > 75:
            next_steps.extend(
                [
                    "Schedule phone screen with recruiter",
                    "Prepare interview questions focused on technical depth",
                    "Review candidate's portfolio or GitHub",
                ]
            )

        elif match_score > 50:
            next_steps.extend(
                [
                    "Send skills assessment or technical test",
                    "Plan phone screening call",
                    "Prepare culture fit questions",
                ]
            )

        elif match_score > 25:
            next_steps.extend(
                [
                    "File for future matching",
                    "Consider if role can be modified for candidate",
                    "Check if candidate interested in different position",
                ]
            )

        else:
            next_steps.append("Pass on this candidate for this role")

        return next_steps

    def _infer_candidate_experience(self, candidate: Candidate) -> int:
        """Infer years of experience from candidate data."""
        if not candidate.parsed_data:
            return 0

        experience = candidate.parsed_data.get("experience", [])
        return len(experience) * 2  # Rough estimate: 2 years per role

    def _infer_job_experience(self, job: Job) -> int:
        """Infer required years of experience from job description."""
        job_description = (job.description or "").lower()

        import re

        pattern = r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)"
        matches = re.findall(pattern, job_description)

        if matches:
            return int(matches[0])

        return 2  # Default assumption

    def _extract_skills_from_job(self, description: str) -> list[str]:
        """Extract skill requirements from job description."""
        common_skills = [
            "python",
            "javascript",
            "typescript",
            "java",
            "csharp",
            "golang",
            "rust",
            "ruby",
            "react",
            "vue",
            "angular",
            "node",
            "express",
            "django",
            "flask",
            "fastapi",
            "postgresql",
            "mongodb",
            "redis",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "git",
            "sql",
            "api",
            "rest",
            "graphql",
        ]

        found_skills = []
        for skill in common_skills:
            if skill in description:
                found_skills.append(skill)

        return found_skills
