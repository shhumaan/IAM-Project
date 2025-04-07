"""Dependencies for API routes."""
from app.dependencies import get_db, get_current_user, get_current_active_superuser

__all__ = ["get_db", "get_current_user", "get_current_active_superuser"] 