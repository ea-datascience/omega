"""Analysis module init."""
from .analysis import router as analysis_router
from .architecture import router as architecture_router

__all__ = ["analysis_router", "architecture_router"]