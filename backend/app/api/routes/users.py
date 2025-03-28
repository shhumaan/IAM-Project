"""User management routes for AzureShield IAM."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_superuser, get_current_user, get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
)

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Retrieve users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user info."""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update current user."""
    # Check if email is being changed and if it already exists
    if user_in.email and user_in.email != current_user.email:
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update user attributes
    if user_in.email is not None:
        current_user.email = user_in.email
    if user_in.first_name is not None:
        current_user.first_name = user_in.first_name
    if user_in.last_name is not None:
        current_user.last_name = user_in.last_name
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.put("/me/password", response_model=UserSchema)
async def update_current_user_password(
    *,
    db: AsyncSession = Depends(get_db),
    password_in: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update current user password."""
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    current_user.hashed_password = get_password_hash(password_in.new_password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if email is being changed and if it already exists
    if user_in.email and user_in.email != user.email:
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update user attributes
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.first_name is not None:
        user.first_name = user_in.first_name
    if user_in.last_name is not None:
        user.last_name = user_in.last_name
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await db.delete(user)
    await db.commit()
    
    return user 