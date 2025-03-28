"""Role management routes for AzureShield IAM."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_superuser, get_current_user, get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate

router = APIRouter()

@router.get("/", response_model=List[RoleSchema])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve roles."""
    result = await db.execute(select(Role).offset(skip).limit(limit))
    roles = result.scalars().all()
    return roles

@router.post("/", response_model=RoleSchema)
async def create_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_in: RoleCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new role."""
    # Check if role already exists
    result = await db.execute(select(Role).where(Role.name == role_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )
    
    role = Role(
        name=role_in.name,
        description=role_in.description,
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return role

@router.get("/{role_id}", response_model=RoleSchema)
async def get_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get role by ID."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    return role

@router.put("/{role_id}", response_model=RoleSchema)
async def update_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: str,
    role_in: RoleUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update role."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Update role attributes
    if role_in.name is not None:
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description
    
    await db.commit()
    await db.refresh(role)
    
    return role

@router.delete("/{role_id}", response_model=RoleSchema)
async def delete_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete role."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    await db.delete(role)
    await db.commit()
    
    return role

@router.post("/{role_id}/assign/{user_id}", response_model=RoleSchema)
async def assign_role_to_user(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Assign role to user."""
    # Get role
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Assign role to user
    if role not in user.roles:
        user.roles.append(role)
        await db.commit()
    
    return role

@router.post("/{role_id}/unassign/{user_id}", response_model=RoleSchema)
async def unassign_role_from_user(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Unassign role from user."""
    # Get role
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Unassign role from user
    if role in user.roles:
        user.roles.remove(role)
        await db.commit()
    
    return role 