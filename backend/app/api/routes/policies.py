"""Policy management routes for AzureShield IAM."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_superuser, get_current_user, get_db
from app.models.policy import Policy
from app.models.role import Role
from app.schemas.policy import Policy as PolicySchema, PolicyCreate, PolicyUpdate

router = APIRouter()

@router.get("/", response_model=List[PolicySchema])
async def get_policies(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve policies."""
    result = await db.execute(select(Policy).offset(skip).limit(limit))
    policies = result.scalars().all()
    return policies

@router.post("/", response_model=PolicySchema)
async def create_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_in: PolicyCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new policy."""
    # Check if policy already exists
    result = await db.execute(select(Policy).where(Policy.name == policy_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy already exists",
        )
    
    policy = Policy(
        name=policy_in.name,
        description=policy_in.description,
        effect=policy_in.effect,
        actions=policy_in.actions,
        resources=policy_in.resources,
        conditions=policy_in.conditions,
    )
    
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    
    return policy

@router.get("/{policy_id}", response_model=PolicySchema)
async def get_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get policy by ID."""
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    return policy

@router.put("/{policy_id}", response_model=PolicySchema)
async def update_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: str,
    policy_in: PolicyUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update policy."""
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    # Update policy attributes
    if policy_in.name is not None:
        policy.name = policy_in.name
    if policy_in.description is not None:
        policy.description = policy_in.description
    if policy_in.effect is not None:
        policy.effect = policy_in.effect
    if policy_in.actions is not None:
        policy.actions = policy_in.actions
    if policy_in.resources is not None:
        policy.resources = policy_in.resources
    if policy_in.conditions is not None:
        policy.conditions = policy_in.conditions
    
    await db.commit()
    await db.refresh(policy)
    
    return policy

@router.delete("/{policy_id}", response_model=PolicySchema)
async def delete_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete policy."""
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    await db.delete(policy)
    await db.commit()
    
    return policy

@router.post("/{policy_id}/assign/{role_id}", response_model=PolicySchema)
async def assign_policy_to_role(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: str,
    role_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Assign policy to role."""
    # Get policy
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    # Get role
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Assign policy to role
    if policy not in role.policies:
        role.policies.append(policy)
        await db.commit()
    
    return policy

@router.post("/{policy_id}/unassign/{role_id}", response_model=PolicySchema)
async def unassign_policy_from_role(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: str,
    role_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Unassign policy from role."""
    # Get policy
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    
    # Get role
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Unassign policy from role
    if policy in role.policies:
        role.policies.remove(policy)
        await db.commit()
    
    return policy 