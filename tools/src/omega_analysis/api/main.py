"""Main FastAPI application with middleware and routing configuration."""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os
import logging
from typing import Dict, Any

from omega_analysis.models.base import init_db, close_db
from omega_analysis.logging import setup_logging
from omega_analysis.tracing import setup_tracing
from omega_analysis.api.v1 import projects_router
from omega_analysis.api.analysis import analysis_router, architecture_router
from omega_analysis.api.reports import reports_router
from omega_analysis.api import health


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Setup tracing
setup_tracing()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Omega Analysis Engine...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Omega Analysis Engine...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Omega Analysis Engine",
    description="System Discovery and Baseline Assessment for Monolith-to-Microservices Migration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} in {process_time:.4f}s",
        extra={
            "status_code": response.status_code,
            "process_time": process_time,
        }
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
            "exception_type": type(exc).__name__,
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        }
    )


# Include routers
app.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

app.include_router(
    projects_router,
    prefix="/api/v1/projects",
    tags=["projects"]
)

app.include_router(
    analysis_router,
    prefix="/api/v1/analysis",
    tags=["analysis"]
)

app.include_router(
    architecture_router,
    prefix="/api/v1/architecture",
    tags=["architecture"]
)

app.include_router(
    reports_router,
    prefix="/api/v1/reports",
    tags=["reports"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Omega Analysis Engine",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/info")
async def app_info():
    """Application information endpoint."""
    return {
        "name": "Omega Analysis Engine",
        "version": "0.1.0",
        "description": "System Discovery and Baseline Assessment for Monolith-to-Microservices Migration",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": os.sys.version,
        "features": {
            "static_analysis": True,
            "runtime_analysis": True,
            "gap_analysis": True,
            "risk_assessment": True,
            "compliance_documentation": True,
        },
        "supported_systems": [
            "spring_boot",
            "spring_mvc", 
            "java_ee",
        ],
        "analysis_tools": [
            "context_mapper",
            "structurizr",
            "codeql",
            "microsoft_appcat",
            "signoz",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "omega_analysis.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )