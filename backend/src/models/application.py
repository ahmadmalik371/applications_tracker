from __future__ import annotations

import enum
import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class ApplicationStage(str, enum.Enum):
    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    HIRED = "Hired"
    REJECTED = "Rejected"


class Application(BaseModel):
    __tablename__ = "applications"

    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[ApplicationStage] = mapped_column(String(50), default=ApplicationStage.APPLIED.value, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)

    job: Mapped["Job"] = relationship("Job", back_populates="applications", lazy="joined")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="applications", lazy="joined")
