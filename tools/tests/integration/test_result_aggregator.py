"""
Integration tests for Result Aggregator.

Tests result aggregation from multiple analysis phases including merging strategies,
validation, and integration with the analysis orchestrator.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from omega_analysis.services.orchestration.result_aggregator import (
    ResultAggregator,
    AggregationStrategy,
    AnalysisResultType
)


class TestResultAggregatorBasics:
    """Test basic result aggregator initialization and state."""
    
    def test_initialization(self):
        """Test aggregator initializes with correct state."""
        analysis_id = uuid4()
        project_id = uuid4()
        
        aggregator = ResultAggregator(analysis_id, project_id)
        
        assert aggregator.analysis_id == analysis_id
        assert aggregator.project_id == project_id
        assert aggregator.created_at is not None
        assert len(aggregator.results) == len(AnalysisResultType)
        assert all(isinstance(results, list) for results in aggregator.results.values())
    
    def test_initial_results_empty(self):
        """Test that all result types start empty."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        for result_type in AnalysisResultType:
            assert len(aggregator.results[result_type]) == 0
    
    def test_initial_validation_state(self):
        """Test initial validation state."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        assert len(aggregator.validation_errors) == 0
        assert len(aggregator.validation_warnings) == 0


class TestAddingResults:
    """Test adding various types of results."""
    
    def test_add_static_analysis_result(self):
        """Test adding static analysis result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "classes": ["OrderService", "PaymentService"],
            "methods": 150,
            "complexity": 45.2
        }
        
        aggregator.add_static_analysis_result(result_data, "javaparser")
        
        results = aggregator.results[AnalysisResultType.STATIC_ANALYSIS]
        assert len(results) == 1
        assert results[0]["data"] == result_data
        assert results[0]["source"] == "static:javaparser"
        assert "timestamp" in results[0]
    
    def test_add_runtime_analysis_result(self):
        """Test adding runtime analysis result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "endpoints": ["/api/orders", "/api/payments"],
            "avg_response_time": 45.3,
            "error_rate": 0.002
        }
        
        aggregator.add_runtime_analysis_result(result_data, "signoz")
        
        results = aggregator.results[AnalysisResultType.RUNTIME_ANALYSIS]
        assert len(results) == 1
        assert results[0]["data"] == result_data
        assert results[0]["source"] == "runtime:signoz"
    
    def test_add_gap_analysis_result(self):
        """Test adding gap analysis result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "discrepancies": [
                {"type": "unused_class", "name": "LegacyService"}
            ],
            "drift_score": 0.15
        }
        
        aggregator.add_gap_analysis_result(result_data)
        
        results = aggregator.results[AnalysisResultType.GAP_ANALYSIS]
        assert len(results) == 1
        assert results[0]["data"] == result_data
        assert results[0]["source"] == "gap_analyzer"
    
    def test_add_architecture_result(self):
        """Test adding architecture result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "bounded_contexts": ["orders", "payments"],
            "c4_diagrams": {"context": {}, "container": {}}
        }
        
        aggregator.add_architecture_result(result_data, "context_mapper")
        
        results = aggregator.results[AnalysisResultType.ARCHITECTURE]
        assert len(results) == 1
        assert results[0]["data"] == result_data
        assert results[0]["source"] == "context_mapper"
    
    def test_add_dependency_result(self):
        """Test adding dependency result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "nodes": ["ServiceA", "ServiceB"],
            "edges": [{"source": "ServiceA", "target": "ServiceB"}]
        }
        
        aggregator.add_dependency_result(result_data, "static_analyzer")
        
        results = aggregator.results[AnalysisResultType.DEPENDENCIES]
        assert len(results) == 1
        assert results[0]["data"] == result_data
    
    def test_add_performance_result(self):
        """Test adding performance result."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        result_data = {
            "metrics": {
                "p50": 45.2,
                "p95": 120.5,
                "p99": 250.8
            }
        }
        
        aggregator.add_performance_result(result_data, "load_tester")
        
        results = aggregator.results[AnalysisResultType.PERFORMANCE]
        assert len(results) == 1
        assert results[0]["data"] == result_data
    
    def test_add_multiple_results_same_type(self):
        """Test adding multiple results of the same type."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_static_analysis_result({"tool": "javaparser"}, "javaparser")
        aggregator.add_static_analysis_result({"tool": "codeql"}, "codeql")
        aggregator.add_static_analysis_result({"tool": "sonar"}, "sonar")
        
        results = aggregator.results[AnalysisResultType.STATIC_ANALYSIS]
        assert len(results) == 3
        assert set(r["source"] for r in results) == {"static:javaparser", "static:codeql", "static:sonar"}
    
    def test_add_result_with_metadata(self):
        """Test adding result with metadata."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        metadata = {
            "version": "1.0.0",
            "duration": 120.5,
            "confidence": 0.95
        }
        
        aggregator.add_static_analysis_result({"classes": 50}, "javaparser", metadata)
        
        result = aggregator.results[AnalysisResultType.STATIC_ANALYSIS][0]
        assert result["metadata"] == metadata


class TestDependencyMerging:
    """Test dependency graph merging strategies."""
    
    def test_merge_dependencies_union(self):
        """Test merging dependencies with UNION strategy."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add two dependency results
        aggregator.add_dependency_result(
            {
                "nodes": ["A", "B"],
                "edges": [{"source": "A", "target": "B", "type": "dependency"}]
            },
            "static_analyzer"
        )
        
        aggregator.add_dependency_result(
            {
                "nodes": ["B", "C"],
                "edges": [{"source": "B", "target": "C", "type": "dependency"}]
            },
            "runtime_monitor"
        )
        
        merged = aggregator.merge_dependencies(
            aggregator.results[AnalysisResultType.DEPENDENCIES],
            AggregationStrategy.UNION
        )
        
        assert set(merged["nodes"]) == {"A", "B", "C"}
        assert len(merged["edges"]) == 2
        assert "sources" in merged
        assert len(merged["sources"]) == 2
    
    def test_merge_dependencies_empty(self):
        """Test merging empty dependency list."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        merged = aggregator.merge_dependencies([])
        
        assert merged["nodes"] == []
        assert merged["edges"] == []
        assert merged["sources"] == []
    
    def test_merge_dependencies_duplicate_nodes(self):
        """Test merging handles duplicate nodes correctly."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_dependency_result(
            {"nodes": ["A", "B", "C"], "edges": []},
            "analyzer1"
        )
        
        aggregator.add_dependency_result(
            {"nodes": ["B", "C", "D"], "edges": []},
            "analyzer2"
        )
        
        merged = aggregator.merge_dependencies(
            aggregator.results[AnalysisResultType.DEPENDENCIES],
            AggregationStrategy.UNION
        )
        
        # Should have unique nodes only
        assert set(merged["nodes"]) == {"A", "B", "C", "D"}
        assert len(merged["nodes"]) == 4
    
    def test_merge_dependencies_duplicate_edges(self):
        """Test merging handles duplicate edges correctly."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        edge_data = {"source": "A", "target": "B", "type": "dependency"}
        
        aggregator.add_dependency_result(
            {"nodes": ["A", "B"], "edges": [edge_data]},
            "analyzer1"
        )
        
        aggregator.add_dependency_result(
            {"nodes": ["A", "B"], "edges": [edge_data]},
            "analyzer2"
        )
        
        merged = aggregator.merge_dependencies(
            aggregator.results[AnalysisResultType.DEPENDENCIES],
            AggregationStrategy.UNION
        )
        
        # Should deduplicate edges
        assert len(merged["edges"]) == 1


class TestArchitectureMerging:
    """Test architecture merging strategies."""
    
    def test_merge_architecture_prefer_runtime(self):
        """Test merging architecture with PREFER_RUNTIME strategy."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        static_arch = {"source_type": "static", "components": ["A", "B"]}
        runtime_arch = {"source_type": "runtime", "components": ["A", "B", "C"]}
        
        aggregator.add_architecture_result(static_arch, "static_analyzer")
        aggregator.add_architecture_result(runtime_arch, "runtime_monitor")
        
        merged = aggregator.merge_architecture(
            aggregator.results[AnalysisResultType.ARCHITECTURE],
            AggregationStrategy.PREFER_RUNTIME
        )
        
        assert merged == runtime_arch
    
    def test_merge_architecture_prefer_static(self):
        """Test merging architecture with PREFER_STATIC strategy."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        static_arch = {"source_type": "static", "components": ["A", "B"]}
        runtime_arch = {"source_type": "runtime", "components": ["A", "B", "C"]}
        
        aggregator.add_architecture_result(runtime_arch, "runtime_monitor")
        aggregator.add_architecture_result(static_arch, "static_analyzer")
        
        merged = aggregator.merge_architecture(
            aggregator.results[AnalysisResultType.ARCHITECTURE],
            AggregationStrategy.PREFER_STATIC
        )
        
        assert merged == static_arch
    
    def test_merge_architecture_empty(self):
        """Test merging empty architecture list."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        merged = aggregator.merge_architecture([])
        
        assert merged == {}


class TestPerformanceMerging:
    """Test performance metrics merging."""
    
    def test_merge_performance_metrics(self):
        """Test merging performance metrics with statistical aggregation."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_performance_result(
            {"metrics": {"p50": 45.0, "p95": 120.0}},
            "run1"
        )
        
        aggregator.add_performance_result(
            {"metrics": {"p50": 50.0, "p95": 130.0}},
            "run2"
        )
        
        aggregator.add_performance_result(
            {"metrics": {"p50": 55.0, "p95": 140.0}},
            "run3"
        )
        
        merged = aggregator.merge_performance_metrics(
            aggregator.results[AnalysisResultType.PERFORMANCE]
        )
        
        assert "metrics" in merged
        assert "p50" in merged["metrics"]
        assert "p95" in merged["metrics"]
        
        # Check p50 statistics
        p50_stats = merged["metrics"]["p50"]
        assert p50_stats["mean"] == 50.0
        assert p50_stats["min"] == 45.0
        assert p50_stats["max"] == 55.0
        assert p50_stats["count"] == 3
        
        # Check p95 statistics
        p95_stats = merged["metrics"]["p95"]
        assert p95_stats["mean"] == 130.0
        assert p95_stats["min"] == 120.0
        assert p95_stats["max"] == 140.0
    
    def test_merge_performance_empty(self):
        """Test merging empty performance list."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        merged = aggregator.merge_performance_metrics([])
        
        assert merged == {}
    
    def test_merge_performance_structured_metrics(self):
        """Test merging performance with structured metric format."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_performance_result(
            {"metrics": {"response_time": {"value": 100, "unit": "ms"}}},
            "run1"
        )
        
        aggregator.add_performance_result(
            {"metrics": {"response_time": {"value": 120, "unit": "ms"}}},
            "run2"
        )
        
        merged = aggregator.merge_performance_metrics(
            aggregator.results[AnalysisResultType.PERFORMANCE]
        )
        
        assert "response_time" in merged["metrics"]
        assert merged["metrics"]["response_time"]["mean"] == 110.0


class TestValidation:
    """Test result validation."""
    
    def test_validate_missing_required_results(self):
        """Test validation fails when required results are missing."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Don't add any results
        validation_passed = aggregator.validate_results()
        
        assert not validation_passed
        assert len(aggregator.validation_errors) > 0
        
        # Check that errors mention missing required types
        error_types = {err["type"] for err in aggregator.validation_errors}
        assert "missing_required_result" in error_types
    
    def test_validate_with_required_results(self):
        """Test validation passes with required results."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add required results
        aggregator.add_static_analysis_result({"data": "test"}, "analyzer")
        aggregator.add_dependency_result({"nodes": [], "edges": []}, "analyzer")
        
        validation_passed = aggregator.validate_results()
        
        assert validation_passed
        assert len(aggregator.validation_errors) == 0
    
    def test_validate_empty_result_data_warning(self):
        """Test validation warns about empty result data."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add required results
        aggregator.add_static_analysis_result({"data": "test"}, "analyzer")
        aggregator.add_dependency_result({"nodes": [], "edges": []}, "analyzer")
        
        # Add empty result
        aggregator.add_result(
            AnalysisResultType.PERFORMANCE,
            {},  # Empty data
            "test_source"
        )
        
        validation_passed = aggregator.validate_results()
        
        assert validation_passed  # Still passes, but has warnings
        assert len(aggregator.validation_warnings) > 0
        
        warning_types = {warn["type"] for warn in aggregator.validation_warnings}
        assert "empty_result_data" in warning_types


class TestAggregation:
    """Test final result aggregation."""
    
    def test_aggregate_results_structure(self):
        """Test aggregated results have correct structure."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add minimal required results
        aggregator.add_static_analysis_result({"classes": 50}, "javaparser")
        aggregator.add_dependency_result({"nodes": ["A"], "edges": []}, "analyzer")
        
        report = aggregator.aggregate_results()
        
        # Check top-level structure
        assert "analysis_id" in report
        assert "project_id" in report
        assert "created_at" in report
        assert "aggregated_at" in report
        assert "validation_passed" in report
        assert "validation_errors" in report
        assert "validation_warnings" in report
        
        # Check result sections
        assert "static_analysis" in report
        assert "runtime_analysis" in report
        assert "gap_analysis" in report
        assert "architecture" in report
        assert "dependencies" in report
        assert "performance" in report
        assert "compliance" in report
        assert "risk_assessment" in report
        
        # Check summary
        assert "summary" in report
        assert "total_results" in report["summary"]
        assert "result_counts_by_type" in report["summary"]
        assert "sources" in report["summary"]
    
    def test_aggregate_results_counts(self):
        """Test aggregated results counts are accurate."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add various results
        aggregator.add_static_analysis_result({"data": 1}, "tool1")
        aggregator.add_static_analysis_result({"data": 2}, "tool2")
        aggregator.add_dependency_result({"nodes": []}, "tool3")
        aggregator.add_performance_result({"metrics": {}}, "tool4")
        
        report = aggregator.aggregate_results()
        
        assert report["summary"]["total_results"] == 4
        assert report["static_analysis"]["count"] == 2
        # Dependencies and performance are merged, so check the merged structure
        assert "nodes" in report["dependencies"]
        assert "metrics" in report["performance"]
    
    def test_aggregate_results_merged_dependencies(self):
        """Test aggregation includes merged dependencies."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        # Add required results
        aggregator.add_static_analysis_result({"data": "test"}, "analyzer")
        
        # Add multiple dependency results
        aggregator.add_dependency_result(
            {"nodes": ["A", "B"], "edges": []},
            "static"
        )
        aggregator.add_dependency_result(
            {"nodes": ["C", "D"], "edges": []},
            "runtime"
        )
        
        report = aggregator.aggregate_results()
        
        # Check merged dependencies
        merged_deps = report["dependencies"]
        assert "nodes" in merged_deps
        assert "edges" in merged_deps
        assert "sources" in merged_deps
        assert len(merged_deps["sources"]) == 2
    
    def test_aggregate_results_sources_list(self):
        """Test aggregation includes all unique sources."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_static_analysis_result({"data": 1}, "javaparser")
        aggregator.add_static_analysis_result({"data": 2}, "codeql")
        aggregator.add_runtime_analysis_result({"data": 3}, "signoz")
        aggregator.add_dependency_result({"nodes": []}, "analyzer")
        
        report = aggregator.aggregate_results()
        
        sources = set(report["summary"]["sources"])
        assert "static:javaparser" in sources
        assert "static:codeql" in sources
        assert "runtime:signoz" in sources
        assert "analyzer" in sources


class TestGetSummary:
    """Test summary retrieval."""
    
    def test_get_summary_structure(self):
        """Test summary has correct structure."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_static_analysis_result({"data": "test"}, "tool")
        
        summary = aggregator.get_summary()
        
        assert "analysis_id" in summary
        assert "project_id" in summary
        assert "created_at" in summary
        assert "total_results" in summary
        assert "result_counts" in summary
        assert "sources" in summary
        assert "validation_errors" in summary
        assert "validation_warnings" in summary
    
    def test_get_summary_accurate_counts(self):
        """Test summary counts are accurate."""
        aggregator = ResultAggregator(uuid4(), uuid4())
        
        aggregator.add_static_analysis_result({"data": 1}, "tool1")
        aggregator.add_static_analysis_result({"data": 2}, "tool2")
        aggregator.add_runtime_analysis_result({"data": 3}, "tool3")
        
        summary = aggregator.get_summary()
        
        assert summary["total_results"] == 3
        assert summary["result_counts"]["static_analysis"] == 2
        assert summary["result_counts"]["runtime_analysis"] == 1


class TestOrchestratorIntegration:
    """Test integration with AnalysisOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_creates_aggregator(self):
        """Test orchestrator creates aggregator on analysis start."""
        from omega_analysis.services.orchestration.analysis_orchestrator import (
            AnalysisOrchestrator
        )
        
        orchestrator = AnalysisOrchestrator()
        project_id = uuid4()
        
        result = await orchestrator.start_analysis(project_id)
        analysis_id_str = result["analysis_id"]
        
        # Check aggregator was created
        assert len(orchestrator.result_aggregators) == 1
        # Convert string back to UUID for comparison
        from uuid import UUID
        analysis_id = UUID(analysis_id_str)
        assert analysis_id in orchestrator.result_aggregators
    
    @pytest.mark.asyncio
    async def test_add_result_to_orchestrator(self):
        """Test adding results through orchestrator."""
        from omega_analysis.services.orchestration.analysis_orchestrator import (
            AnalysisOrchestrator
        )
        from uuid import UUID
        
        orchestrator = AnalysisOrchestrator()
        project_id = uuid4()
        
        result = await orchestrator.start_analysis(project_id)
        analysis_id = UUID(result["analysis_id"])
        
        # Add a result
        await orchestrator.add_analysis_result(
            analysis_id,
            "static_analysis",
            {"classes": 100},
            "javaparser"
        )
        
        # Verify result was added
        aggregator = orchestrator.result_aggregators[analysis_id]
        assert len(aggregator.results[AnalysisResultType.STATIC_ANALYSIS]) == 1
    
    @pytest.mark.asyncio
    async def test_get_aggregated_results_from_orchestrator(self):
        """Test retrieving aggregated results through orchestrator."""
        from omega_analysis.services.orchestration.analysis_orchestrator import (
            AnalysisOrchestrator
        )
        from uuid import UUID
        
        orchestrator = AnalysisOrchestrator()
        project_id = uuid4()
        
        result = await orchestrator.start_analysis(project_id)
        analysis_id = UUID(result["analysis_id"])
        
        # Add results
        await orchestrator.add_analysis_result(
            analysis_id,
            "static_analysis",
            {"classes": 100},
            "javaparser"
        )
        
        await orchestrator.add_analysis_result(
            analysis_id,
            "dependencies",
            {"nodes": ["A", "B"], "edges": []},
            "analyzer"
        )
        
        # Get aggregated results
        aggregated = await orchestrator.get_aggregated_results(analysis_id)
        
        assert "analysis_id" in aggregated
        assert "static_analysis" in aggregated
        assert "dependencies" in aggregated
        assert aggregated["validation_passed"] is True
