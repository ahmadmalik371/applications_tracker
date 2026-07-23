from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Candidate
from src.services.embedding import compute_similarity


@dataclass
class DuplicateMatch:
    candidate_id: str
    duplicate_id: str
    similarity: float
    match_type: str


class DuplicateDetectionService:
    """Detect duplicate candidates by email, phone, name, or embedding similarity."""

    EMAIL_THRESHOLD = 1.0
    PHONE_THRESHOLD = 1.0
    NAME_THRESHOLD = 0.8
    EMBEDDING_THRESHOLD = 0.92

    async def find_duplicates(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        candidate_id: uuid.UUID | None = None,
    ) -> list[DuplicateMatch]:
        stmt = select(Candidate).where(Candidate.organization_id == organization_id)
        if candidate_id is not None:
            stmt = stmt.where(Candidate.id == candidate_id)

        result = await session.execute(stmt)
        candidates = result.scalars().all()

        matches: list[DuplicateMatch] = []
        seen: set[tuple[str, str]] = set()

        for i, a in enumerate(candidates):
            for b in candidates[i + 1 :]:
                pair_key = tuple(sorted([str(a.id), str(b.id)]))
                if pair_key in seen:
                    continue

                match = self._compare_pair(a, b)
                if match:
                    seen.add(pair_key)
                    matches.append(match)
        return matches

    def _compare_pair(self, a: Candidate, b: Candidate) -> DuplicateMatch | None:
        if a.email and b.email and a.email.lower() == b.email.lower():
            return DuplicateMatch(str(a.id), str(b.id), 1.0, "email")

        phone_a = (a.parsed_data or {}).get("phone") if a.parsed_data else None
        phone_b = (b.parsed_data or {}).get("phone") if b.parsed_data else None
        if phone_a and phone_b and phone_a == phone_b:
            return DuplicateMatch(str(a.id), str(b.id), 1.0, "phone")

        name_a = f"{a.first_name or ''} {a.last_name or ''}".strip().lower()
        name_b = f"{b.first_name or ''} {b.last_name or ''}".strip().lower()
        if name_a and name_b:
            name_sim = _string_similarity(name_a, name_b)
            if name_sim >= self.NAME_THRESHOLD:
                return DuplicateMatch(str(a.id), str(b.id), name_sim, "name")

        if a.embedded and b.embedded:
            emb_sim = compute_similarity(a.embedded, b.embedded)
            if emb_sim >= self.EMBEDDING_THRESHOLD:
                return DuplicateMatch(str(a.id), str(b.id), emb_sim, "embedding")

        return None

    async def merge_candidates(
        self,
        session: AsyncSession,
        primary_id: uuid.UUID,
        duplicate_id: uuid.UUID,
    ) -> Candidate:
        """Merge duplicate candidate into the primary, preserving the richer record."""
        primary = await session.get(Candidate, primary_id)
        duplicate = await session.get(Candidate, duplicate_id)
        if not primary or not duplicate:
            raise ValueError("Candidate not found")

        if not primary.parsed_data and duplicate.parsed_data:
            primary.parsed_data = duplicate.parsed_data
        if not primary.embedded and duplicate.embedded:
            primary.embedded = duplicate.embedded
        if not primary.resume_url and duplicate.resume_url:
            primary.resume_url = duplicate.resume_url
        if not primary.phone and duplicate.phone:
            primary.phone = duplicate.phone
        if not primary.first_name and duplicate.first_name:
            primary.first_name = duplicate.first_name
        if not primary.last_name and duplicate.last_name:
            primary.last_name = duplicate.last_name

        await session.delete(duplicate)
        await session.commit()
        await session.refresh(primary)
        return primary


def _string_similarity(a: str, b: str) -> float:
    """Simple Jaccard similarity on word sets."""
    wa, wb = set(a.split()), set(b.split())
    if not wa and not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


duplicate_detection_service = DuplicateDetectionService()
