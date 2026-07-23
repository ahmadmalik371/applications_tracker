from __future__ import annotations

import enum
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class CandidateStatus(str, enum.Enum):
    NEW = "New"
    REVIEW = "Review"
    INTERVIEW = "Interview"
    HIRED = "Hired"
    REJECTED = "Rejected"


class Candidate(BaseModel):
    __tablename__ = "candidates"

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(
        String(50), default=CandidateStatus.NEW.value, nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    embedded: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    applications: Mapped[list[Application]] = relationship(
        "Application", back_populates="candidate", cascade="all, delete-orphan"
    )
