"""Core configuration module for AzureShield IAM."""
from typing import List, Dict, Any, Optional, Union
from pydantic import PostgresDsn, field_validator, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AzureShield IAM"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        """Assemble CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database Settings
    POSTGRES_SERVER: str = Field(..., description="PostgreSQL server host")
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        """Assemble database connection string."""
        if isinstance(v, str):
            return v
        values = info.data
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        """Assemble database URL."""
        if isinstance(v, str):
            # If it doesn't already have a +asyncpg part, add it for async operations
            if '+asyncpg' not in v and v.startswith('postgresql://'):
                return v.replace('postgresql://', 'postgresql+asyncpg://')
            return v
        values = info.data
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False
    
    # Security Settings
    SECRET_KEY: str = Field(..., description="Secret key for JWT token generation")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # MFA Settings
    MFA_ISSUER: str = "AzureShield IAM"
    MFA_VALIDITY_PERIOD: int = 30  # seconds
    
    # Monitoring Settings
    SENTRY_DSN: Optional[str] = None
    ENABLE_PROMETHEUS: bool = True
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Development Settings
    DEBUG: bool = False
    
    # Security
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 30
    
    # MFA Configuration
    MFA_ENABLED: bool = True
    MFA_REQUIRED_FOR_ADMIN: bool = True
    MFA_BACKUP_CODES_COUNT: int = 8
    
    # OAuth2 Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # IP Restrictions
    ALLOWED_IP_RANGES: List[str] = ["10.0.0.0/8", "192.168.0.0/16"]
    BLOCKED_IPS: List[str] = []
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Suspicious Activity Detection
    IMPOSSIBLE_TRAVEL_THRESHOLD_KM: float = 1000
    IMPOSSIBLE_TRAVEL_TIME_HOURS: int = 1
    UNUSUAL_TIME_THRESHOLD_HOURS: int = 6
    
    # GeoIP Configuration
    GEOIP_DATABASE_PATH: str = "GeoLite2-City.mmdb"
    GEOIP_FALLBACK_ENABLED: bool = True
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

    # Session Management
    SESSION_EXPIRE_DAYS: int = 30
    MAX_CONCURRENT_SESSIONS: int = 5

    # Audit Logging
    AUDIT_LOG_RETENTION_DAYS: int = 90
    AUDIT_LOG_ARCHIVE_DIR: str = "audit_logs"
    AUDIT_LOG_BATCH_SIZE: int = 100
    AUDIT_LOG_PROCESSING_INTERVAL: int = 1  # seconds
    AUDIT_LOG_HASH_ALGORITHM: str = "sha256"

    # Monitoring
    ENABLE_MONITORING: bool = True
    MONITORING_INTERVAL: int = 60  # seconds
    METRIC_RETENTION_DAYS: int = 30
    ALERT_RETENTION_DAYS: int = 90
    HEALTH_CHECK_INTERVAL: int = 300  # seconds
    CRITICAL_METRIC_THRESHOLDS: Dict[str, float] = {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "database_response_time": 1.0,
        "redis_response_time": 0.1
    }

    # Azure Monitor Integration
    AZURE_MONITOR_ENABLED: bool = False
    AZURE_MONITOR_CONNECTION_STRING: Optional[str] = None
    AZURE_MONITOR_INSTRUMENTATION_KEY: Optional[str] = None
    AZURE_MONITOR_ENDPOINT: Optional[str] = None

    # Application Insights
    APPINSIGHTS_ENABLED: bool = False
    APPINSIGHTS_INSTRUMENTATION_KEY: Optional[str] = None
    APPINSIGHTS_ENDPOINT: Optional[str] = None

    # Log Analytics
    LOG_ANALYTICS_ENABLED: bool = False
    LOG_ANALYTICS_WORKSPACE_ID: Optional[str] = None
    LOG_ANALYTICS_PRIMARY_KEY: Optional[str] = None
    LOG_ANALYTICS_ENDPOINT: Optional[str] = None

    # Scalability
    ENABLE_ASYNC_PROCESSING: bool = True
    MAX_WORKERS: int = 4
    WORKER_TIMEOUT: int = 300  # seconds
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800  # seconds
    REDIS_POOL_SIZE: int = 10
    REDIS_POOL_TIMEOUT: int = 20
    CACHE_TTL: int = 300  # seconds
    CACHE_PREFIX: str = "azureshield:"

    # High Availability
    ENABLE_CIRCUIT_BREAKER: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60  # seconds
    ENABLE_GRACEFUL_SHUTDOWN: bool = True
    SHUTDOWN_TIMEOUT: int = 30  # seconds
    HEALTH_CHECK_TIMEOUT: int = 5  # seconds
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1  # seconds

    # Background Tasks
    ENABLE_BACKGROUND_TASKS: bool = True
    MAX_BACKGROUND_TASKS: int = 10
    BACKGROUND_TASK_TIMEOUT: int = 300  # seconds
    TASK_QUEUE_SIZE: int = 1000

    # Azure AD Configuration
    AZURE_AD_TENANT_ID: Optional[str] = None
    AZURE_AD_CLIENT_ID: Optional[str] = None
    AZURE_AD_CLIENT_SECRET: Optional[str] = None
    AZURE_AD_AUTHORITY: Optional[str] = None

    @field_validator("AZURE_AD_AUTHORITY", mode="before")
    def assemble_azure_authority(cls, v: Optional[str], info: Dict[str, Any]) -> Optional[str]:
        if isinstance(v, str):
            return v
        values = info.data
        return f"https://login.microsoftonline.com/{values.get('AZURE_AD_TENANT_ID')}"

    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = Field(..., description="SMTP server host")
    SMTP_USER: str = Field(..., description="SMTP username")
    SMTP_PASSWORD: str = Field(..., description="SMTP password")
    EMAILS_FROM_EMAIL: str = Field(..., description="Email address to send from")
    EMAILS_FROM_NAME: str = Field(..., description="Name to send emails from")

# Create global settings instance
settings = Settings() 