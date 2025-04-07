from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum
from app.models.audit import AuditLog, AuditLogArchive, SecurityAlert, SystemMetric

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

# SystemMetric class removed - now imported from audit.py 