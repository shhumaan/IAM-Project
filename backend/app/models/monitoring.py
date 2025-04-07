"""Monitoring and auditing models for AzureShield IAM."""
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Enum, JSON, Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from app.db.base_class import Base
from app.models.audit import AuditLog, SecurityAlert, SystemMetric

class AccessLog(Base):
    """Access log model for recording access attempts."""
    __tablename__ = "access_logs"

    id: UUID = Column(PGUUID, primary_key=True, default=uuid4)
    user_id = Column(PGUUID, ForeignKey("user.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)
    result = Column(String, nullable=False)  # "success", "denied", "error"
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="access_logs")

class HealthCheck(Base):
    """Health check model for recording system health."""
    __tablename__ = "health_checks"

    id: UUID = Column(PGUUID, primary_key=True, default=uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    component = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "healthy", "degraded", "unhealthy"
    response_time = Column(JSON, nullable=True)
    details = Column(JSONB, nullable=True) 