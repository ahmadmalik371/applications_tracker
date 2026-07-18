import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.dependencies import get_current_user, get_db
from src.models import User
from src.services.interview import InterviewService


router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])
interview_service = InterviewService()


class ScheduleRequest(BaseModel):
    application_id: str
    interview_type: str = "phone"
    scheduled_at: str
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    panelist_ids: Optional[List[str]] = None


class FeedbackRequest(BaseModel):
    rating: int
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class InterviewResponse(BaseModel):
    id: str
    application_id: str
    organization_id: str
    interview_type: str
    scheduled_at: datetime
    duration_minutes: int
    location: Optional[str]
    meeting_link: Optional[str]
    status: str
    notes: Optional[str]
    created_by_id: Optional[str]

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    id: str
    interview_id: str
    panelist_id: str
    rating: int
    strengths: Optional[str]
    weaknesses: Optional[str]
    recommendation: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    req: ScheduleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Schedule a new interview."""
    panelist_ids = [uuid.UUID(p) for p in req.panelist_ids] if req.panelist_ids else None
    interview = await interview_service.schedule_interview(
        session,
        uuid.UUID(req.application_id),
        current_user.organization_id,
        req.interview_type,
        req.scheduled_at,
        req.duration_minutes,
        req.location,
        req.meeting_link,
        panelist_ids,
        current_user.id,
    )
    await session.commit()
    await session.refresh(interview)
    return interview


@router.get("/application/{application_id}", response_model=List[InterviewResponse])
async def list_interviews(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all interviews for an application."""
    return await interview_service.get_interviews_for_application(session, application_id)


@router.patch("/{interview_id}/status", response_model=InterviewResponse)
async def update_interview_status(
    interview_id: uuid.UUID,
    req: StatusUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update an interview's status."""
    try:
        interview = await interview_service.update_status(session, interview_id, req.status)
        await session.commit()
        await session.refresh(interview)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{interview_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    interview_id: uuid.UUID,
    req: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Submit feedback for an interview."""
    try:
        feedback = await interview_service.submit_feedback(
            session,
            interview_id,
            current_user.id,
            req.rating,
            req.strengths,
            req.weaknesses,
            req.recommendation,
            req.notes,
        )
        await session.commit()
        await session.refresh(feedback)
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{interview_id}/feedback", response_model=List[FeedbackResponse])
async def get_feedback(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get all feedback for an interview."""
    return await interview_service.get_feedback(session, interview_id)
