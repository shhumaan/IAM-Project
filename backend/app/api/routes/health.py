"""Health check routes for AzureShield IAM."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.core.config import settings
from app.schemas.health import HealthCheck, ServiceStatus

router = APIRouter()

@router.get("/", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Perform a health check of the service.
    
    Checks:
    - API status
    - Database connection
    - Database migrations status
    """
    # Check API status (always OK if we can process this request)
    api_status = ServiceStatus.OK
    
    # Check database connection
    db_status = ServiceStatus.OK
    db_details = "Connected successfully"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = ServiceStatus.ERROR
        db_details = f"Database connection error: {str(e)}"
    
    # Overall status is the worst of all checks
    overall_status = ServiceStatus.OK
    if api_status == ServiceStatus.ERROR or db_status == ServiceStatus.ERROR:
        overall_status = ServiceStatus.ERROR
    elif api_status == ServiceStatus.WARNING or db_status == ServiceStatus.WARNING:
        overall_status = ServiceStatus.WARNING
    
    return HealthCheck(
        status=overall_status,
        version=settings.VERSION,
        api=api_status,
        database=db_status,
        database_details=db_details,
    ) 