from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.schemas.auth import (
    EmailVerificationRequest,
    LoginRequest,
    LogoutRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from src.api.dependencies import get_db
from src.core.security import create_access_token, create_refresh_token
from src.services.auth import (
    authenticate_user,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token_record,
    create_organization_with_admin,
    get_refresh_token_record,
    invalidate_refresh_token,
    reset_password_with_token,
    verify_email_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request: RegisterRequest, db=Depends(get_db)):
    organization, user = await create_organization_with_admin(
        db,
        request.organization_name,
        request.email,
        request.password,
        request.full_name,
    )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()
    await create_refresh_token_record(db, user, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()
    await create_refresh_token_record(db, user, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db=Depends(get_db)):
    token_record = await get_refresh_token_record(db, request.refresh_token)
    if not token_record or token_record.is_revoked or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = token_record.user
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()
    token_record.is_revoked = True
    await db.commit()
    await create_refresh_token_record(db, user, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(request: LogoutRequest, db=Depends(get_db)):
    await invalidate_refresh_token(db, request.refresh_token)
    return {"success": True}


@router.post("/password-reset/request")
async def request_password_reset(request: PasswordResetRequest, db=Depends(get_db)):
    await create_password_reset_token(db, request.email)
    return {"success": True, "message": "If an account exists for that email, a password reset token has been issued."}


@router.post("/password-reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest, db=Depends(get_db)):
    await reset_password_with_token(db, request.token, request.new_password)
    return {"success": True}


@router.post("/verify-email")
async def verify_email(request: EmailVerificationRequest, db=Depends(get_db)):
    await verify_email_token(db, request.token)
    return {"success": True}
