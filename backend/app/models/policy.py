"""Policy model for AzureShield IAM."""
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Policy(BaseModel):
    """Policy model for access control."""
    
    __tablename__ = "policy"
    
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    effect = Column(String(50), nullable=False)  # e.g., "allow", "deny"
    actions = Column(JSONB, nullable=False)
    resources = Column(JSONB, nullable=False)
    conditions = Column(JSONB, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary="role_policy", back_populates="policies")
    
    def __repr__(self) -> str:
        """String representation of the Policy model."""
        return f"<Policy {self.name}>" 