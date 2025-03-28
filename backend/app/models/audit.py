from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
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
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_event_type', 'event_type'),
        Index('idx_audit_logs_severity', 'severity'),
    )

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(Enum(AuditEventType), nullable=False)
    severity = Column(Enum(AuditEventSeverity), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    result = Column(String, nullable=False)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    location = Column(JSONB, nullable=True)
    device_info = Column(JSONB, nullable=True)
    session_id = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)
    request_id = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)
    hash = Column(String, nullable=False)  # For tamper detection

    # Relationships
    user = relationship("User")

class AuditLogArchive(Base):
    __tablename__ = "audit_log_archives"

    id = Column(Integer, primary_key=True, index=True)
    archive_date = Column(DateTime, nullable=False)
    file_path = Column(String, nullable=False)
    start_timestamp = Column(DateTime, nullable=False)
    end_timestamp = Column(DateTime, nullable=False)
    record_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(Enum(AuditEventSeverity), nullable=False)
    description = Column(String, nullable=False)
    details = Column(JSONB, nullable=True)
    status = Column(String, nullable=False, default="open")
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    resolver = relationship("User", foreign_keys=[resolved_by])

class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(JSONB, nullable=False)
    tags = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    component = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response_time = Column(Integer, nullable=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 