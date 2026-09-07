import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.models.models import EmailCode, LoginAttempt, User
from app.schemas.schemas import (
    EmailVerifyRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.email_service import EmailService
from app.services.password_service import PasswordService

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("password cannot be empty")
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return pwd_context.verify(plain[:72], hashed)
    except Exception:
        return False


def _create_token(subject: str, expires_delta: timedelta) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(username: str) -> str:
    return _create_token(username, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(username: str) -> str:
    return _create_token(username, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_error
    except jwt.JWTError:
        raise credentials_error

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_error
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def _check_login_attempts(ip: str, db: AsyncSession) -> bool:
    window_start = datetime.now(timezone.utc) - timedelta(minutes=settings.LOGIN_ATTEMPT_WINDOW_MINUTES)
    result = await db.execute(
        select(LoginAttempt)
        .where(
            LoginAttempt.ip_address == ip,
            LoginAttempt.attempted_at >= window_start,
            LoginAttempt.success.is_(False),
        )
    )
    failed = len(result.scalars().all())
    return failed < settings.MAX_LOGIN_ATTEMPTS


async def _record_login_attempt(ip: str, email: str, success: bool, db: AsyncSession) -> None:
    db.add(LoginAttempt(ip_address=ip, email=email, success=success))
    await db.commit()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    is_valid, error = PasswordService.validate_password(payload.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    existing = await db.execute(
        select(User).where(
            (User.username == payload.username) | (User.email == payload.email)
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="username or email already in use")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_verified=settings.email_enabled is False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    db.add(EmailCode(email=payload.email, code=code, expires_at=expires_at))
    await db.commit()

    if settings.email_enabled:
        html = EmailService.verification_email_html(code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
        await EmailService.send_email(payload.email, "Email confirmation", html)
    else:
        request.state.dev_code = code

    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    if not await _check_login_attempts(client_ip, db):
        raise HTTPException(
            status_code=429,
            detail=f"too many attempts, try again in {settings.LOGIN_ATTEMPT_WINDOW_MINUTES} minutes",
        )

    result = await db.execute(
        select(User).where(
            (User.username == credentials.login) | (User.email == credentials.login)
        )
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.hashed_password):
        await _record_login_attempt(client_ip, credentials.login, False, db)
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="account is deactivated")

    await _record_login_attempt(client_ip, credentials.login, True, db)

    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(mode="json"),
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        token_data = jwt.decode(
            payload.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username = token_data.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="invalid refresh token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="user not found or inactive")

    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(mode="json"),
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/resend-code")
async def resend_code(payload: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="email already verified")

    code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    db.add(EmailCode(email=payload.email, code=code, expires_at=expires_at))
    await db.commit()

    if settings.email_enabled:
        html = EmailService.verification_email_html(code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
        await EmailService.send_email(payload.email, "Email confirmation", html)
        return {"message": "verification code sent"}

    return {"message": "verification code generated", "code": code, "expires_in": settings.EMAIL_TOKEN_EXPIRE_MINUTES}


@router.post("/confirm-email")
async def confirm_email(payload: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    if user.is_verified:
        return {"message": "email already verified"}

    now = datetime.now(timezone.utc)
    code_result = await db.execute(
        select(EmailCode)
        .where(
            EmailCode.email == payload.email,
            EmailCode.code == payload.code,
            EmailCode.is_used.is_(False),
            EmailCode.expires_at > now,
        )
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    )
    email_code = code_result.scalar_one_or_none()
    if email_code is None:
        raise HTTPException(status_code=400, detail="invalid or expired code")

    email_code.is_used = True
    user.is_verified = True
    await db.commit()
    return {"message": "email verified"}


@router.post("/reset-password-request")
async def reset_password_request(payload: EmailVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        return {"message": "if the email exists, a reset code has been sent"}

    code = EmailService.generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    db.add(EmailCode(email=payload.email, code=code, expires_at=expires_at))
    await db.commit()

    if settings.email_enabled:
        html = EmailService.reset_password_email_html(code, settings.EMAIL_TOKEN_EXPIRE_MINUTES)
        await EmailService.send_email(payload.email, "Password reset", html)
        return {"message": "if the email exists, a reset code has been sent"}

    return {
        "message": "if the email exists, a reset code has been sent",
        "code": code,
        "expires_in": settings.EMAIL_TOKEN_EXPIRE_MINUTES,
    }


@router.post("/reset-password-confirm")
async def reset_password_confirm(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    is_valid, error = PasswordService.validate_password(payload.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    now = datetime.now(timezone.utc)
    code_result = await db.execute(
        select(EmailCode)
        .where(
            EmailCode.email == payload.email,
            EmailCode.code == payload.code,
            EmailCode.is_used.is_(False),
            EmailCode.expires_at > now,
        )
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    )
    email_code = code_result.scalar_one_or_none()
    if email_code is None:
        raise HTTPException(status_code=400, detail="invalid or expired code")

    user.hashed_password = hash_password(payload.new_password)
    email_code.is_used = True
    await db.commit()
    return {"message": "password reset successfully"}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="current password is incorrect")

    is_valid, error = PasswordService.validate_password(payload.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return {"message": "password changed"}


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is not None:
            setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user
