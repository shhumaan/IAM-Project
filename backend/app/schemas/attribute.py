"""Pydantic schemas for Attribute models."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

class AttributeDefinitionBase(BaseModel):
    """Base schema for AttributeDefinition."""
    name: str
    description: Optional[str] = None
    data_type: str
    is_required: bool = False

class AttributeDefinitionCreate(AttributeDefinitionBase):
    """Schema for creating a new attribute definition."""
    pass

class AttributeDefinitionUpdate(BaseModel):
    """Schema for updating an attribute definition."""
    name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    is_required: Optional[bool] = None

class AttributeDefinitionInDB(AttributeDefinitionBase):
    """Schema for AttributeDefinition in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class AttributeDefinition(AttributeDefinitionInDB):
    """Schema for AttributeDefinition response."""
    pass

class AttributeValueBase(BaseModel):
    """Base schema for AttributeValue."""
    entity_type: str
    entity_id: str
    value: Dict[str, Any]

class AttributeValueCreate(AttributeValueBase):
    """Schema for creating a new attribute value."""
    definition_id: UUID

class AttributeValueUpdate(BaseModel):
    """Schema for updating an attribute value."""
    value: Dict[str, Any]

class AttributeValueInDB(AttributeValueBase):
    """Schema for AttributeValue in database."""
    id: UUID
    definition_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class AttributeValue(AttributeValueInDB):
    """Schema for AttributeValue response."""
    pass

class AttributeDefinitionWithValues(AttributeDefinition):
    """Schema for AttributeDefinition with values."""
    values: List[AttributeValue] = [] 