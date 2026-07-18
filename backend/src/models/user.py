from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
import enum
import uuid
from typing import Optional
from .base import BaseModel

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "Super Admin"
    COMPANY_ADMIN = "Company Admin"
    RECRUITER = "Recruiter"
    HIRING_MANAGER = "Hiring Manager"
    CANDIDATE = "Candidate"

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), index=True, nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")

    __table_args__ = (
        UniqueConstraint("email", "organization_id", name="uix_user_email_org"),
    )
