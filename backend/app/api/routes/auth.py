"""Authentication routes for AzureShield IAM."""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_mfa_secret,
    verify_mfa_code,
)
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Login endpoint."""
    # Get user from database
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Check if MFA is required
    if user.mfa_enabled:
        # In a real application, you would handle MFA verification here
        # For now, we'll just return a placeholder response
        return {
            "access_token": "",
            "token_type": "bearer",
            "refresh_token": "",
            "mfa_required": True,
            "mfa_secret": user.mfa_secret,
        }
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=refresh_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

@router.post("/register", response_model=UserSchema)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Register new user."""
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True,
        is_superuser=False,
        mfa_enabled=False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/verify-mfa")
async def verify_mfa(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: str,
    mfa_code: str,
) -> Any:
    """Verify MFA code."""
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or MFA not enabled",
        )
    
    if not verify_mfa_code(user.mfa_secret, mfa_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
        )
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=refresh_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

@router.post("/setup-mfa")
async def setup_mfa(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Setup MFA for user."""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA already enabled",
        )
    
    # Generate MFA secret
    mfa_secret = generate_mfa_secret()
    
    # Update user
    current_user.mfa_secret = mfa_secret
    current_user.mfa_enabled = True
    
    await db.commit()
    
    return {
        "mfa_secret": mfa_secret,
        "mfa_uri": f"otpauth://totp/{settings.MFA_ISSUER}:{current_user.email}?secret={mfa_secret}&issuer={settings.MFA_ISSUER}",
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    *,
    db: AsyncSession = Depends(get_db),
    refresh_token: str,
) -> Any:
    """Refresh access token."""
    try:
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == payload.get("sub"))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user",
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) 