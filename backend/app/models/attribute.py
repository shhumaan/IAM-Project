"""Attribute models for AzureShield IAM."""
from typing import List, Optional

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class AttributeDefinition(BaseModel):
    """Attribute definition model for ABAC."""
    
    __tablename__ = "attribute_definition"
    
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


class AttributeValue(BaseModel):
    """Attribute value model for ABAC."""
    
    __tablename__ = "attribute_value"
    
    attribute_def_id = Column(String(36), ForeignKey("attribute_definition.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=True, index=True)
    value = Column(String(255), nullable=False)
    
    # Relationships
    attribute_definition = relationship("AttributeDefinition", back_populates="values")
    user = relationship("User", back_populates="attribute_values")
    
    def __repr__(self) -> str:
        """String representation of the AttributeValue model."""
        return f"<AttributeValue {self.attribute_definition.name}: {self.value}>" 