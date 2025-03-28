from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib
import asyncio
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import aiofiles
import os
from app.models.audit import (
    AuditLog,
    AuditLogArchive,
    AuditEventType,
    AuditEventSeverity,
    SecurityAlert,
    SystemMetric,
    HealthCheck
)
from app.core.config import settings
from app.core.cache import redis_client
from app.services.security import SecurityService

class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.security_service = SecurityService(db)
        self.log_queue = asyncio.Queue()
        self.archive_queue = asyncio.Queue()
        self.alert_queue = asyncio.Queue()
        self.metric_queue = asyncio.Queue()
        self.background_tasks = []

    async def start_background_tasks(self):
        """Start background tasks for log processing."""
        self.background_tasks.extend([
            asyncio.create_task(self._process_log_queue()),
            asyncio.create_task(self._process_archive_queue()),
            asyncio.create_task(self._process_alert_queue()),
            asyncio.create_task(self._process_metric_queue()),
            asyncio.create_task(self._check_log_rotation()),
            asyncio.create_task(self._monitor_system_health())
        ])

    async def stop_background_tasks(self):
        """Stop all background tasks."""
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditEventSeverity,
        action: str,
        result: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an audit event with tamper detection."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "result": result,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "location": location,
            "device_info": device_info,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "request_id": request_id,
            "metadata": metadata
        }

        # Generate tamper-resistant hash
        log_entry["hash"] = self._generate_hash(log_entry)

        # Add to processing queue
        await self.log_queue.put(log_entry)

        # Check for security events
        if severity in [AuditEventSeverity.SECURITY, AuditEventSeverity.CRITICAL]:
            await self._analyze_security_event(log_entry)

    def _generate_hash(self, log_entry: Dict[str, Any]) -> str:
        """Generate a tamper-resistant hash for the log entry."""
        # Create a copy without the hash field
        entry_copy = log_entry.copy()
        entry_copy.pop("hash", None)
        
        # Sort keys for consistent hashing
        sorted_entry = json.dumps(entry_copy, sort_keys=True)
        
        # Generate hash using SHA-256
        return hashlib.sha256(sorted_entry.encode()).hexdigest()

    async def _process_log_queue(self):
        """Process log entries from the queue."""
        while True:
            try:
                # Get batch of logs
                logs = []
                for _ in range(100):  # Process in batches of 100
                    try:
                        log = await asyncio.wait_for(self.log_queue.get(), timeout=1.0)
                        logs.append(log)
                    except asyncio.TimeoutError:
                        break

                if not logs:
                    await asyncio.sleep(1)
                    continue

                # Verify hashes and insert logs
                for log in logs:
                    if self._verify_hash(log):
                        db_log = AuditLog(**log)
                        self.db.add(db_log)
                
                self.db.commit()

            except Exception as e:
                self.db.rollback()
                print(f"Error processing log queue: {str(e)}")
                await asyncio.sleep(1)

    def _verify_hash(self, log_entry: Dict[str, Any]) -> bool:
        """Verify the tamper-resistant hash of a log entry."""
        stored_hash = log_entry.pop("hash")
        calculated_hash = self._generate_hash(log_entry)
        log_entry["hash"] = stored_hash
        return stored_hash == calculated_hash

    async def _process_archive_queue(self):
        """Process log archives from the queue."""
        while True:
            try:
                archive = await self.archive_queue.get()
                
                # Create archive file
                archive_path = os.path.join(
                    settings.AUDIT_LOG_ARCHIVE_DIR,
                    f"audit_logs_{archive['start_timestamp'].strftime('%Y%m%d')}.jsonl"
                )
                
                async with aiofiles.open(archive_path, 'w') as f:
                    for log in archive['logs']:
                        await f.write(json.dumps(log) + '\n')
                
                # Create archive record
                db_archive = AuditLogArchive(
                    archive_date=archive['start_timestamp'],
                    file_path=archive_path,
                    start_timestamp=archive['start_timestamp'],
                    end_timestamp=archive['end_timestamp'],
                    record_count=len(archive['logs']),
                    file_size=os.path.getsize(archive_path),
                    hash=self._generate_hash(archive),
                    created_by=archive['created_by']
                )
                
                self.db.add(db_archive)
                self.db.commit()

            except Exception as e:
                self.db.rollback()
                print(f"Error processing archive queue: {str(e)}")
                await asyncio.sleep(1)

    async def _check_log_rotation(self):
        """Check and rotate logs based on retention policy."""
        while True:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
                
                # Get logs to archive
                logs_to_archive = self.db.query(AuditLog).filter(
                    AuditLog.timestamp < cutoff_date
                ).all()
                
                if logs_to_archive:
                    # Group logs by date
                    logs_by_date = {}
                    for log in logs_to_archive:
                        date = log.timestamp.date()
                        if date not in logs_by_date:
                            logs_by_date[date] = []
                        logs_by_date[date].append(log)
                    
                    # Create archive entries
                    for date, logs in logs_by_date.items():
                        archive = {
                            'start_timestamp': datetime.combine(date, datetime.min.time()),
                            'end_timestamp': datetime.combine(date, datetime.max.time()),
                            'logs': [log.__dict__ for log in logs],
                            'created_by': 1  # System user
                        }
                        await self.archive_queue.put(archive)
                    
                    # Delete archived logs
                    for log in logs_to_archive:
                        self.db.delete(log)
                    self.db.commit()

            except Exception as e:
                self.db.rollback()
                print(f"Error checking log rotation: {str(e)}")
            
            await asyncio.sleep(3600)  # Check every hour

    async def _analyze_security_event(self, log_entry: Dict[str, Any]) -> None:
        """Analyze security events and generate alerts."""
        try:
            # Check for suspicious patterns
            if self._is_suspicious_event(log_entry):
                alert = {
                    'alert_type': 'suspicious_activity',
                    'severity': log_entry['severity'],
                    'description': f"Suspicious activity detected: {log_entry['action']}",
                    'details': log_entry,
                    'created_by': 1  # System user
                }
                await self.alert_queue.put(alert)

        except Exception as e:
            print(f"Error analyzing security event: {str(e)}")

    def _is_suspicious_event(self, log_entry: Dict[str, Any]) -> bool:
        """Check if an event is suspicious."""
        # Implement suspicious activity detection logic
        suspicious_patterns = [
            {'event_type': AuditEventType.AUTH, 'result': 'failure', 'count': 5},
            {'event_type': AuditEventType.AUTHZ, 'result': 'deny', 'count': 3},
            {'event_type': AuditEventType.SECURITY, 'severity': AuditEventSeverity.CRITICAL}
        ]
        
        for pattern in suspicious_patterns:
            if all(log_entry.get(k) == v for k, v in pattern.items() if k != 'count'):
                # Check frequency in Redis
                key = f"suspicious:{pattern['event_type']}:{log_entry.get('user_id')}"
                count = redis_client.incr(key)
                if count >= pattern['count']:
                    return True
        
        return False

    async def _process_alert_queue(self):
        """Process security alerts from the queue."""
        while True:
            try:
                alert = await self.alert_queue.get()
                
                # Create alert record
                db_alert = SecurityAlert(**alert)
                self.db.add(db_alert)
                self.db.commit()
                
                # Send notifications
                await self._send_alert_notifications(db_alert)

            except Exception as e:
                self.db.rollback()
                print(f"Error processing alert queue: {str(e)}")
                await asyncio.sleep(1)

    async def _send_alert_notifications(self, alert: SecurityAlert) -> None:
        """Send notifications for security alerts."""
        # Implement notification logic (email, SMS, etc.)
        pass

    async def _process_metric_queue(self):
        """Process system metrics from the queue."""
        while True:
            try:
                metric = await self.metric_queue.get()
                
                # Create metric record
                db_metric = SystemMetric(**metric)
                self.db.add(db_metric)
                self.db.commit()
                
                # Check thresholds and generate alerts
                await self._check_metric_thresholds(db_metric)

            except Exception as e:
                self.db.rollback()
                print(f"Error processing metric queue: {str(e)}")
                await asyncio.sleep(1)

    async def _check_metric_thresholds(self, metric: SystemMetric) -> None:
        """Check metric values against thresholds and generate alerts."""
        # Implement threshold checking logic
        pass

    async def _monitor_system_health(self):
        """Monitor system health and record metrics."""
        while True:
            try:
                # Check database health
                db_health = await self._check_database_health()
                await self.metric_queue.put({
                    'metric_type': 'database_health',
                    'value': db_health,
                    'tags': {'component': 'database'}
                })
                
                # Check Redis health
                redis_health = await self._check_redis_health()
                await self.metric_queue.put({
                    'metric_type': 'redis_health',
                    'value': redis_health,
                    'tags': {'component': 'redis'}
                })
                
                # Check application health
                app_health = await self._check_application_health()
                await self.metric_queue.put({
                    'metric_type': 'application_health',
                    'value': app_health,
                    'tags': {'component': 'application'}
                })

            except Exception as e:
                print(f"Error monitoring system health: {str(e)}")
            
            await asyncio.sleep(60)  # Check every minute

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            start_time = datetime.utcnow()
            self.db.execute("SELECT 1")
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            start_time = datetime.utcnow()
            await redis_client.ping()
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _check_application_health(self) -> Dict[str, Any]:
        """Check application health."""
        return {
            'status': 'healthy',
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage(),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        import psutil
        return psutil.Process().memory_percent()

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        import psutil
        return psutil.Process().cpu_percent() 