"""
Integration tests for the Analysis Orchestrator (T040).

Tests the core orchestration service that coordinates analysis workflows.
"""

import pytest
from uuid import UUID, uuid4

from omega_analysis.services.orchestration.analysis_orchestrator import (
    AnalysisOrchestrator,
    get_orchestrator_instance
)


class TestAnalysisOrchestratorBasics:
    """Test basic orchestrator functionality."""
    
    def test_orchestrator_singleton(self):
        """Test orchestrator returns same instance."""
        orch1 = get_orchestrator_instance()
        orch2 = get_orchestrator_instance()
        assert orch1 is orch2
    
    @pytest.mark.asyncio
    async def test_start_analysis(self):
        """Test starting an analysis."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        result = await orch.start_analysis(project_id)
        
        assert result["project_id"] == str(project_id)
        assert result["status"] == "running"
        assert "analysis_id" in result
    
    @pytest.mark.asyncio
    async def test_get_analysis_status(self):
        """Test retrieving analysis status."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        result = await orch.start_analysis(project_id)
        analysis_id = UUID(result["analysis_id"])  # Parse string to UUID
        
        status = await orch.get_analysis_status(analysis_id)
        
        assert status["project_id"] == str(project_id)
        assert status["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_cancel_analysis(self):
        """Test cancelling an analysis."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        result = await orch.start_analysis(project_id)
        analysis_id = UUID(result["analysis_id"])  # Parse string to UUID
        
        cancel_result = await orch.cancel_analysis(analysis_id, "Testing cancellation")
        
        assert cancel_result["status"] == "cancelled"


class TestOrchestratorArchitectureMethods:
    """Test architecture-related orchestrator methods."""
    
    @pytest.mark.asyncio
    async def test_get_system_architecture(self):
        """Test retrieving system architecture."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        arch = await orch.get_system_architecture(project_id)
        
        assert arch.analysis_project_id == project_id
        assert arch.architecture_style is not None
    
    @pytest.mark.asyncio
    async def test_get_service_boundaries(self):
        """Test retrieving service boundaries."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        boundaries = await orch.get_service_boundaries(project_id)
        
        assert isinstance(boundaries, list)
        assert len(boundaries) > 0
        assert all(hasattr(b, 'name') for b in boundaries)
    
    @pytest.mark.asyncio
    async def test_get_component_details(self):
        """Test retrieving component details."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        components = await orch.get_component_details(project_id)
        
        assert isinstance(components, list)
        assert len(components) > 0
        assert all(hasattr(c, 'name') for c in components)


class TestOrchestratorDependencyMethods:
    """Test dependency-related orchestrator methods."""
    
    @pytest.mark.asyncio
    async def test_get_dependency_graph(self):
        """Test retrieving dependency graph."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        graph = await orch.get_dependency_graph(project_id, "combined")
        
        assert graph.analysis_project_id == project_id
        assert graph.graph_type == "combined"
        assert hasattr(graph, 'nodes')
        assert hasattr(graph, 'edges')
    
    @pytest.mark.asyncio
    async def test_get_dependency_graph_types(self):
        """Test different dependency graph types."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        for graph_type in ["static", "runtime", "combined"]:
            graph = await orch.get_dependency_graph(project_id, graph_type)
            assert graph.graph_type == graph_type


class TestOrchestratorPerformanceMethods:
    """Test performance-related orchestrator methods."""
    
    @pytest.mark.asyncio
    async def test_get_performance_baselines(self):
        """Test retrieving performance baselines."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        baselines = await orch.get_performance_baselines(project_id)
        
        assert isinstance(baselines, list)
        assert len(baselines) > 0
        assert all(hasattr(b, 'environment_type') for b in baselines)
    
    @pytest.mark.asyncio
    async def test_get_performance_baselines_filtered(self):
        """Test retrieving filtered performance baselines."""
        orch = get_orchestrator_instance()
        project_id = uuid4()
        
        baselines = await orch.get_performance_baselines(project_id, "production")
        
        assert all(b.environment_type == "production" for b in baselines)
