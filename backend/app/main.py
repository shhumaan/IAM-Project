"""
Main FastAPI application module for AzureShield IAM.
This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_client import make_asgi_app
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import oauth, mfa, policies, attributes, monitoring
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.error_handling import ErrorHandlingMiddleware

# Initialize logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="AzureShield IAM",
    description="Enterprise-grade Identity and Access Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(oauth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(mfa.router, prefix="/api/v1/auth/mfa", tags=["MFA"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
app.include_router(attributes.router, prefix="/api/v1/attributes", tags=["Attributes"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

# Error handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid input data",
            "details": exc.errors(),
        },
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AzureShield IAM application...")
    # Initialize database connection
    # Initialize Redis connection
    # Initialize other services

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AzureShield IAM application...")
    # Close database connection
    # Close Redis connection
    # Cleanup other resources 