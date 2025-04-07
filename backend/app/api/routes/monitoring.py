from typing import List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.health import HealthCheck, SystemMetric
from app.models.audit import AuditLog, SecurityAlert
from app.models.monitoring import AccessLog
from app.models.user import User
from app.schemas.monitoring import (
    HealthCheckResponse,
    SystemMetricsResponse,
    SecurityAlertResponse,
    AuditLogResponse,
    SystemStatusResponse,
    MonitoringConfig,
    MonitoringStats,
    AccessLog as AccessLogSchema,
    AccessLogCreate,
    UsageMetrics,
)
from app.services.health import HealthService
from app.core.task_manager import task_manager
from app.dependencies import get_current_active_superuser, get_current_user, get_db

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
async def check_health(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis: Session = Depends(get_redis)
):
    """Check the health status of all system components."""
    health_service = HealthService(db, redis)
    return await health_service.check_health()

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_metrics(
    metric_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get system metrics with optional filtering."""
    query = db.query(SystemMetric)
    
    if metric_type:
        query = query.filter(SystemMetric.metric_type == metric_type)
    if start_time:
        query = query.filter(SystemMetric.timestamp >= start_time)
    if end_time:
        query = query.filter(SystemMetric.timestamp <= end_time)
    
    metrics = query.order_by(desc(SystemMetric.timestamp)).limit(100).all()
    return SystemMetricsResponse(metrics=metrics, timestamp=datetime.utcnow())

@router.get("/alerts", response_model=List[SecurityAlertResponse])
async def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get security alerts with optional filtering."""
    query = db.query(SecurityAlert)
    
    if status:
        query = query.filter(SecurityAlert.status == status)
    if severity:
        query = query.filter(SecurityAlert.severity == severity)
    if start_time:
        query = query.filter(SecurityAlert.timestamp >= start_time)
    if end_time:
        query = query.filter(SecurityAlert.timestamp <= end_time)
    
    return query.order_by(desc(SecurityAlert.timestamp)).limit(100).all()

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering."""
    query = db.query(AuditLog)
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_time:
        query = query.filter(AuditLog.timestamp >= start_time)
    if end_time:
        query = query.filter(AuditLog.timestamp <= end_time)
    
    return query.order_by(desc(AuditLog.timestamp)).limit(100).all()

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    db: Session = Depends(get_db),
    redis: Session = Depends(get_redis)
):
    """Get comprehensive system status including health, alerts, and metrics."""
    health_service = HealthService(db, redis)
    health_status = await health_service.check_health()
    
    # Get recent alerts
    recent_alerts = db.query(SecurityAlert).order_by(
        desc(SecurityAlert.timestamp)
    ).limit(5).all()
    
    # Get critical events
    critical_events = db.query(AuditLog).filter(
        AuditLog.severity == "CRITICAL"
    ).order_by(desc(AuditLog.timestamp)).limit(5).all()
    
    # Get recent metrics
    recent_metrics = db.query(SystemMetric).order_by(
        desc(SystemMetric.timestamp)
    ).limit(10).all()
    
    return SystemStatusResponse(
        health_status=health_status["status"],
        components=health_status["components"],
        recent_alerts=recent_alerts,
        critical_events=critical_events,
        metrics=recent_metrics,
        timestamp=datetime.utcnow()
    )

@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlertResponse)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve a security alert."""
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    
    # Log the resolution
    audit_log = AuditLog(
        event_type="ALERT_RESOLUTION",
        severity="INFO",
        user_id=current_user.id,
        action="resolve_alert",
        resource_type="security_alert",
        resource_id=str(alert_id),
        result="success",
        details={"alert_type": alert.alert_type, "severity": alert.severity}
    )
    db.add(audit_log)
    db.commit()
    
    return alert

@router.post("/health-check", response_model=HealthCheckResponse)
async def trigger_health_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis: Session = Depends(get_redis)
):
    """Trigger a manual health check."""
    health_service = HealthService(db, redis)
    return await health_service.check_health()

@router.get("/config", response_model=MonitoringConfig)
async def get_monitoring_config():
    """Get current monitoring configuration."""
    return MonitoringConfig(
        enabled=settings.ENABLE_MONITORING,
        check_interval=settings.HEALTH_CHECK_INTERVAL,
        metric_retention_days=settings.METRIC_RETENTION_DAYS,
        alert_retention_days=settings.ALERT_RETENTION_DAYS,
        critical_thresholds=settings.CRITICAL_METRIC_THRESHOLDS
    )

@router.get("/stats", response_model=MonitoringStats)
async def get_monitoring_stats(
    db: Session = Depends(get_db)
):
    """Get monitoring statistics."""
    # Get total counts
    total_health_checks = db.query(HealthCheck).count()
    total_metrics = db.query(SystemMetric).count()
    total_alerts = db.query(SecurityAlert).count()
    total_audit_logs = db.query(AuditLog).count()
    
    # Get last check time
    last_check = db.query(HealthCheck).order_by(
        desc(HealthCheck.timestamp)
    ).first()
    last_check_time = last_check.timestamp if last_check else None
    
    # Calculate average response time
    recent_checks = db.query(HealthCheck).filter(
        HealthCheck.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).all()
    avg_response_time = sum(c.duration for c in recent_checks) / len(recent_checks) if recent_checks else 0
    
    # Calculate uptime percentage
    total_checks = db.query(HealthCheck).count()
    healthy_checks = db.query(HealthCheck).filter(
        HealthCheck.status == "HEALTHY"
    ).count()
    uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
    
    return MonitoringStats(
        total_health_checks=total_health_checks,
        total_metrics=total_metrics,
        total_alerts=total_alerts,
        total_audit_logs=total_audit_logs,
        last_check_time=last_check_time,
        average_response_time=avg_response_time,
        uptime_percentage=uptime_percentage
    )

# Access Logs routes
@router.get("/access-logs", response_model=List[AccessLogSchema])
async def get_access_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get access logs with optional filtering."""
    query = select(AccessLog)
    
    if user_id:
        query = query.where(AccessLog.user_id == user_id)
    if resource_id:
        query = query.where(AccessLog.resource_id == resource_id)
    if resource_type:
        query = query.where(AccessLog.resource_type == resource_type)
    if action:
        query = query.where(AccessLog.action == action)
    if status:
        query = query.where(AccessLog.status == status)
    if start_date:
        query = query.where(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.where(AccessLog.timestamp <= end_date)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    access_logs = result.scalars().all()
    
    return access_logs

@router.post("/access-logs", response_model=AccessLogSchema)
async def create_access_log(
    *,
    db: AsyncSession = Depends(get_db),
    access_log_in: AccessLogCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new access log entry."""
    access_log = AccessLog(
        user_id=current_user.id,
        resource_id=access_log_in.resource_id,
        resource_type=access_log_in.resource_type,
        action=access_log_in.action,
        status=access_log_in.status,
        ip_address=access_log_in.ip_address,
        user_agent=access_log_in.user_agent,
        details=access_log_in.details,
    )
    db.add(access_log)
    await db.commit()
    await db.refresh(access_log)
    return access_log

@router.get("/audit-logs", response_model=List[AuditLogSchema])
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Get audit logs with optional filtering."""
    query = select(AuditLog)
    
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if action:
        query = query.where(AuditLog.action == action)
    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    return audit_logs

@router.post("/audit-logs", response_model=AuditLogSchema)
async def create_audit_log(
    *,
    db: AsyncSession = Depends(get_db),
    audit_log_in: AuditLogCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create a new audit log entry."""
    audit_log = AuditLog(
        user_id=current_user.id,
        entity_id=audit_log_in.entity_id,
        entity_type=audit_log_in.entity_type,
        action=audit_log_in.action,
        previous_state=audit_log_in.previous_state,
        new_state=audit_log_in.new_state,
        details=audit_log_in.details,
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log

@router.get("/metrics/usage", response_model=UsageMetrics)
async def get_usage_metrics(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Get usage metrics for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get access log counts by day
    access_log_counts = await db.execute(
        select(
            func.date_trunc('day', AccessLog.timestamp).label('day'),
            func.count().label('count')
        )
        .where(AccessLog.timestamp >= start_date)
        .group_by('day')
        .order_by('day')
    )
    access_log_counts = access_log_counts.all()
    
    # Get audit log counts by day
    audit_log_counts = await db.execute(
        select(
            func.date_trunc('day', AuditLog.timestamp).label('day'),
            func.count().label('count')
        )
        .where(AuditLog.timestamp >= start_date)
        .group_by('day')
        .order_by('day')
    )
    audit_log_counts = audit_log_counts.all()
    
    # Get alert counts by day
    alert_counts = await db.execute(
        select(
            func.date_trunc('day', SecurityAlert.timestamp).label('day'),
            func.count().label('count')
        )
        .where(SecurityAlert.timestamp >= start_date)
        .group_by('day')
        .order_by('day')
    )
    alert_counts = alert_counts.all()
    
    return UsageMetrics(
        access_log_counts=access_log_counts,
        audit_log_counts=audit_log_counts,
        alert_counts=alert_counts,
        start_date=start_date,
        end_date=datetime.utcnow()
    ) 