import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher, exceptions as argon2_exceptions

from src.core.config import get_settings

settings = get_settings()

password_hasher = PasswordHasher(time_cost=2, memory_cost=102400, parallelism=8, hash_len=32, salt_len=16)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hasher.verify(hashed, password)
    except argon2_exceptions.VerifyMismatchError:
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    options = {"verify_exp": verify_exp}
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options=options)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)
