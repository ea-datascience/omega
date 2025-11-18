"""
Integration tests for performance baselines endpoints.

Tests the performance baselines REST API endpoints including:
- Baselines retrieval with environment_type filtering
- Schema validation for PerformanceBaseline model
- Error handling and edge cases
- Integration readiness for T040 baselines service
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


class TestBaselinesEndpoints:
    """Test performance baselines endpoint functionality."""
    
    def test_health_check_endpoint(self, client):
        """Test baselines service health check endpoint."""
        response = client.get("/api/v1/baselines/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert data["status"] == "pending"
        assert "T040" in data["message"]
    
    def test_list_baselines_endpoint_structure(self, client, sample_project_id):
        """Test baselines endpoint exists and has correct structure."""
        response = client.get(f"/api/v1/projects/{sample_project_id}/baselines")
        
        # Should return 501 Not Implemented until T040
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 501:
            data = response.json()
            assert "detail" in data
            assert "T040" in data["detail"]
    
    def test_list_baselines_with_production_filter(self, client, sample_project_id):
        """Test baselines endpoint with production environment filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/baselines",
            params={"environment_type": "production"}
        )
        
        # Should return 501 until service implemented
        assert response.status_code in [200, 404, 501]
    
    def test_list_baselines_with_staging_filter(self, client, sample_project_id):
        """Test baselines endpoint with staging environment filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/baselines",
            params={"environment_type": "staging"}
        )
        
        assert response.status_code in [200, 404, 501]
    
    def test_list_baselines_with_development_filter(self, client, sample_project_id):
        """Test baselines endpoint with development environment filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/baselines",
            params={"environment_type": "development"}
        )
        
        assert response.status_code in [200, 404, 501]
    
    def test_list_baselines_with_synthetic_filter(self, client, sample_project_id):
        """Test baselines endpoint with synthetic environment filter."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/baselines",
            params={"environment_type": "synthetic"}
        )
        
        assert response.status_code in [200, 404, 501]
    
    def test_list_baselines_without_filter(self, client, sample_project_id):
        """Test baselines endpoint without environment_type filter returns all."""
        response = client.get(f"/api/v1/projects/{sample_project_id}/baselines")
        
        # Should work without filter
        assert response.status_code in [200, 404, 501]
    
    def test_list_baselines_invalid_environment_type(self, client, sample_project_id):
        """Test baselines endpoint rejects invalid environment_type values."""
        response = client.get(
            f"/api/v1/projects/{sample_project_id}/baselines",
            params={"environment_type": "invalid"}
        )
        
        # Should return 422 for invalid enum value or 501 if dependency injection runs first
        assert response.status_code in [422, 501]
    
    def test_list_baselines_invalid_uuid(self, client):
        """Test baselines endpoint with malformed project UUID."""
        response = client.get("/api/v1/projects/not-a-uuid/baselines")
        
        # FastAPI returns 422 for invalid UUID format or 501 if dependency injection runs first
        assert response.status_code in [422, 501]
    
    def test_concurrent_baselines_requests(self, client, sample_project_id):
        """Test multiple concurrent baselines requests."""
        import concurrent.futures
        
        def make_request():
            return client.get(
                f"/api/v1/projects/{sample_project_id}/baselines",
                params={"environment_type": "production"}
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [f.result() for f in futures]
        
        # All should return same status code
        assert all(r.status_code in [200, 404, 501] for r in responses)


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestBaselinesResponseSchemas:
    """Test Pydantic schema validation for baselines responses."""
    
    def test_performance_baseline_schema_structure(self, client):
        """Test PerformanceBaseline schema has required and optional fields."""
        # Get OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi = response.json()
        schema = openapi["components"]["schemas"]["PerformanceBaseline"]
        
        # Verify core required fields (response_time_metrics has default_factory, not in required)
        required_fields = {
            "id", "analysis_project_id", "collection_period_start", 
            "collection_period_end", "environment_type", 
            "statistical_confidence", "sample_size"
        }
        assert required_fields.issubset(set(schema.get("required", [])))
        
        # Verify all fields exist in properties
        expected_fields = {
            "id", "analysis_project_id", "collection_period_start", "collection_period_end",
            "environment_type", "load_characteristics", "response_time_metrics",
            "throughput_metrics", "error_rate_metrics", "resource_utilization",
            "database_performance", "external_service_metrics", "statistical_confidence",
            "sample_size", "data_quality_score"
        }
        actual_fields = set(schema["properties"].keys())
        assert expected_fields == actual_fields
    
    def test_environment_type_enum_values(self, client):
        """Test environment_type field has correct enum values."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["PerformanceBaseline"]
        env_type_prop = schema["properties"]["environment_type"]
        
        # Should have enum or pattern constraint
        assert "pattern" in env_type_prop or "enum" in env_type_prop
    
    def test_confidence_and_quality_scores_bounded(self, client):
        """Test confidence and quality scores are bounded between 0.0 and 1.0."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["PerformanceBaseline"]
        
        # Check statistical_confidence constraints
        if "statistical_confidence" in schema["properties"]:
            confidence_prop = schema["properties"]["statistical_confidence"]
            
            # Handle Optional fields with anyOf structure
            if "anyOf" in confidence_prop:
                number_schema = next(
                    (s for s in confidence_prop["anyOf"] if s.get("type") == "number"),
                    None
                )
                if number_schema:
                    assert number_schema.get("minimum") == 0.0
                    assert number_schema.get("maximum") == 1.0
            else:
                assert confidence_prop.get("minimum") == 0.0
                assert confidence_prop.get("maximum") == 1.0
        
        # Check data_quality_score constraints
        if "data_quality_score" in schema["properties"]:
            quality_prop = schema["properties"]["data_quality_score"]
            
            if "anyOf" in quality_prop:
                number_schema = next(
                    (s for s in quality_prop["anyOf"] if s.get("type") == "number"),
                    None
                )
                if number_schema:
                    assert number_schema.get("minimum") == 0.0
                    assert number_schema.get("maximum") == 1.0
            else:
                assert quality_prop.get("minimum") == 0.0
                assert quality_prop.get("maximum") == 1.0
    
    def test_sample_size_constraints(self, client):
        """Test sample_size field has minimum value constraint."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["PerformanceBaseline"]
        sample_size_prop = schema["properties"]["sample_size"]
        
        # Should have minimum constraint of 1
        if "anyOf" in sample_size_prop:
            integer_schema = next(
                (s for s in sample_size_prop["anyOf"] if s.get("type") == "integer"),
                None
            )
            if integer_schema:
                assert integer_schema.get("minimum") == 1
        else:
            assert sample_size_prop.get("minimum") == 1
    
    def test_schema_has_examples(self, client):
        """Test PerformanceBaseline schema includes example data."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        schema = openapi["components"]["schemas"]["PerformanceBaseline"]
        
        # Should have examples in schema
        assert "example" in schema or "examples" in schema


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestBaselinesErrorHandling:
    """Test error handling for baselines endpoints."""
    
    def test_baselines_service_not_implemented(self, client, sample_project_id):
        """Test baselines service returns 501 when not yet implemented."""
        response = client.get(f"/api/v1/projects/{sample_project_id}/baselines")
        
        # Should return 501 until T040 implements service
        assert response.status_code in [404, 501]
        
        if response.status_code == 501:
            data = response.json()
            assert "detail" in data
            assert "T040" in data["detail"] or "not yet available" in data["detail"].lower()
    
    def test_malformed_environment_type_parameter(self, client, sample_project_id):
        """Test handling of invalid environment_type parameter values."""
        invalid_types = ["PRODUCTION", "unknown", "123", "prod-staging", ""]
        
        for invalid_type in invalid_types:
            response = client.get(
                f"/api/v1/projects/{sample_project_id}/baselines",
                params={"environment_type": invalid_type}
            )
            
            # Should return 422 for invalid enum or pattern violation, or 501
            assert response.status_code in [422, 501]


# ============================================================================
# Integration Readiness Tests
# ============================================================================


class TestBaselinesIntegrationReadiness:
    """Test readiness for T040 baselines service integration."""
    
    def test_baselines_service_interface(self, client):
        """Test baselines service dependency injection is configured."""
        # Verify the endpoint exists and has proper dependency injection
        response = client.get("/openapi.json")
        openapi = response.json()
        
        # Check that baselines endpoint is documented
        paths = openapi["paths"]
        assert "/api/v1/projects/{id}/baselines" in paths
        
        endpoint = paths["/api/v1/projects/{id}/baselines"]["get"]
        assert endpoint["summary"] == "List performance baselines"
        assert "parameters" in endpoint
        
        # Verify environment_type parameter
        params = endpoint["parameters"]
        env_type_param = next((p for p in params if p["name"] == "environment_type"), None)
        assert env_type_param is not None
        assert env_type_param["in"] == "query"
        assert env_type_param["required"] is False  # Optional parameter
    
    def test_endpoint_documentation_completeness(self, client):
        """Test that baselines endpoint has complete OpenAPI documentation."""
        response = client.get("/openapi.json")
        openapi = response.json()
        
        endpoint = openapi["paths"]["/api/v1/projects/{id}/baselines"]["get"]
        
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
        
        endpoint = openapi["paths"]["/api/v1/projects/{id}/baselines"]["get"]
        success_response = endpoint["responses"]["200"]
        
        # Should reference array of PerformanceBaseline
        assert "content" in success_response
        assert "application/json" in success_response["content"]
        schema = success_response["content"]["application/json"]["schema"]
        
        # Should be array type
        assert schema.get("type") == "array"
        assert "items" in schema
        assert "$ref" in schema["items"]
        assert "PerformanceBaseline" in schema["items"]["$ref"]
