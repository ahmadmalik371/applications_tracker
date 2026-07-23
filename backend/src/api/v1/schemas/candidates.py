from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    deadline: Optional[datetime] = None
    employment_type: Optional[str] = Field(None, max_length=100)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    is_published: Optional[bool] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: UUID
    status: str
    is_published: bool
    organization_id: UUID
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: UUID
    status: str
    resume_url: Optional[str]
    parsed_data: Optional[dict] = None
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
    status: Optional[str] = None
    score: Optional[float] = None


class ApplicationResponse(ApplicationBase):
    id: UUID
    status: str
    score: Optional[float]
    ai_explanation: Optional[dict] = None
    is_active: bool
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    
    candidate: Optional['CandidateResponse'] = None
    job: Optional['JobResponse'] = None

    class Config:
        from_attributes = True
