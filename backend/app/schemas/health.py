"""Health schemas for AzureShield IAM."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ServiceStatus(str, Enum):
    """Service status enum."""
    
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class HealthCheck(BaseModel):
    """Health check response schema."""
    
    status: ServiceStatus
    version: str
    api: ServiceStatus
    database: ServiceStatus
    database_details: Optional[str] = None 