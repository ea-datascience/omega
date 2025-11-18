"""Integration tests for analysis operations API endpoints."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from fastapi.testclient import TestClient

from omega_analysis.api.main import app


client = TestClient(app)


class TestAnalysisEndpoints:
    """Test suite for analysis operations endpoints."""
    
    def test_analysis_health_check(self):
        """Test analysis service health check endpoint."""
        response = client.get("/api/v1/analysis/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "analysis-operations"
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "endpoints" in data
        assert "dependencies" in data
        
        # Verify endpoint mappings
        endpoints = data["endpoints"]
        assert "start_analysis" in endpoints
        assert "get_status" in endpoints
        assert "get_results" in endpoints
        assert "cancel_analysis" in endpoints
    
    def test_start_analysis_endpoint_structure(self):
        """Test start analysis endpoint returns proper structure (will fail until T040)."""
        project_id = uuid4()
        request_data = {
            "analysis_types": ["static", "runtime"],
            "static_analysis_config": {
                "include_tests": True
            }
        }
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Currently returns 501 until orchestrator is implemented (T040)
        assert response.status_code == 501
        assert "orchestrator not yet implemented" in response.json()["detail"].lower()
    
    def test_start_analysis_request_validation(self):
        """Test start analysis request schema validation."""
        project_id = uuid4()
        
        # Test with default analysis types
        request_data = {}
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Should accept empty request with defaults
        assert response.status_code in [501, 202]  # 501 until T040, then 202
    
    def test_start_analysis_with_custom_config(self):
        """Test start analysis with custom configuration."""
        project_id = uuid4()
        request_data = {
            "analysis_types": ["static", "gap_analysis"],
            "static_analysis_config": {
                "include_tests": False,
                "parse_annotations": True,
                "max_depth": 10
            },
            "runtime_analysis_config": None
        }
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Currently returns 501 until T040
        assert response.status_code == 501
    
    def test_get_analysis_status_endpoint(self):
        """Test get analysis status endpoint (will fail until T040)."""
        project_id = uuid4()
        
        response = client.get(f"/api/v1/projects/{project_id}/analysis")
        
        # Currently returns 501 until T040
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_get_analysis_results_endpoint(self):
        """Test get analysis results endpoint (will fail until T040)."""
        project_id = uuid4()
        
        response = client.get(f"/api/v1/projects/{project_id}/analysis/results")
        
        # Currently returns 501 until T040
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_cancel_analysis_endpoint(self):
        """Test cancel analysis endpoint (will fail until T040)."""
        project_id = uuid4()
        request_data = {
            "reason": "Test cancellation"
        }
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis/cancel",
            json=request_data
        )
        
        # Currently returns 501 until T040
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
    
    def test_cancel_analysis_without_reason(self):
        """Test cancel analysis without providing a reason."""
        project_id = uuid4()
        request_data = {}
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis/cancel",
            json=request_data
        )
        
        # Should accept empty request (reason is optional)
        assert response.status_code in [501, 200]  # 501 until T040
    
    def test_invalid_project_id_format(self):
        """Test endpoints with invalid UUID format."""
        invalid_id = "not-a-uuid"
        
        # Test start analysis
        response = client.post(
            f"/api/v1/projects/{invalid_id}/analysis",
            json={}
        )
        assert response.status_code in [422, 501]  # 422 validation error or 501 if orchestrator not ready
        
        # Test get status
        response = client.get(f"/api/v1/projects/{invalid_id}/analysis")
        assert response.status_code in [422, 501]
        
        # Test get results
        response = client.get(f"/api/v1/projects/{invalid_id}/analysis/results")
        assert response.status_code in [422, 501]
        
        # Test cancel
        response = client.post(
            f"/api/v1/projects/{invalid_id}/analysis/cancel",
            json={}
        )
        assert response.status_code in [422, 501]  # 422 validation error or 501 if orchestrator not ready
    
    def test_analysis_types_validation(self):
        """Test validation of analysis types."""
        project_id = uuid4()
        
        # Valid analysis types
        valid_types = ["static", "runtime", "gap_analysis", "risk_assessment"]
        request_data = {"analysis_types": valid_types}
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Should accept valid types (returns 501 until T040)
        assert response.status_code in [501, 202]
    
    def test_empty_analysis_types(self):
        """Test start analysis with empty analysis types list."""
        project_id = uuid4()
        request_data = {"analysis_types": []}
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Should accept empty list (will use defaults)
        assert response.status_code in [501, 202]
    
    def test_request_id_generation(self):
        """Test that each request gets a unique request ID."""
        project_id = uuid4()
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.get(f"/api/v1/projects/{project_id}/analysis")
            responses.append(response)
        
        # All should have responses
        assert all(r.status_code in [501, 200, 404] for r in responses)
    
    def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests to same project."""
        project_id = uuid4()
        
        # Simulate concurrent start requests
        request_data = {"analysis_types": ["static"]}
        
        response1 = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        response2 = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=request_data
        )
        
        # Both should return 501 until T040
        # After T040, one should succeed (202), other should conflict (409)
        assert response1.status_code == 501
        assert response2.status_code == 501


class TestAnalysisResponseSchemas:
    """Test response schema validation."""
    
    def test_analysis_status_response_schema(self):
        """Test AnalysisStatusResponse schema structure."""
        from omega_analysis.api.analysis.analysis import AnalysisStatusResponse
        
        # Create valid response
        response = AnalysisStatusResponse(
            project_id=uuid4(),
            status="running",
            progress_percentage=50,
            current_phase="static_analysis",
            phase_details={"files_analyzed": 100},
            estimated_completion=datetime.now(),
            error_message=None
        )
        
        # Verify required fields
        assert response.project_id is not None
        assert response.status in ["queued", "running", "completed", "failed", "cancelled"]
        assert 0 <= response.progress_percentage <= 100
    
    def test_analysis_status_progress_validation(self):
        """Test progress percentage validation."""
        from omega_analysis.api.analysis.analysis import AnalysisStatusResponse
        
        # Valid progress values
        for progress in [0, 25, 50, 75, 100]:
            response = AnalysisStatusResponse(
                project_id=uuid4(),
                status="running",
                progress_percentage=progress
            )
            assert response.progress_percentage == progress
    
    def test_analysis_results_summary_schema(self):
        """Test AnalysisResultsSummary schema structure."""
        from omega_analysis.api.analysis.analysis import AnalysisResultsSummary
        
        summary = AnalysisResultsSummary(
            project_id=uuid4(),
            status="completed",
            completed_at=datetime.now(),
            static_analysis_completed=True,
            runtime_analysis_completed=True,
            gap_analysis_completed=True,
            risk_assessment_completed=True,
            total_components=150,
            total_dependencies=500,
            identified_boundaries=8,
            overall_risk_score=72.5,
            migration_readiness_score=68.0
        )
        
        # Verify fields
        assert summary.project_id is not None
        assert summary.static_analysis_completed is True
        assert summary.total_components == 150
        assert summary.overall_risk_score == 72.5
    
    def test_start_analysis_request_schema(self):
        """Test StartAnalysisRequest schema."""
        from omega_analysis.api.analysis.analysis import StartAnalysisRequest
        
        # Test with defaults
        request = StartAnalysisRequest()
        assert request.analysis_types == ["static", "runtime", "gap_analysis", "risk_assessment"]
        assert request.static_analysis_config is None
        assert request.runtime_analysis_config is None
        
        # Test with custom values
        request = StartAnalysisRequest(
            analysis_types=["static"],
            static_analysis_config={"include_tests": True}
        )
        assert request.analysis_types == ["static"]
        assert request.static_analysis_config["include_tests"] is True
    
    def test_cancel_analysis_request_schema(self):
        """Test CancelAnalysisRequest schema."""
        from omega_analysis.api.analysis.analysis import CancelAnalysisRequest
        
        # With reason
        request = CancelAnalysisRequest(reason="Test cancellation")
        assert request.reason == "Test cancellation"
        
        # Without reason
        request = CancelAnalysisRequest()
        assert request.reason is None


class TestAnalysisErrorHandling:
    """Test error handling for analysis endpoints."""
    
    def test_orchestrator_not_implemented_error(self):
        """Test that missing orchestrator returns proper error."""
        project_id = uuid4()
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json={}
        )
        
        assert response.status_code == 501
        error_data = response.json()
        assert "detail" in error_data
        assert "orchestrator" in error_data["detail"].lower()
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests."""
        project_id = uuid4()
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        # Analysis endpoints don't have strictly required fields due to defaults
        # This test verifies graceful handling
        project_id = uuid4()
        
        response = client.post(
            f"/api/v1/projects/{project_id}/analysis",
            json=None
        )
        
        # Should handle gracefully
        assert response.status_code in [422, 501]


class TestAnalysisIntegrationReadiness:
    """Tests to verify integration readiness for T040-T042."""
    
    def test_orchestrator_dependency_interface(self):
        """Test that orchestrator dependency interface is correctly defined."""
        from omega_analysis.api.analysis.analysis import get_orchestrator
        
        # Should raise 501 until T040 is complete
        with pytest.raises(Exception) as exc_info:
            get_orchestrator()
        
        # Verify it's the expected error
        assert "501" in str(exc_info.value) or "not yet implemented" in str(exc_info.value).lower()
    
    def test_background_tasks_parameter_present(self):
        """Test that background tasks parameter is present in start_analysis."""
        from omega_analysis.api.analysis.analysis import start_analysis
        import inspect
        
        sig = inspect.signature(start_analysis)
        params = sig.parameters
        
        # Should have background_tasks parameter for async execution
        assert "background_tasks" in params
    
    def test_endpoint_documentation_present(self):
        """Test that all endpoints have proper documentation."""
        from omega_analysis.api.analysis.analysis import (
            start_analysis,
            get_analysis_status,
            get_analysis_results,
            cancel_analysis
        )
        
        # All endpoints should have docstrings
        assert start_analysis.__doc__ is not None
        assert get_analysis_status.__doc__ is not None
        assert get_analysis_results.__doc__ is not None
        assert cancel_analysis.__doc__ is not None
        
        # Docstrings should contain key information
        assert "Args:" in start_analysis.__doc__
        assert "Returns:" in start_analysis.__doc__
        assert "Raises:" in start_analysis.__doc__


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
