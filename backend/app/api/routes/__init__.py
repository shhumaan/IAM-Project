"""API routes package for AzureShield IAM."""
from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.roles import router as roles_router
from app.api.routes.policies import router as policies_router
from app.api.routes.attributes import router as attributes_router
from app.api.routes.monitoring import router as monitoring_router
from app.api.routes.health import router as health_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_router.include_router(policies_router, prefix="/policies", tags=["policies"])
api_router.include_router(attributes_router, prefix="/attributes", tags=["attributes"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(health_router, prefix="/health", tags=["health"]) 