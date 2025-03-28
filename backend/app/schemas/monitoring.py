from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.audit import AuditEventSeverity
from app.models.health import HealthStatus
from uuid import UUID

class ComponentHealth(BaseModel):
    name: str
    status: str
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    components: List[ComponentHealth]
    duration: float

class SystemMetricResponse(BaseModel):
    id: int
    timestamp: datetime
    metric_type: str
    value: float
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime

class SecurityAlertResponse(BaseModel):
    id: int
    timestamp: datetime
    alert_type: str
    severity: str
    description: str
    details: Optional[Dict[str, Any]] = None
    status: str
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    created_at: datetime

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    severity: str
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    result: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

class SystemStatusResponse(BaseModel):
    health_status: str
    components: List[ComponentHealth]
    recent_alerts: List[SecurityAlertResponse]
    critical_events: List[AuditLogResponse]
    metrics: List[SystemMetricResponse]
    timestamp: datetime

class HealthCheck(BaseModel):
    component: str
    status: str
    response_time: float
    details: Dict[str, Any]

class SystemMetricsResponse(BaseModel):
    metrics: List[SystemMetricResponse]
    timestamp: datetime

class SecurityAlert(BaseModel):
    alert_type: str
    severity: str
    description: str
    details: Optional[Dict[str, Any]] = None

class AuditLog(BaseModel):
    event_type: str
    severity: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    result: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class MonitoringConfig(BaseModel):
    enabled: bool = Field(..., description="Whether monitoring is enabled")
    check_interval: int = Field(..., description="Interval between health checks in seconds")
    metric_retention_days: int = Field(..., description="Number of days to retain metrics")
    alert_retention_days: int = Field(..., description="Number of days to retain alerts")
    critical_thresholds: Dict[str, float] = Field(..., description="Critical thresholds for various metrics")

class MonitoringStats(BaseModel):
    total_health_checks: int
    total_metrics: int
    total_alerts: int
    total_audit_logs: int
    last_check_time: Optional[datetime]
    average_response_time: float
    uptime_percentage: float

class AuditLogBase(BaseModel):
    """Base schema for AuditLog."""
    event_type: str
    severity: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    result: str
    details: Optional[Dict[str, Any]] = None
    hash: str

class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log."""
    user_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AuditLogInDB(AuditLogBase):
    """Schema for AuditLog in database."""
    id: UUID
    timestamp: datetime
    user_id: Optional[UUID] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class AuditLog(AuditLogInDB):
    """Schema for AuditLog response."""
    pass

class SecurityAlertBase(BaseModel):
    """Base schema for SecurityAlert."""
    alert_type: str
    severity: str
    description: str
    status: str

class SecurityAlertCreate(SecurityAlertBase):
    """Schema for creating a new security alert."""
    created_by: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SecurityAlertUpdate(BaseModel):
    """Schema for updating a security alert."""
    status: str
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None

class SecurityAlertInDB(SecurityAlertBase):
    """Schema for SecurityAlert in database."""
    id: UUID
    timestamp: datetime
    created_by: UUID
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class SecurityAlert(SecurityAlertInDB):
    """Schema for SecurityAlert response."""
    pass

class SystemMetricBase(BaseModel):
    """Base schema for SystemMetric."""
    metric_type: str
    value: float
    tags: Optional[Dict[str, Any]] = None

class SystemMetricCreate(SystemMetricBase):
    """Schema for creating a new system metric."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemMetricInDB(SystemMetricBase):
    """Schema for SystemMetric in database."""
    id: UUID
    timestamp: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class SystemMetric(SystemMetricInDB):
    """Schema for SystemMetric response."""
    pass

class HealthCheckBase(BaseModel):
    """Base schema for HealthCheck."""
    component: str
    status: str
    response_time: float
    details: Optional[Dict[str, Any]] = None

class HealthCheckCreate(HealthCheckBase):
    """Schema for creating a new health check."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthCheckInDB(HealthCheckBase):
    """Schema for HealthCheck in database."""
    id: UUID
    timestamp: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class HealthCheck(HealthCheckInDB):
    """Schema for HealthCheck response."""
    pass 