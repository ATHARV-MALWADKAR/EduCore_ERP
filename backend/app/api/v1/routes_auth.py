"""
Authentication endpoints with access/refresh token flow and password management.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password
)
from app.crud import entities as crud
from app.db.models import User, UserRefreshToken
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    UserResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, returns access and refresh tokens.
    """
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token (short-lived)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.email,
        user_id=user.id,
        role_name=user.role.name,
        expires_delta=access_token_expires
    )

    # Create refresh token (long-lived)
    refresh_token_expires = timedelta(days=7)
    refresh_token_expires_at = datetime.now(timezone.utc) + refresh_token_expires
    refresh_token_hash = hash_password(
        f"{settings.secret_key}:{user.id}:{datetime.now(timezone.utc).timestamp()}"
    )

    refresh_token = crud.create_refresh_token(
        db,
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=refresh_token_expires_at
    )

    # In a real implementation, you'd return the actual refresh token to the user
    # For security, we only return a reference ID or handle it via HttpOnly cookies
    # For simplicity in this implementation, we'll return a mock refresh token
    # In production, consider using secure HTTP-only cookies for refresh tokens

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_hash,  # In production, don't return actual token
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user_id": user.id,
        "role": user.role.name,
        "full_name": user.full_name
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    """
    # In production, validate the refresh token hash against database
    # For now, we'll implement a simplified version
    refresh_token = crud.get_refresh_token(db, request.refresh_token)

    if not refresh_token or not refresh_token.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if expired
    if refresh_token.is_expired:
        crud.revoke_refresh_token(db, request.refresh_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = crud.get_user(db, refresh_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        subject=user.email,
        user_id=user.id,
        role_name=user.role.name,
        expires_delta=access_token_expires
    )

    # Optionally rotate refresh token (uncomment for production)
    # crud.revoke_refresh_token(db, request.refresh_token)
    # new_refresh_token_hash = hash_password(f"{settings.secret_key}:{user.id}:{datetime.now(timezone.utc).timestamp()}")
    # new_refresh_token = crud.create_refresh_token(
    #     db,
    #     user_id=user.id,
    #     token_hash=new_refresh_token_hash,
    #     expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    # )

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,  # In production, return new rotated token
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user_id": user.id,
        "role": user.role.name,
        "full_name": user.full_name
    }


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # We'll get user from token in deps
) -> Any:
    """
    Logout user by revoking refresh token.
    """
    # In production, get token from Authorization header
    # For now, we'll revoke the provided refresh token
    success = crud.revoke_refresh_token(db, request.refresh_token)

    if success:
        return {"message": "Successfully logged out"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


@router.post("/logout-all", response_model=MessageResponse)
def logout_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Will be implemented with proper deps
) -> Any:
    """
    Logout user from all devices by revoking all refresh tokens.
    """
    # In production, get current user from token
    count = crud.revoke_all_user_tokens(db, current_user.id)
    return {"message": f"Successfully logged out from {count} sessions"}


@router.post("/request-reset", response_model=MessageResponse)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset email (simplified - in production sends actual email).
    """
    user = crud.get_user_by_email(db, request.email)
    if user:
        # In production: generate token, store in DB, send email
        # For demo: just log to console
        print(f"[PASSWORD RESET] Token for {request.email}: demo-reset-token-123")

    # Always return same message to prevent email enumeration
    return {"message": "If the email exists, reset instructions have been sent"}


@router.post("/reset-password", response_model=MessageResponse)
def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirm password reset with token and new password.
    """
    # In production: validate token from DB, update password
    # For demo: we'll simulate success
    return {"message": "Password has been successfully reset"}


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Will be implemented with proper deps
) -> Any:
    """
    Change password for authenticated user.
    """
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = hash_password(request.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Password successfully updated"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(lambda: None)  # Will be implemented with proper deps
) -> Any:
    """
    Get current user's information.
    """
    return current_user