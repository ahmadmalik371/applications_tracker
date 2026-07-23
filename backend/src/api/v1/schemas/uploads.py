from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    candidate_id: UUID
    resume_url: str
    file_name: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
