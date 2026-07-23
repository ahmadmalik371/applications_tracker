import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from src.core.config import get_settings
from src.services.storage import storage_provider

settings = get_settings()

# Allowed file extensions for resumes
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def validate_resume_file(file: UploadFile) -> None:
    """Validate resume file type and size."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required"
        )

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Check file size (read content to get size)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {MAX_FILE_SIZE / (1024 * 1024)}MB limit",
        )

    # Reset file position for later reading
    await file.seek(0)


async def save_resume_file(file: UploadFile, candidate_id: str) -> tuple[str, int]:
    """Save resume file via the configured storage provider and return URL and file size."""
    await validate_resume_file(file)

    file_ext = Path(file.filename).suffix
    unique_filename = f"resumes/{candidate_id}_{uuid.uuid4()}{file_ext}"

    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    resume_url = await storage_provider.save(content, unique_filename, content_type)

    return resume_url, len(content)
