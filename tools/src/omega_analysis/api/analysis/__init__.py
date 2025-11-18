"""Analysis module init."""
from .analysis import router as analysis_router
from .architecture import router as architecture_router
from .dependencies import router as dependencies_router
from .baselines import router as baselines_router

__all__ = ["analysis_router", "architecture_router", "dependencies_router", "baselines_router"]