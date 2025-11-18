"""API v1 module."""
from .projects import router as projects_router

__all__ = ["projects_router"]