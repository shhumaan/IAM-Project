from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
import enum

from app.db.base_class import Base

class AuditEventSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditEventType(str, enum.Enum):
    AUTH = "authentication"
    AUTHZ = "authorization"
    USER = "user_management"
    SYSTEM = "system"
    SECURITY = "security"
    ACCESS = "access_control"
    CONFIG = "configuration"
    AUDIT = "audit"

class AuditLog(Base):
    __table_args__ = (
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_event_type', 'event_type'),
        Index('idx_audit_logs_severity', 'severity'),
    )

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType), nullable=False)
    severity: Mapped[AuditEventSeverity] = mapped_column(Enum(AuditEventSeverity), nullable=False)
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("user.id"), nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    result: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    device_info: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    audit_metadata: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    hash: Mapped[str] = mapped_column(String, nullable=False)  # For tamper detection

    # Relationships
    user = relationship("User")

class AuditLogArchive(Base):
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    archive_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    start_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("user.id"))

    # Relationships
    creator = relationship("User")

class SecurityAlert(Base):
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    alert_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[AuditEventSeverity] = mapped_column(Enum(AuditEventSeverity), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("user.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("user.id"))

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    resolver = relationship("User", foreign_keys=[resolved_by])

class SystemMetric(Base):
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    metric_type: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    tags: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class HealthCheck(Base):
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    component: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    response_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) 