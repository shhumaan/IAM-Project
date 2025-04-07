"""Attribute models for AzureShield IAM."""
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AttributeDefinition(Base):
    """Attribute definition model for ABAC."""
    
    __tablename__ = "attribute_definition"
    
    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    data_type = Column(String(50), nullable=False)  # e.g., "string", "number", "boolean"
    is_required = Column(Boolean, default=False, nullable=False)
    is_multivalued = Column(Boolean, default=False, nullable=False)
    default_value = Column(String(255), nullable=True)
    
    # Relationships
    values = relationship("AttributeValue", back_populates="attribute_definition")
    
    def __repr__(self) -> str:
        """String representation of the AttributeDefinition model."""
        return f"<AttributeDefinition {self.name}>"


class AttributeValue(Base):
    """Attribute value model for ABAC."""
    
    __tablename__ = "attribute_value"
    
    id = Column(PGUUID, primary_key=True, default=uuid4)
    attribute_def_id = Column(PGUUID, ForeignKey("attribute_definition.id"), nullable=False, index=True)
    user_id = Column(PGUUID, ForeignKey("user.id"), nullable=True, index=True)
    value = Column(String(255), nullable=False)
    
    # Relationships
    attribute_definition = relationship("AttributeDefinition", back_populates="values")
    user = relationship("User", back_populates="attribute_values")
    
    def __repr__(self) -> str:
        """String representation of the AttributeValue model."""
        return f"<AttributeValue {self.attribute_definition.name}: {self.value}>" 