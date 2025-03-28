from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import text
from redis import Redis
from app.core.config import settings
from app.models.health import HealthCheck, SystemMetric

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"

@dataclass
class ComponentHealth:
    name: str
    status: ComponentStatus
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime

class HealthService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self._running = False
        self._last_check: Optional[datetime] = None

    async def start_monitoring(self) -> None:
        """Start the health monitoring service."""
        if not settings.ENABLE_MONITORING:
            logger.warning("Health monitoring is disabled")
            return

        self._running = True
        asyncio.create_task(self._monitor_health())
        logger.info("Health monitoring service started")

    async def stop_monitoring(self) -> None:
        """Stop the health monitoring service."""
        self._running = False
        logger.info("Health monitoring service stopped")

    async def check_health(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of all system components."""
        start_time = datetime.utcnow()
        components: List[ComponentHealth] = []

        # Check database
        db_health = await self._check_database()
        components.append(db_health)

        # Check Redis
        redis_health = await self._check_redis()
        components.append(redis_health)

        # Check system resources
        system_health = await self._check_system_resources()
        components.append(system_health)

        # Calculate overall status
        overall_status = self._calculate_overall_status(components)
        
        # Record health check
        health_check = HealthCheck(
            timestamp=start_time,
            status=overall_status.value,
            components=[c.__dict__ for c in components],
            duration=(datetime.utcnow() - start_time).total_seconds()
        )
        self.db.add(health_check)
        self.db.commit()

        return {
            "status": overall_status.value,
            "timestamp": start_time.isoformat(),
            "components": [c.__dict__ for c in components],
            "duration": (datetime.utcnow() - start_time).total_seconds()
        }

    async def _check_database(self) -> ComponentHealth:
        """Check database health."""
        start_time = datetime.utcnow()
        try:
            # Test database connection
            self.db.execute(text("SELECT 1"))
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Check connection pool
            pool_status = self.db.get_bind().pool.status()
            
            return ComponentHealth(
                name="database",
                status=ComponentStatus.HEALTHY,
                response_time=response_time,
                details={
                    "pool_size": pool_status.size,
                    "checkedin": pool_status.checkedin,
                    "overflow": pool_status.overflow,
                    "checkedout": pool_status.checkedout
                },
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return ComponentHealth(
                name="database",
                status=ComponentStatus.UNHEALTHY,
                response_time=(datetime.utcnow() - start_time).total_seconds(),
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    async def _check_redis(self) -> ComponentHealth:
        """Check Redis health."""
        start_time = datetime.utcnow()
        try:
            # Test Redis connection
            self.redis.ping()
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Get Redis info
            info = self.redis.info()
            
            return ComponentHealth(
                name="redis",
                status=ComponentStatus.HEALTHY,
                response_time=response_time,
                details={
                    "connected_clients": info.get("connected_clients"),
                    "used_memory": info.get("used_memory"),
                    "uptime_in_seconds": info.get("uptime_in_seconds")
                },
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return ComponentHealth(
                name="redis",
                status=ComponentStatus.UNHEALTHY,
                response_time=(datetime.utcnow() - start_time).total_seconds(),
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    async def _check_system_resources(self) -> ComponentHealth:
        """Check system resource usage."""
        start_time = datetime.utcnow()
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = ComponentStatus.HEALTHY
            if cpu_percent > settings.CRITICAL_METRIC_THRESHOLDS["cpu_usage"] or \
               memory.percent > settings.CRITICAL_METRIC_THRESHOLDS["memory_usage"]:
                status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="system",
                status=status,
                response_time=(datetime.utcnow() - start_time).total_seconds(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                },
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"System resources health check failed: {str(e)}")
            return ComponentHealth(
                name="system",
                status=ComponentStatus.UNKNOWN,
                response_time=(datetime.utcnow() - start_time).total_seconds(),
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    def _calculate_overall_status(self, components: List[ComponentHealth]) -> ComponentStatus:
        """Calculate overall system status based on component statuses."""
        if any(c.status == ComponentStatus.UNHEALTHY for c in components):
            return ComponentStatus.UNHEALTHY
        elif any(c.status == ComponentStatus.DEGRADED for c in components):
            return ComponentStatus.DEGRADED
        elif all(c.status == ComponentStatus.HEALTHY for c in components):
            return ComponentStatus.HEALTHY
        return ComponentStatus.UNKNOWN

    async def _monitor_health(self) -> None:
        """Monitor system health periodically."""
        while self._running:
            try:
                await self.check_health()
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(5)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current health metrics."""
        return {
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "is_monitoring": self._running,
            "check_interval": settings.HEALTH_CHECK_INTERVAL
        } 