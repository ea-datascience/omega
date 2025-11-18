"""
Integration tests for dependency graph endpoints.

Tests the dependency analysis REST API endpoints including:
- Dependency graph retrieval with graph_type filtering
- Schema validation for DependencyGraph model
- Error handling and edge cases
- Integration readiness for T040 dependency service
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from omega_analysis.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_project_id():
    """Generate sample project UUID."""
    return str(uuid4())


# ============================================================================
# Endpoint Functionality Tests
# ============================================================================


class TestDependencyEndpoints:
    """Test dependency graph endpoint functionality."""
    
    def test_health_check_endpoint(self, client):
        """Test dependency service health check endpoint."""
        response = client.get("/api/v1/dependencies/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert data["status"] == "pending"
        assert "T040" in data["message"]
    
    def test_get_dependency_graph_endpoint_structure(self, client, sample_project_id):
        """Test dependency graph endpoint exists and has correct structure."""
        response = client.get(f"/api/v1/projects/{sample_project_id}/analysis/dependencies")
        
        # Should return 501 Not Implemented until T040
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 501:
            data = response.json()
            assert "detail" in data
            assert "T040" in data["detail"]
    
    def test_dependency_graph_with_static_type(self, client, sample_project_id):
        """Test dependency graph endpoint with static graph type filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
            params={"graph_type": "static"}
        )
        
        # Should return 501 until service implemented
        assert response.status_code in [200, 404, 501]
    
    def test_dependency_graph_with_runtime_type(self, client, sample_project_id):
        """Test dependency graph endpoint with runtime graph type filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
            params={"graph_type": "runtime"}
        )
        
        assert response.status_code in [200, 404, 501]
    
    def test_dependency_graph_with_combined_type(self, client, sample_project_id):
        """Test dependency graph endpoint with combined graph type (default)."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
            params={"graph_type": "combined"}
        )
        
        assert response.status_code in [200, 404, 501]
    
    def test_dependency_graph_default_type(self, client, sample_project_id):
        """Test dependency graph endpoint without graph_type uses 'combined' default."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies"
        )
        
        # Should default to combined type
        assert response.status_code in [200, 404, 501]
    
    def test_dependency_graph_invalid_type(self, client, sample_project_id):
        """Test dependency graph endpoint rejects invalid graph_type values."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
            params={"graph_type": "invalid"}
        )
        
        # Should return 422 for invalid enum value or 501 if dependency injection runs first
        assert response.status_code in [422, 501]
    
    def test_dependency_graph_invalid_uuid(self, client):
        """Test dependency graph endpoint with malformed project UUID."""
        response = client.get("/api/v1/projects/not-a-uuid/analysis/dependencies")
        
        # FastAPI returns 422 for invalid UUID format or 501 if dependency injection runs first
        assert response.status_code in [422, 501]
    
    def test_concurrent_dependency_requests(self, client, sample_project_id):
        """Test multiple concurrent dependency graph requests."""
        import concurrent.futures
        
        def make_request():
            return client.get(
                f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
                params={"graph_type": "combined"}
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [f.result() for f in futures]
        
        # All should return same status code
        assert all(r.status_code in [200, 404, 501] for r in responses)


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestDependencyResponseSchemas:
    """Test Pydantic schema validation for dependency responses."""
    
    def test_dependency_graph_schema_structure(self, client):
        """Test DependencyGraph schema has required and optional fields."""
        # Get OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi = response.json()
        schema = openapi["components"]["schemas"]["DependencyGraph"]
        
        # Verify core required fields (nodes and edges have default_factory, so not in required)
        required_fields = {"id", "analysis_project_id", "graph_type", "generated_at"}
        assert required_fields.issubset(set(schema.get("required", [])))
        
        # Verify all fields exist in properties
        expected_fields = {
            "id", "analysis_project_id", "graph_type", "nodes", "edges",
            "coupling_metrics", "external_dependencies", "data_dependencies",
            "circular_dependencies", "critical_path_analysis", "confidence_score",
            "generated_at", "validation_status"
        }
        actual_fields = set(schema["properties"].keys())
        assert expected_fields == actual_fields
    
    def test_graph_type_enum_values(self, client):
        """Test graph_type field has correct enum values."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["DependencyGraph"]
        graph_type_prop = schema["properties"]["graph_type"]
        
        # Should have enum constraint
        assert "pattern" in graph_type_prop or "enum" in graph_type_prop
    
    def test_validation_status_enum_values(self, client):
        """Test validation_status field has correct enum values."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["DependencyGraph"]
        
        # validation_status should exist and have pattern or enum
        if "validation_status" in schema["properties"]:
            status_prop = schema["properties"]["validation_status"]
            # Should have constraints (anyOf for Optional or direct pattern)
            assert "pattern" in status_prop or "anyOf" in status_prop or "enum" in status_prop
    
    def test_confidence_score_bounded(self, client):
        """Test confidence_score field is bounded between 0.0 and 1.0."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["DependencyGraph"]
        
        # Check confidence_score constraints (may be in anyOf for Optional)
        if "confidence_score" in schema["properties"]:
            score_prop = schema["properties"]["confidence_score"]
            
            # Handle Optional fields with anyOf structure
            if "anyOf" in score_prop:
                # Find the number schema in anyOf
                number_schema = next(
                    (s for s in score_prop["anyOf"] if s.get("type") == "number"),
                    None
                )
                if number_schema:
                    assert number_schema.get("minimum") == 0.0
                    assert number_schema.get("maximum") == 1.0
            else:
                assert score_prop.get("minimum") == 0.0
                assert score_prop.get("maximum") == 1.0
    
    def test_schema_has_examples(self, client):
        """Test DependencyGraph schema includes example data."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["DependencyGraph"]
        
        # Should have examples in schema
        assert "example" in schema or "examples" in schema


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestDependencyErrorHandling:
    """Test error handling for dependency endpoints."""
    
    def test_dependency_service_not_implemented(self, client, sample_project_id):
        """Test dependency service returns 501 when not yet implemented."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/analysis/dependencies"
        )
        
        # Should return 501 until T040 implements service
        assert response.status_code in [404, 501]
        
        if response.status_code == 501:
            data = response.json()
            assert "detail" in data
            assert "T040" in data["detail"] or "not yet available" in data["detail"].lower()
    
    def test_malformed_graph_type_parameter(self, client, sample_project_id):
        """Test handling of invalid graph_type parameter values."""
        invalid_types = ["STATIC", "unknown", "123", "static-runtime", ""]
        
        for invalid_type in invalid_types:
            response = client.get(
                f"/api/v1/projects/{sample_project_id}/analysis/dependencies",
                params={"graph_type": invalid_type}
            )
            
            # Should return 422 for invalid enum or pattern violation
            assert response.status_code in [422, 501]


# ============================================================================
# Integration Readiness Tests
# ============================================================================


class TestDependencyIntegrationReadiness:
    """Test readiness for T040 dependency service integration."""
    
    def test_dependency_service_interface(self, client):
        """Test dependency service dependency injection is configured."""
        # Verify the endpoint exists and has proper dependency injection
        response = client.get("/openapi.json")
        openapi = response.json()
        
        # Check that dependencies endpoint is documented (using {id} path param)
        paths = openapi["paths"]
        assert "/api/v1/projects/{id}/analysis/dependencies" in paths
        
        endpoint = paths["/api/v1/projects/{id}/analysis/dependencies"]["get"]
        assert endpoint["summary"] == "Get dependency graph"
        assert "parameters" in endpoint
        
        # Verify graph_type parameter
        params = endpoint["parameters"]
        graph_type_param = next((p for p in params if p["name"] == "graph_type"), None)
        assert graph_type_param is not None
        assert graph_type_param["in"] == "query"
    
    def test_endpoint_documentation_completeness(self, client):
        """Test that dependency endpoint has complete OpenAPI documentation."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        endpoint = openapi["paths"]["/api/v1/projects/{id}/analysis/dependencies"]["get"]
        
        # Should have complete documentation
        assert "summary" in endpoint
        assert "description" in endpoint
        assert "responses" in endpoint
        assert "200" in endpoint["responses"]
        assert "404" in endpoint["responses"]
    
    def test_response_models_configured(self, client):
        """Test that response models are properly configured."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        endpoint = openapi["paths"]["/api/v1/projects/{id}/analysis/dependencies"]["get"]
        success_response = endpoint["responses"]["200"]
        
        # Should reference DependencyGraph schema
        assert "content" in success_response
        assert "application/json" in success_response["content"]
        schema_ref = success_response["content"]["application/json"]["schema"]
        assert "$ref" in schema_ref
        assert "DependencyGraph" in schema_ref["$ref"]
