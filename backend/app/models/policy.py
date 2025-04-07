"""Policy model for AzureShield IAM."""
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base


class Policy(Base):
    """Policy model for access control."""
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    effect: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "allow", "deny"
    actions: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    resources: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    conditions: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")
    assignments = relationship("PolicyAssignment", back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the Policy model."""
        return f"<Policy {self.name}>"


class PolicyVersion(Base):
    """Policy version model for versioning policies."""
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("policy.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Policy content
    effect: Mapped[str] = mapped_column(String(50), nullable=False)
    actions: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    resources: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    conditions: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    policy = relationship("Policy", back_populates="versions")
    
    def __repr__(self) -> str:
        """String representation of the PolicyVersion model."""
        return f"<PolicyVersion {self.policy.name} v{self.version}>"


class PolicyAssignment(Base):
    """Policy assignment model for assigning policies to users or groups."""
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("policy.id"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "user" or "group"
    target_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    policy = relationship("Policy", back_populates="assignments")
    
    def __repr__(self) -> str:
        """String representation of the PolicyAssignment model."""
        return f"<PolicyAssignment {self.policy.name} -> {self.target_type}:{self.target_id}>" 