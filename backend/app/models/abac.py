from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.db.base_class import Base

class PolicyEffect(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"

class AttributeType(str, enum.Enum):
    USER = "user"
    RESOURCE = "resource"
    ENVIRONMENT = "environment"

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    effect = Column(Enum(PolicyEffect), nullable=False)
    conditions = Column(JSONB, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    resource_type = Column(String, nullable=False)
    priority = Column(Integer, default=0)

    # Relationships
    creator = relationship("User", back_populates="created_policies")
    assignments = relationship("PolicyAssignment", back_populates="policy", cascade="all, delete-orphan")
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")

class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    version = Column(Integer, nullable=False)
    conditions = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    comment = Column(String)

    # Relationships
    policy = relationship("Policy", back_populates="versions")
    creator = relationship("User")

class PolicyAssignment(Base):
    __tablename__ = "policy_assignments"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    resource_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    policy = relationship("Policy", back_populates="assignments")
    creator = relationship("User")

class AttributeDefinition(Base):
    __tablename__ = "attribute_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(AttributeType), nullable=False)
    description = Column(String)
    data_type = Column(String, nullable=False)
    validation_rules = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    creator = relationship("User")

class AttributeValue(Base):
    __tablename__ = "attribute_values"

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attribute_definitions.id"), nullable=False)
    entity_id = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    value = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    attribute = relationship("AttributeDefinition")
    creator = relationship("User")

class AccessDecisionLog(Base):
    __tablename__ = "access_decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True)
    evaluation_context = Column(JSONB)
    evaluation_result = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    location = Column(JSONB)
    device_info = Column(JSONB)

    # Relationships
    user = relationship("User")
    policy = relationship("Policy") 