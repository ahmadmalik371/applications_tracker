import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Candidate, User
from src.models.recruiter import Tag, CandidateTag, Note


@pytest.mark.asyncio
async def test_create_tag(session: AsyncSession):
    """Test creating a tag."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    tag = Tag(
        organization_id=org_id,
        name="High Priority",
        description="Candidates with high priority",
        color="red",
        created_by_id=user_id,
    )

    session.add(tag)
    await session.commit()
    await session.refresh(tag)

    assert tag.id is not None
    assert tag.name == "High Priority"
    assert tag.color == "red"


@pytest.mark.asyncio
async def test_add_tag_to_candidate(session: AsyncSession):
    """Test adding a tag to a candidate."""
    candidate_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    user_id = uuid.uuid4()

    candidate_tag = CandidateTag(
        candidate_id=candidate_id,
        tag_id=tag_id,
        added_by_id=user_id,
    )

    session.add(candidate_tag)
    await session.commit()

    # Verify it was created
    from sqlalchemy import select

    result = await session.execute(
        select(CandidateTag).where(
            CandidateTag.candidate_id == candidate_id,
            CandidateTag.tag_id == tag_id,
        )
    )
    retrieved = result.scalar_one_or_none()
    assert retrieved is not None
    assert retrieved.candidate_id == candidate_id


@pytest.mark.asyncio
async def test_create_note(session: AsyncSession):
    """Test creating a note."""
    candidate_id = uuid.uuid4()
    author_id = uuid.uuid4()

    note = Note(
        candidate_id=candidate_id,
        author_id=author_id,
        content="This candidate has strong technical skills.",
        is_private=False,
    )

    session.add(note)
    await session.commit()
    await session.refresh(note)

    assert note.id is not None
    assert note.content == "This candidate has strong technical skills."
    assert note.is_private is False


@pytest.mark.asyncio
async def test_note_privacy(session: AsyncSession):
    """Test note privacy settings."""
    candidate_id = uuid.uuid4()
    author_id = uuid.uuid4()

    private_note = Note(
        candidate_id=candidate_id,
        author_id=author_id,
        content="Private thoughts",
        is_private=True,
    )

    session.add(private_note)
    await session.commit()
    await session.refresh(private_note)

    assert private_note.is_private is True
