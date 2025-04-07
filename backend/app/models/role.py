"""Role model for AzureShield IAM."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association table for Role-Permission relationship
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", PGUUID, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", PGUUID, ForeignKey("permissions.id"), primary_key=True),
)

class Role(Base):
    """Role model representing an IAM role."""
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_role",
        back_populates="roles",
        lazy="selectin"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permission,
        back_populates="roles",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation of the Role model."""
        return f"<Role {self.name}>"

class Permission(Base):
    """Permission model representing an IAM permission."""
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permission,
        back_populates="permissions",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation of the Permission model."""
        return f"<Permission {self.name}>" 