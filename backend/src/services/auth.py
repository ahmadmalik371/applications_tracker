import secrets
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password, create_refresh_token
from src.models import (
    EmailVerificationToken,
    Organization,
    PasswordResetToken,
    RefreshToken,
    Role,
    Session,
    User,
)

DEFAULT_ROLES = [
    "Super Admin",
    "Company Admin",
    "Recruiter",
    "Hiring Manager",
    "Candidate",
]


async def get_role_by_name(session: AsyncSession, name: str) -> Role | None:
    result = await session.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def ensure_roles(session: AsyncSession) -> None:
    result = await session.execute(select(Role))
    existing_names = {role.name for role in result.scalars().all()}
    for name in DEFAULT_ROLES:
        if name not in existing_names:
            session.add(Role(name=name, description=f"Default {name} role"))
    await session.commit()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_organization_with_admin(
    session: AsyncSession,
    organization_name: str,
    email: str,
    password: str,
    full_name: str | None = None,
) -> tuple[Organization, User]:
    await ensure_roles(session)

    organization = Organization(name=organization_name)
    session.add(organization)
    await session.flush()

    role = await get_role_by_name(session, "Company Admin")
    if role is None:
        raise ValueError("Company Admin role is not available")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role_id=role.id,
        organization_id=organization.id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return organization, user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_refresh_token_record(session: AsyncSession, user: User, refresh_token: str) -> RefreshToken:
    expires_at = datetime.utcnow() + timedelta(days=7)
    token_record = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    session.add(token_record)
    await session.commit()
    await session.refresh(token_record)
    return token_record


async def get_refresh_token_record(session: AsyncSession, refresh_token: str) -> RefreshToken | None:
    result = await session.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    return result.scalar_one_or_none()


async def invalidate_refresh_token(session: AsyncSession, refresh_token: str) -> None:
    token = await get_refresh_token_record(session, refresh_token)
    if token:
        token.is_revoked = True
        await session.commit()


async def create_password_reset_token(session: AsyncSession, email: str) -> PasswordResetToken | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    password_token = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
    session.add(password_token)
    await session.commit()
    await session.refresh(password_token)
    return password_token


async def reset_password_with_token(session: AsyncSession, token: str, new_password: str) -> None:
    result = await session.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
    password_token = result.scalar_one_or_none()
    if not password_token or password_token.expires_at < datetime.utcnow() or password_token.is_revoked:
        raise ValueError("Invalid or expired password reset token")

    user = await session.get(User, password_token.user_id)
    if not user:
        raise ValueError("User not found")

    user.hashed_password = hash_password(new_password)
    password_token.is_revoked = True
    await session.commit()


async def create_email_verification_token(session: AsyncSession, email: str) -> EmailVerificationToken | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    verification_token = EmailVerificationToken(user_id=user.id, token=token_value, expires_at=expires_at)
    session.add(verification_token)
    await session.commit()
    await session.refresh(verification_token)
    return verification_token


async def verify_email_token(session: AsyncSession, token: str) -> None:
    result = await session.execute(select(EmailVerificationToken).where(EmailVerificationToken.token == token))
    verification_token = result.scalar_one_or_none()
    if not verification_token or verification_token.expires_at < datetime.utcnow():
        raise ValueError("Invalid or expired email verification token")

    user = await session.get(User, verification_token.user_id)
    if not user:
        raise ValueError("User not found")

    user.is_verified = True
    await session.delete(verification_token)
    await session.commit()


async def create_session_record(session: AsyncSession, user: User, token: str, ip_address: str | None = None, user_agent: str | None = None) -> Session:
    expires_at = datetime.utcnow() + timedelta(days=7)
    session_record = Session(
        user_id=user.id,
        token=token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        is_active=True,
    )
    session.add(session_record)
    await session.commit()
    await session.refresh(session_record)
    return session_record
