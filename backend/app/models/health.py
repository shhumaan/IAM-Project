from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class HealthStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(HealthStatus), nullable=False)
    components = Column(JSON, nullable=False)
    duration = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<HealthCheck {self.id} {self.status} {self.timestamp}>"

class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<SystemMetric {self.id} {self.metric_type} {self.value}>"

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="open")
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    resolver = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self):
        return f"<SecurityAlert {self.id} {self.alert_type} {self.severity}>"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    result = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog {self.id} {self.event_type} {self.action}>"

class AuditLogArchive(Base):
    __tablename__ = "audit_log_archives"

    id = Column(Integer, primary_key=True, index=True)
    archive_date = Column(DateTime, nullable=False)
    file_path = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    hash_value = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLogArchive {self.id} {self.archive_date}>" 