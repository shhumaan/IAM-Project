"""Monitoring and audit models for AzureShield IAM."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Float, ForeignKey, Column, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

class AccessLog(BaseModel):
    """Access log model for tracking resource access attempts."""
    
    __tablename__ = "access_log"
    
    user_id = Column(String(36), ForeignKey("user.id"), nullable=True, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="access_logs")

class AuditLog(BaseModel):
    """Audit log model for tracking administrative actions."""
    
    __tablename__ = "audit_log"
    
    user_id = Column(String(36), ForeignKey("user.id"), nullable=True, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    previous_state = Column(JSONB, nullable=True)
    new_state = Column(JSONB, nullable=True)
    details = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class SecurityAlert(BaseModel):
    """Security alert model for tracking security incidents."""
    __tablename__ = "security_alerts"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    alert_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    resolved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="resolved_alerts",
        foreign_keys=[created_by]
    )
    resolved_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[resolved_by]
    )

    def __repr__(self) -> str:
        """String representation of the SecurityAlert model."""
        return f"<SecurityAlert {self.alert_type} - {self.severity}>"

class SystemMetric(BaseModel):
    """System metric model for tracking performance metrics."""
    __tablename__ = "system_metrics"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metric_type: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        """String representation of the SystemMetric model."""
        return f"<SystemMetric {self.metric_type} - {self.value}>"

class HealthCheck(BaseModel):
    """Health check model for monitoring system components."""
    __tablename__ = "health_checks"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    component: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        """String representation of the HealthCheck model."""
        return f"<HealthCheck {self.component} - {self.status}>" 