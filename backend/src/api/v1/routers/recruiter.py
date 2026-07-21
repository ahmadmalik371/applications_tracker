import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models import Candidate, User
from src.models.recruiter import CandidateTag, Note, NoteVersion, Tag

router = APIRouter(prefix="/api/v1/recruiter", tags=["recruiter"])


# Pydantic schemas - Tags
class TagCreate(BaseModel):
    name: str
    description: str | None = None
    color: str | None = "blue"


class TagUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    is_active: bool | None = None


class TagResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None
    color: str
    is_active: bool

    class Config:
        from_attributes = True


# Pydantic schemas - Notes
class NoteCreate(BaseModel):
    content: str
    is_private: bool = False
    mentions: list[str] | None = None
    attachments: list[str] | None = None


class NoteUpdate(BaseModel):
    content: str | None = None
    is_private: bool | None = None


class NoteResponse(BaseModel):
    id: str
    candidate_id: str
    author_id: str
    content: str
    is_private: bool
    mentions: list[str] | None
    attachments: list[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tag endpoints
@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a new tag for the organization."""
    tag = Tag(
        organization_id=current_user.organization_id,
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
        created_by_id=current_user.id,
    )
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List all tags for the organization."""
    result = await session.execute(
        select(Tag)
        .where(Tag.organization_id == current_user.organization_id)
        .where(Tag.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    tags = result.scalars().all()
    return tags


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update a tag."""
    result = await session.execute(
        select(Tag)
        .where(Tag.id == tag_id)
        .where(Tag.organization_id == current_user.organization_id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    update_data = tag_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(tag, key, value)

    await session.commit()
    await session.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) a tag."""
    result = await session.execute(
        select(Tag)
        .where(Tag.id == tag_id)
        .where(Tag.organization_id == current_user.organization_id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.is_active = False
    await session.commit()


# Candidate tags endpoints
@router.post(
    "/candidates/{candidate_id}/tags/{tag_id}", status_code=status.HTTP_201_CREATED
)
async def add_tag_to_candidate(
    candidate_id: uuid.UUID,
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Add a tag to a candidate."""
    # Verify candidate exists
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Verify tag exists and belongs to organization
    tag_result = await session.execute(
        select(Tag)
        .where(Tag.id == tag_id)
        .where(Tag.organization_id == current_user.organization_id)
    )
    tag = tag_result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if already tagged
    check_result = await session.execute(
        select(CandidateTag).where(
            CandidateTag.candidate_id == candidate_id,
            CandidateTag.tag_id == tag_id,
        )
    )
    if check_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Candidate already has this tag")

    candidate_tag = CandidateTag(
        candidate_id=candidate_id,
        tag_id=tag_id,
        added_by_id=current_user.id,
    )
    session.add(candidate_tag)
    await session.commit()


@router.delete(
    "/candidates/{candidate_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tag_from_candidate(
    candidate_id: uuid.UUID,
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Remove a tag from a candidate."""
    # Verify candidate exists
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    if not candidate_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = await session.execute(
        select(CandidateTag).where(
            CandidateTag.candidate_id == candidate_id,
            CandidateTag.tag_id == tag_id,
        )
    )
    candidate_tag = result.scalar_one_or_none()
    if not candidate_tag:
        raise HTTPException(status_code=404, detail="Tag not assigned to candidate")

    await session.delete(candidate_tag)
    await session.commit()


# Notes endpoints
@router.post(
    "/candidates/{candidate_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    candidate_id: uuid.UUID,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a note on a candidate."""
    # Verify candidate exists
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    if not candidate_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    note = Note(
        candidate_id=candidate_id,
        author_id=current_user.id,
        content=note_data.content,
        is_private=note_data.is_private,
        mentions=note_data.mentions,
        attachments=note_data.attachments,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


@router.get("/candidates/{candidate_id}/notes", response_model=list[NoteResponse])
async def list_candidate_notes(
    candidate_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List notes for a candidate."""
    # Verify candidate exists
    candidate_result = await session.execute(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .where(Candidate.organization_id == current_user.organization_id)
    )
    if not candidate_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = await session.execute(
        select(Note)
        .where(Note.candidate_id == candidate_id)
        .where(Note.is_deleted == False)
        .where(
            (Note.is_private == False) | (Note.author_id == current_user.id)
        )  # Show private notes only to author
        .offset(skip)
        .limit(limit)
    )
    notes = result.scalars().all()
    return notes


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update a note."""
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Only author or admin can edit
    if note.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this note")

    update_data = note_data.dict(exclude_unset=True)

    # Store version history if content changed
    if "content" in update_data and update_data["content"] != note.content:
        note_version = NoteVersion(
            note_id=note.id,
            content=note.content,
            changed_by_id=current_user.id,
        )
        session.add(note_version)

    for key, value in update_data.items():
        if value is not None:
            setattr(note, key, value)

    await session.commit()
    await session.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Soft delete a note."""
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Only author or admin can delete
    if note.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this note"
        )

    note.is_deleted = True
    note.deleted_at = datetime.utcnow()
    await session.commit()
