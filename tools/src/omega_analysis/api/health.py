"""Health check endpoints."""
from fastapi import APIRouter, status
from datetime import datetime
import os

router = APIRouter()


@router.get(
    "/",
    summary="Basic health check",
    description="Returns basic health status of the application"
)
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "omega-analysis-engine",
        "version": "0.1.0"
    }


@router.get(
    "/ready",
    summary="Readiness check",
    description="Returns readiness status for Kubernetes/container orchestration"
)
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",  # TODO: Add actual database health check
            "cache": "ok",     # TODO: Add actual cache health check
            "storage": "ok"    # TODO: Add actual storage health check
        }
    }


@router.get(
    "/live",
    summary="Liveness check",
    description="Returns liveness status for Kubernetes/container orchestration"
)
async def liveness_check():
    """Liveness check endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "unknown",  # TODO: Track actual uptime
        "environment": os.getenv("ENVIRONMENT", "development")
    }