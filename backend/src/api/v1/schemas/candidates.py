from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    location: str | None = Field(None, max_length=255)
    employment_type: str | None = Field(None, max_length=100)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    is_published: bool | None = None
    status: str | None = None


class JobResponse(JobBase):
    id: UUID
    status: str
    is_published: bool
    organization_id: UUID
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    email: str = Field(..., max_length=255)
    phone: str | None = Field(None, max_length=50)


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None


class CandidateResponse(CandidateBase):
    id: UUID
    status: str
    resume_url: str | None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    job_id: UUID
    candidate_id: UUID


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str | None = None
    score: float | None = None


class ApplicationResponse(ApplicationBase):
    id: UUID
    status: str
    score: float | None
    is_active: bool
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
