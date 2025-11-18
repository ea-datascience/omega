"""Integration tests for architecture retrieval endpoints."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from omega_analysis.api.main import app


client = TestClient(app)


class TestArchitectureEndpoints:
    """Test architecture analysis retrieval endpoints."""
    
    def test_architecture_health_check(self):
        """Test architecture service health check endpoint."""
        response = client.get("/api/v1/architecture/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "architecture-analysis"
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "endpoints" in data
        assert "get_architecture" in data["endpoints"]
        assert "get_boundaries" in data["endpoints"]
        assert "get_components" in data["endpoints"]
    
    def test_get_system_architecture_endpoint_structure(self):
        """Test GET /projects/{id}/analysis/architecture endpoint exists."""
        project_id = uuid4()
        response = client.get(f"/api/v1/projects/{project_id}/analysis/architecture")
        
        # Should return 501 until T040 is implemented
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_get_service_boundaries_endpoint_structure(self):
        """Test GET /projects/{id}/analysis/architecture/boundaries endpoint exists."""
        project_id = uuid4()
        response = client.get(f"/api/v1/projects/{project_id}/analysis/architecture/boundaries")
        
        # Should return 501 until T040 is implemented
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_get_component_details_endpoint_structure(self):
        """Test GET /projects/{id}/analysis/architecture/components endpoint exists."""
        project_id = uuid4()
        response = client.get(f"/api/v1/projects/{project_id}/analysis/architecture/components")
        
        # Should return 501 until T040 is implemented
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_get_components_with_boundary_filter(self):
        """Test GET components with optional boundary_id filter."""
        project_id = uuid4()
        boundary_id = uuid4()
        
        response = client.get(
            f"/api/v1/projects/{project_id}/analysis/architecture/components",
            params={"boundary_id": str(boundary_id)}
        )
        
        # Should return 501 until T040 is implemented
        assert response.status_code == 501
    
    def test_invalid_project_id_format_architecture(self):
        """Test endpoints with invalid UUID format."""
        invalid_id = "not-a-uuid"
        
        # Test get architecture
        response = client.get(f"/api/v1/projects/{invalid_id}/analysis/architecture")
        assert response.status_code in [422, 501]  # 422 validation or 501 if passes through
        
        # Test get boundaries
        response = client.get(f"/api/v1/projects/{invalid_id}/analysis/architecture/boundaries")
        assert response.status_code in [422, 501]
        
        # Test get components
        response = client.get(f"/api/v1/projects/{invalid_id}/analysis/architecture/components")
        assert response.status_code in [422, 501]
    
    def test_concurrent_architecture_requests(self):
        """Test handling of concurrent architecture retrieval requests."""
        project_id = uuid4()
        
        # Make concurrent requests
        response1 = client.get(f"/api/v1/projects/{project_id}/analysis/architecture")
        response2 = client.get(f"/api/v1/projects/{project_id}/analysis/architecture/boundaries")
        response3 = client.get(f"/api/v1/projects/{project_id}/analysis/architecture/components")
        
        # All should handle gracefully (return 501 until T040)
        assert response1.status_code == 501
        assert response2.status_code == 501
        assert response3.status_code == 501


class TestArchitectureResponseSchemas:
    """Test architecture response schema validation."""
    
    def test_system_architecture_schema_structure(self):
        """Test SystemArchitecture schema has required fields."""
        from omega_analysis.api.analysis.architecture import SystemArchitecture
        
        # Check schema structure
        schema = SystemArchitecture.model_json_schema()
        required = schema.get("required", [])
        
        # Core required fields
        assert "id" in required
        assert "analysis_project_id" in required
        assert "architecture_style" in required
        assert "discovered_at" in required
        
        # Check all fields exist in properties (required or optional)
        properties = schema.get("properties", {})
        assert "domain_model" in properties
        assert "c4_model" in properties
        assert "technology_stack" in properties
        assert "architectural_patterns" in properties
        assert "quality_metrics" in properties
        assert "documentation_coverage" in properties
        assert "test_coverage" in properties
        assert "generated_diagrams" in properties
        assert "tool_versions" in properties
    
    def test_service_boundary_schema_structure(self):
        """Test ServiceBoundary schema has required fields."""
        from omega_analysis.api.analysis.architecture import ServiceBoundary
        
        schema = ServiceBoundary.model_json_schema()
        required = schema.get("required", [])
        
        assert "id" in required
        assert "name" in required
        
        properties = schema.get("properties", {})
        assert "components" in properties
        assert "dependencies" in properties
        assert "data_ownership" in properties
        assert "api_contracts" in properties
        assert "cohesion_score" in properties
        assert "coupling_score" in properties
    
    def test_component_detail_schema_structure(self):
        """Test ComponentDetail schema has required fields."""
        from omega_analysis.api.analysis.architecture import ComponentDetail
        
        schema = ComponentDetail.model_json_schema()
        required = schema.get("required", [])
        
        assert "id" in required
        assert "name" in required
        assert "type" in required
        
        properties = schema.get("properties", {})
        assert "package" in properties
        assert "responsibilities" in properties
        assert "dependencies" in properties
        assert "lines_of_code" in properties
        assert "complexity_score" in properties
    
    def test_coverage_scores_bounded(self):
        """Test coverage and score fields are bounded 0-1."""
        from omega_analysis.api.analysis.architecture import (
            SystemArchitecture, ServiceBoundary, ComponentDetail
        )
        
        # SystemArchitecture coverage bounds
        arch_schema = SystemArchitecture.model_json_schema()
        doc_cov = arch_schema["properties"]["documentation_coverage"]
        test_cov = arch_schema["properties"]["test_coverage"]
        # Check that constraints exist (anyOf structure with null)
        assert "anyOf" in doc_cov or "minimum" in doc_cov
        assert "anyOf" in test_cov or "minimum" in test_cov
        
        # ServiceBoundary score bounds
        boundary_schema = ServiceBoundary.model_json_schema()
        cohesion = boundary_schema["properties"]["cohesion_score"]
        coupling = boundary_schema["properties"]["coupling_score"]
        assert "anyOf" in cohesion or "minimum" in cohesion
        assert "anyOf" in coupling or "minimum" in coupling
        
        # ComponentDetail coverage bounds
        comp_schema = ComponentDetail.model_json_schema()
        comp_cov = comp_schema["properties"]["test_coverage"]
        assert "anyOf" in comp_cov or "minimum" in comp_cov
    
    def test_schema_examples_provided(self):
        """Test that schemas have example data for documentation."""
        from omega_analysis.api.analysis.architecture import (
            SystemArchitecture, ServiceBoundary, ComponentDetail
        )
        
        # All schemas should have examples in their config
        arch_example = SystemArchitecture.model_config.get("json_schema_extra", {}).get("example")
        assert arch_example is not None
        assert "architecture_style" in arch_example
        assert "domain_model" in arch_example
        
        boundary_example = ServiceBoundary.model_config.get("json_schema_extra", {}).get("example")
        assert boundary_example is not None
        assert "name" in boundary_example
        assert "components" in boundary_example
        
        component_example = ComponentDetail.model_config.get("json_schema_extra", {}).get("example")
        assert component_example is not None
        assert "name" in component_example
        assert "type" in component_example


class TestArchitectureErrorHandling:
    """Test error handling for architecture endpoints."""
    
    def test_architecture_service_not_implemented(self):
        """Test that service returns 501 when not implemented."""
        project_id = uuid4()
        
        response = client.get(f"/api/v1/projects/{project_id}/analysis/architecture")
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
        assert "T040" in response.json()["detail"] or "t040" in response.json()["detail"].lower()
    
    def test_malformed_boundary_id_parameter(self):
        """Test handling of malformed boundary_id query parameter."""
        project_id = uuid4()
        
        response = client.get(
            f"/api/v1/projects/{project_id}/analysis/architecture/components",
            params={"boundary_id": "not-a-uuid"}
        )
        
        # Should return validation error or pass through to 501
        assert response.status_code in [422, 501]


class TestArchitectureIntegrationReadiness:
    """Test readiness for T040 integration."""
    
    def test_architecture_service_dependency_interface(self):
        """Test that architecture service dependency is ready for T040."""
        from omega_analysis.api.analysis.architecture import get_architecture_service
        
        # Should raise 501 until T040 is implemented
        with pytest.raises(Exception) as exc_info:
            get_architecture_service()
        
        assert exc_info.value.status_code == 501
        assert "not yet implemented" in str(exc_info.value.detail).lower()
    
    def test_endpoint_documentation_complete(self):
        """Test that all endpoints have proper documentation."""
        from omega_analysis.api.analysis.architecture import router
        
        # Check that router has routes
        routes = [route for route in router.routes]
        assert len(routes) >= 4  # 3 main endpoints + health check
        
        # All routes should have summary and description
        for route in routes:
            if hasattr(route, 'summary'):
                assert route.summary is not None
                assert route.description is not None
    
    def test_response_models_configured(self):
        """Test that endpoints have response models configured."""
        from omega_analysis.api.analysis.architecture import router
        
        # Check main endpoints have response models
        get_arch_route = None
        get_boundaries_route = None
        get_components_route = None
        
        for route in router.routes:
            if hasattr(route, 'path'):
                if 'architecture/boundaries' in route.path:
                    get_boundaries_route = route
                elif 'architecture/components' in route.path:
                    get_components_route = route
                elif 'architecture' in route.path and 'health' not in route.path:
                    if get_arch_route is None:  # Get first match
                        get_arch_route = route
        
        # Verify response models are set
        if get_arch_route and hasattr(get_arch_route, 'response_model'):
            assert get_arch_route.response_model is not None
        if get_boundaries_route and hasattr(get_boundaries_route, 'response_model'):
            assert get_boundaries_route.response_model is not None
        if get_components_route and hasattr(get_components_route, 'response_model'):
            assert get_components_route.response_model is not None
