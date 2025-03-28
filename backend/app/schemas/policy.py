"""Pydantic schemas for Policy models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.abac import PolicyEffect
from uuid import UUID

class PolicyBase(BaseModel):
    """Base schema for Policy."""
    name: str
    description: Optional[str] = None
    effect: PolicyEffect
    conditions: Dict[str, Any]
    resource_type: str
    priority: int = Field(default=0, ge=0)

class PolicyCreate(PolicyBase):
    """Schema for creating a new policy."""
    rules: Dict[str, Any]

class PolicyUpdate(BaseModel):
    """Schema for updating a policy."""
    name: Optional[str] = None
    description: Optional[str] = None
    effect: Optional[PolicyEffect] = None
    conditions: Optional[Dict[str, Any]] = None
    resource_type: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class PolicyInDB(PolicyBase):
    """Schema for Policy in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class Policy(PolicyInDB):
    """Schema for Policy response."""
    pass

class PolicyVersionBase(BaseModel):
    """Base schema for PolicyVersion."""
    version: int
    rules: Dict[str, Any]

class PolicyVersionCreate(PolicyVersionBase):
    """Schema for creating a new policy version."""
    policy_id: UUID

class PolicyVersionInDB(PolicyVersionBase):
    """Schema for PolicyVersion in database."""
    id: UUID
    policy_id: UUID
    created_at: datetime
    created_by: UUID

    class Config:
        """Pydantic config."""
        from_attributes = True

class PolicyVersion(PolicyVersionInDB):
    """Schema for PolicyVersion response."""
    pass

class PolicyAssignmentBase(BaseModel):
    """Base schema for PolicyAssignment."""
    resource_type: str
    resource_id: str

class PolicyAssignmentCreate(PolicyAssignmentBase):
    """Schema for creating a new policy assignment."""
    policy_id: UUID

class PolicyAssignmentInDB(PolicyAssignmentBase):
    """Schema for PolicyAssignment in database."""
    id: UUID
    policy_id: UUID
    created_at: datetime
    created_by: UUID

    class Config:
        """Pydantic config."""
        from_attributes = True

class PolicyAssignment(PolicyAssignmentInDB):
    """Schema for PolicyAssignment response."""
    pass

class PolicyWithVersions(Policy):
    """Schema for Policy with versions."""
    versions: List[PolicyVersion] = []

class PolicyWithAssignments(Policy):
    """Schema for Policy with assignments."""
    assignments: List[PolicyAssignment] = []

class PolicyResponse(PolicyBase):
    id: int
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        orm_mode = True

class PolicyTestRequest(BaseModel):
    policy_id: int
    context: Dict[str, Any]

class PolicyTestResponse(BaseModel):
    policy_id: int
    decision: bool
    context: Dict[str, Any]

class AttributeDefinitionBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    data_type: str
    validation_rules: Optional[Dict[str, Any]] = None

class AttributeDefinitionCreate(AttributeDefinitionBase):
    pass

class AttributeDefinitionResponse(AttributeDefinitionBase):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int

    class Config:
        orm_mode = True

class AttributeValueBase(BaseModel):
    attribute_id: int
    entity_id: str
    entity_type: str
    value: Dict[str, Any]
    expires_at: Optional[datetime] = None

class AttributeValueCreate(AttributeValueBase):
    pass

class AttributeValueResponse(AttributeValueBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        orm_mode = True

class AccessDecisionLogResponse(BaseModel):
    id: int
    user_id: int
    resource_id: str
    resource_type: str
    action: str
    decision: str
    policy_id: Optional[int]
    evaluation_context: Dict[str, Any]
    evaluation_result: Dict[str, Any]
    created_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    location: Optional[Dict[str, Any]]
    device_info: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True 