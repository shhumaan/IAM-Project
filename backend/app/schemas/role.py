"""Pydantic schemas for Role model."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class RoleBase(BaseModel):
    """Base schema for Role."""
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None

class RoleInDB(RoleBase):
    """Schema for Role in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class Role(RoleInDB):
    """Schema for Role response."""
    pass

class RoleWithUsers(Role):
    """Schema for Role with users."""
    users: List["User"] = [] 