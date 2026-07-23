import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Application, Candidate, Job
from src.services.embedding import compute_similarity


async def hybrid_search_candidates(
    session: AsyncSession,
    query: str,
    organization_id: uuid.UUID,
    limit: int = 20,
    semantic_weight: float = 0.6,
    keyword_weight: float = 0.4,
) -> list[dict]:
    """Hybrid search combining PostgreSQL full-text search with pgvector semantic similarity.

    Returns candidates ranked by a weighted blend of keyword and semantic scores.
    """
    if not query.strip():
        return []

    try:
        candidates_result = await session.execute(
            select(Candidate).where(Candidate.organization_id == organization_id)
        )
        candidates = candidates_result.scalars().all()

        query_lower = query.lower()
        query_terms = [t for t in query_lower.split() if len(t) > 1]

        results = []
        for candidate in candidates:
            parsed = candidate.parsed_data or {}
            searchable = " ".join(
                [
                    candidate.email or "",
                    candidate.first_name or "",
                    candidate.last_name or "",
                    " ".join(parsed.get("skills", [])),
                    " ".join(str(e) for e in parsed.get("experience", [])),
                    " ".join(str(e) for e in parsed.get("education", [])),
                    parsed.get("location", "") or "",
                ]
            ).lower()

            # Keyword score: fraction of query terms present
            if query_terms:
                hits = sum(1 for t in query_terms if t in searchable)
                keyword_score = hits / len(query_terms)
            else:
                keyword_score = 0.0

            # Semantic score: cosine similarity between candidate embedding and query embedding
            semantic_score = 0.0
            if candidate.embedded is not None:
                try:
                    from src.services.embedding import generate_job_embedding

                    query_embedding = await generate_job_embedding(query)
                    from src.services.embedding import compute_similarity

                    semantic_score = await compute_similarity(
                        query_embedding, candidate.embedded
                    )
                except Exception:
                    semantic_score = 0.0

            combined = semantic_weight * semantic_score + keyword_weight * keyword_score
            if combined > 0:
                results.append(
                    {
                        "candidate_id": str(candidate.id),
                        "candidate_name": f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                        "email": candidate.email,
                        "status": candidate.status,
                        "keyword_score": round(keyword_score, 4),
                        "semantic_score": round(semantic_score, 4),
                        "combined_score": round(combined, 4),
                        "skills": parsed.get("skills", [])[:5],
                    }
                )

        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return results[:limit]
    except Exception as e:
        raise ValueError(f"Failed hybrid search: {str(e)}")


async def find_similar_candidates(
    session: AsyncSession,
    job_id: uuid.UUID,
    organization_id: uuid.UUID,
    limit: int = 10,
) -> list[dict]:
    """
    Find candidates most similar to a job using vector similarity.
    Returns candidates ranked by similarity score.
    """
    try:
        # Get job with embedding
        job_result = await session.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()

        if not job or job.embedding is None:
            # No embedding available for job
            return []

        # Get all candidates with embeddings for organization
        candidates_result = await session.execute(
            select(Candidate).where(
                and_(
                    Candidate.organization_id == organization_id,
                    Candidate.embedded.isnot(None),
                )
            )
        )
        candidates = candidates_result.scalars().all()

        # Calculate similarity scores
        matches = []
        for candidate in candidates:
            similarity = await compute_similarity(job.embedding, candidate.embedded)
            matches.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_name": f"{candidate.first_name or ''} {candidate.last_name or ''}".strip(),
                    "email": candidate.email,
                    "score": round(similarity, 4),
                    "status": candidate.status,
                }
            )

        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches[:limit]
    except Exception as e:
        raise ValueError(f"Failed to find similar candidates: {str(e)}")


async def find_matching_jobs(
    session: AsyncSession,
    candidate_id: uuid.UUID,
    organization_id: uuid.UUID,
    limit: int = 10,
) -> list[dict]:
    """
    Find jobs most similar to a candidate using vector similarity.
    Returns jobs ranked by similarity score.
    """
    try:
        # Get candidate with embedding
        candidate_result = await session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()

        if not candidate or candidate.embedded is None:
            # No embedding available for candidate
            return []

        # Get all published jobs with embeddings for organization
        jobs_result = await session.execute(
            select(Job).where(
                and_(
                    Job.organization_id == organization_id,
                    Job.embedding.isnot(None),
                    Job.is_published == True,
                )
            )
        )
        jobs = jobs_result.scalars().all()

        # Calculate similarity scores
        matches = []
        for job in jobs:
            similarity = await compute_similarity(candidate.embedded, job.embedding)
            matches.append(
                {
                    "job_id": job.id,
                    "title": job.title,
                    "location": job.location,
                    "score": round(similarity, 4),
                    "status": job.status,
                }
            )

        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches[:limit]
    except Exception as e:
        raise ValueError(f"Failed to find matching jobs: {str(e)}")


async def bulk_create_auto_applications(
    session: AsyncSession,
    job_id: uuid.UUID,
    organization_id: uuid.UUID,
    similarity_threshold: float = 0.7,
) -> list[uuid.UUID]:
    """
    Automatically create applications for candidates that exceed similarity threshold.
    """
    try:
        # Get similar candidates
        similar = await find_similar_candidates(
            session, job_id, organization_id, limit=100
        )

        created_application_ids = []

        for match in similar:
            if match["score"] >= similarity_threshold:
                # Check if application already exists
                existing = await session.execute(
                    select(Application).where(
                        and_(
                            Application.job_id == job_id,
                            Application.candidate_id == match["candidate_id"],
                        )
                    )
                )

                if not existing.scalar_one_or_none():
                    # Create new application
                    app = Application(
                        job_id=job_id,
                        candidate_id=match["candidate_id"],
                        organization_id=organization_id,
                        score=match["score"],
                    )
                    session.add(app)
                    created_application_ids.append(app.id)

        if created_application_ids:
            await session.commit()

        return created_application_ids
    except Exception as e:
        raise ValueError(f"Failed to bulk create applications: {str(e)}")
