import math
from typing import Dict, List, Any, Optional
from src.models import Candidate, Job
from src.services.parsing import extract_years_of_experience


class FeatureExtractor:
    """Service for extracting ML features from candidates and jobs."""

    def extract_candidate_features(self, candidate: Candidate, job: Job) -> Dict[str, float]:
        """
        Extract normalized features for a candidate relative to a job.
        
        Returns a dict of feature_name -> normalized_value (0-1)
        """
        features = {}

        # Experience match
        features["experience_match"] = self._calculate_experience_match(candidate, job)

        # Skills match
        features["skills_match"] = self._calculate_skills_match(candidate, job)

        # Education match
        features["education_match"] = self._calculate_education_match(candidate, job)

        # Location match
        features["location_match"] = self._calculate_location_match(candidate, job)

        # Recency of experience (how recent is the candidate's most recent role)
        features["experience_recency"] = self._calculate_experience_recency(candidate)

        # Skill diversity (how many unique skills does the candidate have)
        features["skill_diversity"] = self._calculate_skill_diversity(candidate)

        # Education level
        features["education_level"] = self._calculate_education_level(candidate)

        return features

    def _calculate_experience_match(self, candidate: Candidate, job: Job) -> float:
        """Calculate how well candidate's experience matches job requirements."""
        if not candidate.parsed_data:
            return 0.0

        candidate_experience = extract_years_of_experience(
            candidate.parsed_data.get("experience", [])
        )

        # Assume job description gives us a hint about required experience
        job_description = (job.description or "").lower()
        required_years = self._extract_required_experience_from_description(
            job_description
        )

        if required_years == 0:
            return 1.0 if candidate_experience > 0 else 0.0

        # Calculate match: perfect if within +/- 2 years, decreases beyond
        diff = abs(candidate_experience - required_years)
        if diff <= 2:
            return 1.0
        else:
            # Penalty for being overqualified or underqualified
            return max(0.0, 1.0 - (diff / 10.0))

    def _calculate_skills_match(self, candidate: Candidate, job: Job) -> float:
        """Calculate how many required skills the candidate has."""
        if not candidate.parsed_data:
            return 0.0

        candidate_skills = [
            s.lower() for s in candidate.parsed_data.get("skills", [])
        ]
        if not candidate_skills:
            return 0.0

        # Extract skills from job description
        job_description = (job.description or "").lower()
        required_skills = self._extract_skills_from_description(job_description)

        if not required_skills:
            # If no explicit skills found, just reward having skills
            return min(1.0, len(candidate_skills) / 10.0)

        # Calculate percentage of required skills the candidate has
        matched = sum(1 for skill in required_skills if skill in candidate_skills)
        return matched / len(required_skills) if required_skills else 0.0

    def _calculate_education_match(self, candidate: Candidate, job: Job) -> float:
        """Calculate if candidate meets education requirements."""
        if not candidate.parsed_data:
            return 0.0

        candidate_education = " ".join(
            [str(e).lower() for e in candidate.parsed_data.get("education", [])]
        )

        job_description = (job.description or "").lower()

        # Look for common degree types
        degree_keywords = {
            "bachelor": 0.7,
            "master": 0.9,
            "phd": 1.0,
            "degree": 0.6,
            "diploma": 0.4,
        }

        max_score = 0.0
        for keyword, score in degree_keywords.items():
            if keyword in candidate_education:
                max_score = max(max_score, score)

        # Check if job requires specific education
        if any(kw in job_description for kw in degree_keywords):
            if max_score > 0:
                return max_score
            else:
                return 0.3  # Penalty for not meeting education requirement
        else:
            return max_score if max_score > 0 else 0.5

    def _calculate_location_match(self, candidate: Candidate, job: Job) -> float:
        """Calculate if candidate location matches job location."""
        candidate_location = (
            (candidate.parsed_data or {}).get("location", "").lower()
            if candidate.parsed_data
            else ""
        )
        job_location = (job.location or "").lower()

        if not job_location:
            return 1.0  # No location requirement

        if not candidate_location:
            return 0.5  # Unknown location

        if candidate_location == job_location:
            return 1.0

        # Partial match (same city/region)
        if any(
            part in job_location for part in candidate_location.split()
        ) or any(part in candidate_location for part in job_location.split()):
            return 0.7

        return 0.2  # Different location

    def _calculate_experience_recency(self, candidate: Candidate) -> float:
        """Calculate how recent the candidate's most recent role is."""
        if not candidate.parsed_data:
            return 0.0

        experience = candidate.parsed_data.get("experience", [])
        if not experience:
            return 0.0

        # Assume most recent is first in list
        most_recent = experience[0] if isinstance(experience, list) else None
        if not most_recent:
            return 0.5

        # Simple heuristic: if role says "current" or recent, score higher
        role_str = str(most_recent).lower()
        if any(word in role_str for word in ["current", "present", "now"]):
            return 1.0

        return 0.7  # Default high score if we have recent roles

    def _calculate_skill_diversity(self, candidate: Candidate) -> float:
        """Calculate how many diverse skills the candidate has."""
        if not candidate.parsed_data:
            return 0.0

        skills = candidate.parsed_data.get("skills", [])
        if not skills:
            return 0.0

        # Normalize to 0-1 range: 0 skills = 0, 10+ skills = 1
        return min(1.0, len(skills) / 10.0)

    def _calculate_education_level(self, candidate: Candidate) -> float:
        """Calculate the highest education level."""
        if not candidate.parsed_data:
            return 0.0

        education = " ".join(
            [str(e).lower() for e in candidate.parsed_data.get("education", [])]
        )

        # Map education keywords to levels
        if "phd" in education or "doctorate" in education:
            return 1.0
        elif "master" in education:
            return 0.85
        elif "bachelor" in education:
            return 0.7
        elif "degree" in education:
            return 0.6
        elif "diploma" in education:
            return 0.4
        elif "certification" in education:
            return 0.3

        return 0.0

    def _extract_required_experience_from_description(
        self, description: str
    ) -> int:
        """Extract required years of experience from job description."""
        # Simple pattern matching for "X years" or "X+ years"
        import re

        pattern = r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)"
        matches = re.findall(pattern, description)

        if matches:
            return int(matches[0])

        return 0

    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skill keywords from job description."""
        # Common tech skills to look for
        common_skills = [
            "python",
            "javascript",
            "typescript",
            "java",
            "csharp",
            "c++",
            "golang",
            "rust",
            "ruby",
            "php",
            "swift",
            "kotlin",
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
            "elasticsearch",
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
