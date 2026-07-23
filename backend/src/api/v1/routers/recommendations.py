import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.duplicate_detection import duplicate_detection_service
from src.services.recommendation import recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/jobs/{job_id}")
async def recommend_for_job(
    job_id: uuid.UUID,
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recs = await recommendation_engine.recommend_candidates(
        db, job_id, user.organization_id, limit
    )
    return {"job_id": job_id, "recommendations": recs}


@router.get("/duplicates")
async def find_duplicates(
    candidate_id: uuid.UUID = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    matches = await duplicate_detection_service.find_duplicates(
        db, user.organization_id, candidate_id
    )
    return {
        "count": len(matches),
        "duplicates": [
            {
                "candidate_id": m.candidate_id,
                "duplicate_id": m.duplicate_id,
                "similarity": m.similarity,
                "match_type": m.match_type,
            }
            for m in matches
        ],
    }


class MergeRequest(BaseModel):
    primary_id: uuid.UUID
    duplicate_id: uuid.UUID


@router.post("/merge", status_code=status.HTTP_200_OK)
async def merge_candidates(
    req: MergeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        merged = await duplicate_detection_service.merge_candidates(
            db, req.primary_id, req.duplicate_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"merged_id": str(merged.id), "email": merged.email}
