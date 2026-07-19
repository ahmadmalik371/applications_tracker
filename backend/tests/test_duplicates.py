import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Candidate
from src.services.duplicate_detection import duplicate_detection_service


@pytest.mark.asyncio
async def test_duplicate_email_detection(session: AsyncSession):
    org_id = uuid.uuid4()
    a = Candidate(id=uuid.uuid4(), email="dup@example.com", organization_id=org_id)
    b = Candidate(id=uuid.uuid4(), email="dup@example.com", organization_id=org_id)
    session.add_all([a, b])
    await session.commit()

    matches = await duplicate_detection_service.find_duplicates(session, org_id)
    assert len(matches) == 1
    assert matches[0].match_type == "email"
    assert matches[0].similarity == 1.0


@pytest.mark.asyncio
async def test_duplicate_name_detection(session: AsyncSession):
    org_id = uuid.uuid4()
    a = Candidate(id=uuid.uuid4(), email="a@example.com", organization_id=org_id,
                  first_name="John", last_name="Smith")
    b = Candidate(id=uuid.uuid4(), email="b@example.com", organization_id=org_id,
                  first_name="John", last_name="Smith")
    session.add_all([a, b])
    await session.commit()

    matches = await duplicate_detection_service.find_duplicates(session, org_id)
    assert len(matches) == 1
    assert matches[0].match_type == "name"


@pytest.mark.asyncio
async def test_no_duplicate_for_different_candidates(session: AsyncSession):
    org_id = uuid.uuid4()
    a = Candidate(id=uuid.uuid4(), email="a@example.com", organization_id=org_id,
                  first_name="Alice", last_name="Wonderland")
    b = Candidate(id=uuid.uuid4(), email="b@example.com", organization_id=org_id,
                  first_name="Bob", last_name="Builder")
    session.add_all([a, b])
    await session.commit()

    matches = await duplicate_detection_service.find_duplicates(session, org_id)
    assert len(matches) == 0


@pytest.mark.asyncio
async def test_merge_candidates(session: AsyncSession):
    org_id = uuid.uuid4()
    primary = Candidate(
        id=uuid.uuid4(), email="primary@example.com", organization_id=org_id,
        first_name="Alice",
    )
    duplicate = Candidate(
        id=uuid.uuid4(), email="dup@example.com", organization_id=org_id,
        parsed_data={"skills": ["Python"]},
    )
    session.add_all([primary, duplicate])
    await session.commit()

    merged = await duplicate_detection_service.merge_candidates(
        session, primary.id, duplicate.id
    )
    assert merged.id == primary.id
    assert merged.parsed_data == {"skills": ["Python"]}

    from sqlalchemy import select
    result = await session.execute(
        select(Candidate).where(Candidate.id == duplicate.id)
    )
    assert result.scalar_one_or_none() is None
