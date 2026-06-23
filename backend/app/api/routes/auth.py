"""
Authentication API routes.
Login, register, token refresh, and user management.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    RegisterRequest, UserResponse, UserRole,
)
from app.models.database import get_db
from app.security.rbac import (
    authenticate_user, create_user, get_user_by_email, check_permission,
)
from app.api.middleware.auth import (
    create_access_token, create_refresh_token, decode_token, require_auth,
)
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user and return JWT tokens.
    """
    user = authenticate_user(request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    settings = get_settings()

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
    )

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=UserRole(user.role),
            specialty=user.specialty,
            created_at=user.created_at,
        ),
    )


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    """
    # Check if email already exists
    existing = get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role.value,
        specialty=request.specialty,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=UserRole(user.role),
        specialty=user.specialty,
        created_at=user.created_at,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an expired access token using a valid refresh token.
    """
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        email = payload.get("sub")
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        settings = get_settings()
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role},
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=UserRole(user.role),
                specialty=user.specialty,
                created_at=user.created_at,
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user=Depends(require_auth)):
    """Get the current authenticated user's information."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=UserRole(user.role),
        specialty=user.specialty,
        created_at=user.created_at,
    )
