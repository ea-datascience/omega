"""Architecture retrieval API endpoints for system architecture analysis."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

router = APIRouter(tags=["architecture"])


# Pydantic Schemas

class SystemArchitecture(BaseModel):
    """System architecture analysis results."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "analysis_project_id": "550e8400-e29b-41d4-a716-446655440001",
            "architecture_style": "modular_monolith",
            "domain_model": {
                "bounded_contexts": ["orders", "inventory", "payments"],
                "aggregates": ["Order", "Product", "Payment"]
            },
            "c4_model": {
                "context": "Enterprise E-Commerce System",
                "containers": ["Web App", "API", "Database"],
                "components": ["OrderService", "ProductCatalog"]
            },
            "technology_stack": {
                "frameworks": ["Spring Boot 3.2", "Spring Data JPA"],
                "databases": ["PostgreSQL 15"],
                "libraries": ["Hibernate", "Jackson"]
            },
            "documentation_coverage": 0.65,
            "test_coverage": 0.78,
            "discovered_at": "2024-11-18T10:00:00Z"
        }
    })
    
    id: UUID
    analysis_project_id: UUID
    architecture_style: str = Field(
        description="Architecture style: layered, modular_monolith, microservices, hybrid, unknown"
    )
    domain_model: Dict[str, Any] = Field(
        default_factory=dict,
        description="Discovered bounded contexts and aggregates"
    )
    c4_model: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context, Container, Component, Code diagrams"
    )
    technology_stack: Dict[str, Any] = Field(
        default_factory=dict,
        description="Frameworks, libraries, dependencies"
    )
    architectural_patterns: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Design patterns and anti-patterns"
    )
    quality_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Code quality and technical debt scores"
    )
    documentation_coverage: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Documentation coverage ratio"
    )
    test_coverage: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Test coverage ratio"
    )
    generated_diagrams: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PlantUML and Mermaid diagram definitions"
    )
    discovered_at: datetime
    tool_versions: Optional[Dict[str, str]] = Field(
        default=None,
        description="Analysis tool versions used"
    )


class ServiceBoundary(BaseModel):
    """Identified service boundary for microservices decomposition."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "order-management",
            "description": "Order processing and fulfillment",
            "components": ["OrderService", "OrderRepository", "OrderController"],
            "dependencies": ["inventory-service", "payment-service"],
            "data_ownership": ["orders", "order_items"],
            "api_contracts": ["/api/orders", "/api/orders/{id}"],
            "cohesion_score": 0.85,
            "coupling_score": 0.25
        }
    })
    
    id: UUID
    name: str
    description: Optional[str] = None
    components: List[str] = Field(
        default_factory=list,
        description="Classes/modules within this boundary"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="External service dependencies"
    )
    data_ownership: List[str] = Field(
        default_factory=list,
        description="Database tables/schemas owned"
    )
    api_contracts: List[str] = Field(
        default_factory=list,
        description="Exposed API endpoints"
    )
    cohesion_score: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Internal cohesion strength"
    )
    coupling_score: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="External coupling strength"
    )
    business_capability: Optional[str] = Field(
        default=None,
        description="Business capability alignment"
    )
    team_alignment: Optional[str] = Field(
        default=None,
        description="Recommended team ownership"
    )


class ComponentDetail(BaseModel):
    """Detailed component information from C4 model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "OrderService",
            "type": "service",
            "package": "com.example.orders",
            "responsibilities": ["Create orders", "Process payments"],
            "dependencies": ["OrderRepository", "PaymentGateway"],
            "lines_of_code": 1250,
            "complexity_score": 45.2
        }
    })
    
    id: UUID
    name: str
    type: str = Field(
        description="Component type: service, repository, controller, etc."
    )
    package: Optional[str] = None
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Component dependencies"
    )
    lines_of_code: Optional[int] = None
    complexity_score: Optional[float] = None
    test_coverage: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0
    )
    documentation_status: Optional[str] = Field(
        default=None,
        description="Documentation quality: none, minimal, adequate, comprehensive"
    )


# Dependency: Get architecture service (implemented via orchestrator)
def get_architecture_service():
    """Get architecture analysis service dependency.
    
    Returns:
        AnalysisOrchestrator: Orchestrator instance providing architecture methods
    """
    from omega_analysis.services.orchestration.analysis_orchestrator import get_orchestrator_instance
    return get_orchestrator_instance()


# API Endpoints

@router.get(
    "/projects/{project_id}/analysis/architecture",
    response_model=SystemArchitecture,
    summary="Get system architecture",
    description="Retrieve discovered system architecture and C4 diagrams"
)
async def get_system_architecture(
    project_id: UUID,
    service = Depends(get_architecture_service)
) -> SystemArchitecture:
    """Get complete system architecture for a project.
    
    Args:
        project_id: Analysis project UUID
        service: Architecture analysis service (injected)
        
    Returns:
        SystemArchitecture with complete analysis results
        
    Raises:
        HTTPException: 404 if project not found
        HTTPException: 501 if service not implemented
    """
    logger.info(f"Retrieving architecture for project {project_id}")
    
    try:
        architecture = await service.get_system_architecture(project_id)
        return architecture
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving architecture for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve architecture: {str(e)}"
        )


@router.get(
    "/projects/{project_id}/analysis/architecture/boundaries",
    response_model=List[ServiceBoundary],
    summary="Get service boundaries",
    description="Retrieve identified service boundaries for microservices decomposition"
)
async def get_service_boundaries(
    project_id: UUID,
    service = Depends(get_architecture_service)
) -> List[ServiceBoundary]:
    """Get identified service boundaries for microservices migration.
    
    Args:
        project_id: Analysis project UUID
        service: Architecture analysis service (injected)
        
    Returns:
        List of ServiceBoundary recommendations
        
    Raises:
        HTTPException: 404 if project not found
        HTTPException: 501 if service not implemented
    """
    logger.info(f"Retrieving service boundaries for project {project_id}")
    
    try:
        boundaries = await service.get_service_boundaries(project_id)
        return boundaries
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving service boundaries for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service boundaries: {str(e)}"
        )


@router.get(
    "/projects/{project_id}/analysis/architecture/components",
    response_model=List[ComponentDetail],
    summary="Get component details",
    description="Retrieve detailed component information from C4 model analysis"
)
async def get_component_details(
    project_id: UUID,
    boundary_id: Optional[UUID] = None,
    service = Depends(get_architecture_service)
) -> List[ComponentDetail]:
    """Get detailed component information, optionally filtered by service boundary.
    
    Args:
        project_id: Analysis project UUID
        boundary_id: Optional service boundary UUID to filter components
        service: Architecture analysis service (injected)
        
    Returns:
        List of ComponentDetail from C4 analysis
        
    Raises:
        HTTPException: 404 if project not found
        HTTPException: 501 if service not implemented
    """
    logger.info(
        f"Retrieving components for project {project_id}" +
        (f" in boundary {boundary_id}" if boundary_id else "")
    )
    
    try:
        components = await service.get_component_details(project_id, boundary_id)
        return components
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving components for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve components: {str(e)}"
        )


# Health check for architecture service
@router.get(
    "/architecture/health",
    summary="Architecture service health check",
    description="Check health of architecture analysis service"
)
async def architecture_health_check() -> Dict[str, Any]:
    """Health check for architecture service.
    
    Returns:
        Health status information
    """
    return {
        "service": "architecture-analysis",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "get_architecture": "GET /projects/{id}/analysis/architecture",
            "get_boundaries": "GET /projects/{id}/analysis/architecture/boundaries",
            "get_components": "GET /projects/{id}/analysis/architecture/components"
        },
        "dependencies": {
            "architecture_service": "not_implemented",  # Will be updated when T040 is complete
            "database": "not_checked",
            "cache": "not_checked"
        }
    }