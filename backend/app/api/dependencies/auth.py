"""Authentication dependencies for API routes."""
from app.dependencies import get_current_user, get_current_active_superuser

# Re-export authentication dependencies from main dependencies module
__all__ = ["get_current_user", "get_current_active_superuser"] 