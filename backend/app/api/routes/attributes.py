"""Attribute management routes for AzureShield IAM."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_superuser, get_current_user, get_db
from app.models.attribute import AttributeDefinition, AttributeValue
from app.models.user import User
from app.schemas.attribute import (
    AttributeDefinition as AttributeDefinitionSchema,
    AttributeDefinitionCreate,
    AttributeDefinitionUpdate,
    AttributeValue as AttributeValueSchema,
    AttributeValueCreate,
    AttributeValueUpdate,
)

router = APIRouter()

# Attribute Definition routes
@router.get("/definitions", response_model=List[AttributeDefinitionSchema])
async def get_attribute_definitions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve attribute definitions."""
    result = await db.execute(select(AttributeDefinition).offset(skip).limit(limit))
    attribute_definitions = result.scalars().all()
    return attribute_definitions

@router.post("/definitions", response_model=AttributeDefinitionSchema)
async def create_attribute_definition(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_def_in: AttributeDefinitionCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new attribute definition."""
    # Check if attribute definition already exists
    result = await db.execute(
        select(AttributeDefinition).where(AttributeDefinition.name == attribute_def_in.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attribute definition already exists",
        )
    
    attribute_def = AttributeDefinition(
        name=attribute_def_in.name,
        description=attribute_def_in.description,
        data_type=attribute_def_in.data_type,
        is_required=attribute_def_in.is_required,
        is_multivalued=attribute_def_in.is_multivalued,
        default_value=attribute_def_in.default_value,
    )
    
    db.add(attribute_def)
    await db.commit()
    await db.refresh(attribute_def)
    
    return attribute_def

@router.get("/definitions/{attribute_def_id}", response_model=AttributeDefinitionSchema)
async def get_attribute_definition(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_def_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get attribute definition by ID."""
    result = await db.execute(
        select(AttributeDefinition).where(AttributeDefinition.id == attribute_def_id)
    )
    attribute_def = result.scalar_one_or_none()
    
    if not attribute_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute definition not found",
        )
    
    return attribute_def

@router.put("/definitions/{attribute_def_id}", response_model=AttributeDefinitionSchema)
async def update_attribute_definition(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_def_id: str,
    attribute_def_in: AttributeDefinitionUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update attribute definition."""
    result = await db.execute(
        select(AttributeDefinition).where(AttributeDefinition.id == attribute_def_id)
    )
    attribute_def = result.scalar_one_or_none()
    
    if not attribute_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute definition not found",
        )
    
    # Update attribute definition attributes
    if attribute_def_in.name is not None:
        attribute_def.name = attribute_def_in.name
    if attribute_def_in.description is not None:
        attribute_def.description = attribute_def_in.description
    if attribute_def_in.data_type is not None:
        attribute_def.data_type = attribute_def_in.data_type
    if attribute_def_in.is_required is not None:
        attribute_def.is_required = attribute_def_in.is_required
    if attribute_def_in.is_multivalued is not None:
        attribute_def.is_multivalued = attribute_def_in.is_multivalued
    if attribute_def_in.default_value is not None:
        attribute_def.default_value = attribute_def_in.default_value
    
    await db.commit()
    await db.refresh(attribute_def)
    
    return attribute_def

@router.delete("/definitions/{attribute_def_id}", response_model=AttributeDefinitionSchema)
async def delete_attribute_definition(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_def_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete attribute definition."""
    result = await db.execute(
        select(AttributeDefinition).where(AttributeDefinition.id == attribute_def_id)
    )
    attribute_def = result.scalar_one_or_none()
    
    if not attribute_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute definition not found",
        )
    
    await db.delete(attribute_def)
    await db.commit()
    
    return attribute_def

# Attribute Value routes
@router.get("/values", response_model=List[AttributeValueSchema])
async def get_attribute_values(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: str = None,
    attribute_def_id: str = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve attribute values."""
    query = select(AttributeValue)
    
    if user_id:
        query = query.where(AttributeValue.user_id == user_id)
    if attribute_def_id:
        query = query.where(AttributeValue.attribute_def_id == attribute_def_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    attribute_values = result.scalars().all()
    
    return attribute_values

@router.post("/values", response_model=AttributeValueSchema)
async def create_attribute_value(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_value_in: AttributeValueCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new attribute value."""
    # Check if attribute definition exists
    result = await db.execute(
        select(AttributeDefinition).where(AttributeDefinition.id == attribute_value_in.attribute_def_id)
    )
    attribute_def = result.scalar_one_or_none()
    
    if not attribute_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute definition not found",
        )
    
    # Check if user exists
    if attribute_value_in.user_id:
        result = await db.execute(
            select(User).where(User.id == attribute_value_in.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    
    # Check if attribute value already exists for this user and definition
    if attribute_value_in.user_id:
        result = await db.execute(
            select(AttributeValue).where(
                AttributeValue.attribute_def_id == attribute_value_in.attribute_def_id,
                AttributeValue.user_id == attribute_value_in.user_id,
            )
        )
        if result.scalar_one_or_none() and not attribute_def.is_multivalued:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attribute value already exists for this user and is not multivalued",
            )
    
    attribute_value = AttributeValue(
        attribute_def_id=attribute_value_in.attribute_def_id,
        user_id=attribute_value_in.user_id,
        value=attribute_value_in.value,
    )
    
    db.add(attribute_value)
    await db.commit()
    await db.refresh(attribute_value)
    
    return attribute_value

@router.get("/values/{attribute_value_id}", response_model=AttributeValueSchema)
async def get_attribute_value(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_value_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get attribute value by ID."""
    result = await db.execute(
        select(AttributeValue).where(AttributeValue.id == attribute_value_id)
    )
    attribute_value = result.scalar_one_or_none()
    
    if not attribute_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found",
        )
    
    return attribute_value

@router.put("/values/{attribute_value_id}", response_model=AttributeValueSchema)
async def update_attribute_value(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_value_id: str,
    attribute_value_in: AttributeValueUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update attribute value."""
    result = await db.execute(
        select(AttributeValue).where(AttributeValue.id == attribute_value_id)
    )
    attribute_value = result.scalar_one_or_none()
    
    if not attribute_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found",
        )
    
    # Update attribute value
    if attribute_value_in.value is not None:
        attribute_value.value = attribute_value_in.value
    
    await db.commit()
    await db.refresh(attribute_value)
    
    return attribute_value

@router.delete("/values/{attribute_value_id}", response_model=AttributeValueSchema)
async def delete_attribute_value(
    *,
    db: AsyncSession = Depends(get_db),
    attribute_value_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete attribute value."""
    result = await db.execute(
        select(AttributeValue).where(AttributeValue.id == attribute_value_id)
    )
    attribute_value = result.scalar_one_or_none()
    
    if not attribute_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found",
        )
    
    await db.delete(attribute_value)
    await db.commit()
    
    return attribute_value 