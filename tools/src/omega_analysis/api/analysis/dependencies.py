"""
Dependency Graph Retrieval API Endpoints.

This module provides REST API endpoints for retrieving dependency analysis results,
including static code dependencies, runtime communication patterns, and combined views.
Supports filtering by graph type (static, runtime, combined).
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models (Schemas)
# ============================================================================


class DependencyGraph(BaseModel):
    """
    Complete dependency graph for a system analysis.
    
    Includes static code dependencies, runtime communication patterns,
    coupling metrics, and circular dependency detection.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "analysis_project_id": "123e4567-e89b-12d3-a456-426614174000",
                "graph_type": "combined",
                "nodes": {
                    "modules": [
                        {"id": "order-service", "type": "module", "size": 5400},
                        {"id": "payment-service", "type": "module", "size": 3200}
                    ]
                },
                "edges": {
                    "dependencies": [
                        {
                            "source": "order-service",
                            "target": "payment-service",
                            "type": "static",
                            "weight": 12
                        }
                    ]
                },
                "coupling_metrics": {
                    "afferent_coupling": {"order-service": 3, "payment-service": 8},
                    "efferent_coupling": {"order-service": 8, "payment-service": 2},
                    "instability": {"order-service": 0.73, "payment-service": 0.2}
                },
                "external_dependencies": {
                    "libraries": ["spring-boot", "hibernate", "jackson"],
                    "services": ["stripe-api", "sendgrid-api"]
                },
                "data_dependencies": {
                    "database_schemas": ["orders", "payments", "customers"],
                    "shared_tables": ["customers"]
                },
                "circular_dependencies": {
                    "cycles": [
                        {"path": ["order-service", "inventory-service", "order-service"], "severity": "high"}
                    ]
                },
                "critical_path_analysis": {
                    "longest_paths": [
                        {"path": ["ui", "order-service", "payment-service", "database"], "length": 4}
                    ]
                },
                "confidence_score": 0.87,
                "generated_at": "2025-11-18T12:00:00Z",
                "validation_status": "validated"
            }
        }
    )
    
    id: UUID = Field(description="Unique identifier for this dependency graph")
    analysis_project_id: UUID = Field(description="ID of the analysis project this graph belongs to")
    graph_type: str = Field(description="Type of dependency graph", pattern="^(static|runtime|combined)$")
    nodes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph nodes representing modules, services, or databases"
    )
    edges: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph edges representing dependencies and communications"
    )
    coupling_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Coupling strength measurements (afferent, efferent, instability)"
    )
    external_dependencies: Optional[Dict[str, Any]] = Field(
        default=None,
        description="External system integrations (libraries, APIs, services)"
    )
    data_dependencies: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Database schemas and data flow dependencies"
    )
    circular_dependencies: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Circular dependency cycles with severity ratings"
    )
    critical_path_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Critical dependency paths and longest chains"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in dependency analysis accuracy (0.0-1.0)"
    )
    generated_at: datetime = Field(description="Timestamp when this graph was generated")
    validation_status: Optional[str] = Field(
        default="unvalidated",
        description="Manual validation status",
        pattern="^(unvalidated|validated|disputed)$"
    )


# ============================================================================
# Dependency Injection
# ============================================================================


def get_dependency_service():
    """
    Get dependency analysis service instance.
    
    Returns:
        AnalysisOrchestrator: Orchestrator instance providing dependency graph methods
    """
    from omega_analysis.services.orchestration.analysis_orchestrator import get_orchestrator_instance
    return get_orchestrator_instance()


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/projects/{id}/analysis/dependencies",
    response_model=DependencyGraph,
    status_code=status.HTTP_200_OK,
    summary="Get dependency graph",
    description="Retrieve static and runtime dependency analysis results with optional graph type filtering",
    responses={
        200: {"description": "Dependency graph retrieved successfully"},
        404: {"description": "Project not found"},
        501: {"description": "Dependency service not yet implemented"}
    }
)
async def get_dependency_graph(
    id: UUID,
    graph_type: str = Query(
        default="combined",
        pattern="^(static|runtime|combined)$",
        description="Type of dependency graph to retrieve"
    ),
    service=Depends(get_dependency_service)
) -> DependencyGraph:
    """
    Retrieve dependency graph for a project.
    
    Returns static code dependencies, runtime communication patterns, or a combined view.
    Includes coupling metrics, circular dependencies, and critical path analysis.
    
    Args:
        id: UUID of the analysis project
        graph_type: Type of graph to retrieve (static, runtime, or combined)
        service: Injected dependency analysis service
    
    Returns:
        DependencyGraph with nodes, edges, and analysis metrics
    
    Raises:
        HTTPException: 404 if project not found, 501 if service unavailable
    """
    logger.info(f"Retrieving dependency graph for project {id} (type: {graph_type})")
    
    try:
        # Service implementation pending in T040
        graph = await service.get_dependency_graph(id, graph_type)
        logger.info(f"Retrieved dependency graph {graph.id} with {len(graph.nodes)} nodes")
        return graph
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve dependency graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dependency graph: {str(e)}"
        )


@router.get(
    "/dependencies/health",
    status_code=status.HTTP_200_OK,
    summary="Dependency service health check",
    description="Check if dependency analysis service is available and operational"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for dependency analysis service.
    
    Returns:
        Dict with status and message
    """
    logger.debug("Dependency service health check")
    return {
        "status": "pending",
        "message": "Dependency analysis service awaiting implementation in T040"
    }
