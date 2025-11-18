"""Integration tests for gap analysis comparison engine.

Tests gap analysis comparing static and runtime results:
- Discrepancy identification
- Complexity scoring
- Migration readiness assessment
- Go/No-Go decision making
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.omega_analysis.analysis.gap.gap_analyzer import (
    GapAnalyzer,
    GapAnalysisResult,
    DiscrepancyFinding,
    ComplexityScore,
    MigrationReadinessAssessment,
    GapCategory,
    DiscrepancySeverity
)
from src.omega_analysis.analysis.static.appcat import (
    AppCATResults,
    TechnologyAssessment,
    ArchitecturalPattern,
    DataAccessPattern,
    CloudReadinessAssessment
)
from src.omega_analysis.services.orchestration.runtime_analyzer import (
    RuntimeAnalysisResults,
    PerformanceBaseline
)


@pytest.fixture
def gap_analyzer():
    """Provide gap analyzer instance."""
    return GapAnalyzer()


@pytest.fixture
def mock_appcat_results():
    """Provide mock AppCAT results."""
    return AppCATResults(
        technology_assessments=[
            TechnologyAssessment(
                name="Spring Framework",
                version="5.3.23",
                assessment_status="Supported",
                migration_effort="Low",
                recommended_alternative=None,
                notes=["Cloud-ready framework"],
                confidence_level=0.95
            ),
            TechnologyAssessment(
                name="Legacy Library",
                version="1.0.0",
                assessment_status="Not Supported",
                migration_effort="High",
                recommended_alternative="Modern Alternative",
                notes=["Requires replacement"],
                confidence_level=0.90
            )
        ],
        architectural_patterns=[
            ArchitecturalPattern(
                pattern_name="Layered Architecture",
                pattern_type="Layered",
                components=["Controller", "Service", "Repository"],
                complexity_score=6.5,
                migration_readiness="Partial",
                recommendations=["Implement API versioning", "Add circuit breakers"]
            ),
            ArchitecturalPattern(
                pattern_name="Monolithic Structure",
                pattern_type="Monolith",
                components=["Core", "UI", "Data"],
                complexity_score=8.5,
                migration_readiness="Needs Refactoring",
                recommendations=["Decompose into microservices", "Implement service boundaries"]
            )
        ],
        data_access_patterns=[
            DataAccessPattern(
                pattern_type="ORM",
                technologies=["Hibernate", "JPA"],
                complexity_assessment="Medium",
                migration_considerations=["Review connection pooling"],
                recommended_approach="Spring Data JPA"
            )
        ],
        cloud_readiness=CloudReadinessAssessment(
            overall_readiness_score=72.5,
            readiness_category="Cloud Friendly",
            blockers=["Hard-coded configuration", "File system dependencies"],
            recommendations=["Externalize configuration", "Use cloud storage"],
            estimated_effort_weeks=12
        ),
        metrics={
            "technology_assessment": {
                "total_technologies": 2,
                "by_migration_effort": {"Low": 1, "High": 1}
            }
        },
        assessment_metadata={
            "assessment_timestamp": datetime.now().isoformat(),
            "source_path": "/test/path"
        }
    )


@pytest.fixture
def mock_runtime_results():
    """Provide mock runtime results."""
    baseline = PerformanceBaseline(
        baseline_id="baseline_test_001",
        application_name="test-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=10.0,
        response_time_mean=150.0,
        response_time_median=120.0,
        response_time_p95=450.0,  # Below 500ms threshold
        response_time_p99=650.0,
        response_time_max=1200.0,
        requests_per_second=16.67,
        error_rate=0.02,  # 2% error rate
        errors_by_type={"timeout": 20},
        statistical_confidence=0.95,
        sample_size=1000,
        data_quality_score=0.85
    )
    
    results = RuntimeAnalysisResults(
        analysis_id="runtime_test_001",
        application_name="test-app",
        output_directory=Path("/tmp/test"),
        baseline=baseline
    )
    
    return results


@pytest.fixture
def mock_static_results():
    """Provide mock static analysis results."""
    return {
        "analysis_id": "static_test_001",
        "dependency_analysis": {
            "total_dependencies": 50,
            "circular_dependencies": [
                {"source": "ModuleA", "target": "ModuleB", "chain": ["A", "B", "C", "A"]}
            ]
        },
        "codeql_analysis": {
            "findings": [
                {"severity": "high", "type": "SQL Injection", "location": "UserController.java:42"},
                {"severity": "medium", "type": "XSS", "location": "OutputHelper.java:15"}
            ],
            "summary": {
                "total": 2,
                "high": 1,
                "medium": 1
            }
        }
    }


def test_gap_analyzer_initialization(gap_analyzer):
    """Test gap analyzer initialization."""
    assert gap_analyzer is not None
    assert gap_analyzer.config is not None
    assert "performance_thresholds" in gap_analyzer.config
    assert "complexity_weights" in gap_analyzer.config


def test_analyze_gaps_basic(gap_analyzer):
    """Test basic gap analysis without input data."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app"
    )
    
    assert results is not None
    assert results.application_name == "test-app"
    assert results.analysis_id.startswith("gap_test-app")
    assert isinstance(results.discrepancies, list)
    assert isinstance(results.complexity_score, ComplexityScore)
    assert isinstance(results.readiness_assessment, MigrationReadinessAssessment)


def test_analyze_gaps_with_appcat(gap_analyzer, mock_appcat_results):
    """Test gap analysis with AppCAT results."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        appcat_results=mock_appcat_results
    )
    
    # Should identify architectural discrepancies
    arch_discrepancies = [d for d in results.discrepancies 
                         if d.category == GapCategory.ARCHITECTURAL]
    assert len(arch_discrepancies) > 0
    
    # Should identify technology gaps
    tech_discrepancies = [d for d in results.discrepancies 
                         if d.category == GapCategory.TECHNOLOGY]
    assert len(tech_discrepancies) > 0
    
    # Should have "Needs Refactoring" pattern
    monolith_issue = [d for d in results.discrepancies 
                     if "Monolithic" in d.title]
    assert len(monolith_issue) > 0


def test_analyze_gaps_with_runtime(gap_analyzer, mock_runtime_results):
    """Test gap analysis with runtime results."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        runtime_results=mock_runtime_results
    )
    
    # Should analyze performance
    assert results.complexity_score.performance_complexity >= 0
    
    # P95 is 450ms (below 500ms threshold) so shouldn't flag as critical
    perf_discrepancies = [d for d in results.discrepancies 
                         if d.category == GapCategory.PERFORMANCE]
    
    # May have error rate issue (2% > threshold)
    # But overall performance should be reasonable


def test_analyze_gaps_with_static(gap_analyzer, mock_static_results):
    """Test gap analysis with static results."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        static_results=mock_static_results
    )
    
    # Should identify circular dependencies
    dep_discrepancies = [d for d in results.discrepancies 
                        if d.category == GapCategory.DEPENDENCY]
    assert len(dep_discrepancies) > 0
    
    circular_dep = [d for d in dep_discrepancies 
                   if "Circular" in d.title]
    assert len(circular_dep) > 0
    assert circular_dep[0].severity == DiscrepancySeverity.HIGH
    
    # Should identify security issues
    sec_discrepancies = [d for d in results.discrepancies 
                        if d.category == GapCategory.SECURITY]
    assert len(sec_discrepancies) > 0
    
    high_severity_sec = [d for d in sec_discrepancies 
                        if d.severity == DiscrepancySeverity.CRITICAL]
    assert len(high_severity_sec) > 0


def test_complexity_scoring(gap_analyzer, mock_appcat_results, mock_runtime_results):
    """Test complexity scoring algorithm."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        appcat_results=mock_appcat_results,
        runtime_results=mock_runtime_results
    )
    
    complexity = results.complexity_score
    
    # Verify all component scores present
    assert 0 <= complexity.architectural_complexity <= 100
    assert 0 <= complexity.coupling_complexity <= 100
    assert 0 <= complexity.performance_complexity <= 100
    assert 0 <= complexity.technology_complexity <= 100
    assert 0 <= complexity.data_complexity <= 100
    
    # Overall score should be weighted average
    assert 0 <= complexity.overall_score <= 100
    
    # Should have complexity level
    assert complexity.complexity_level in ["Low", "Medium", "High", "Very High"]
    
    # Should have effort estimate
    assert complexity.estimated_effort_weeks > 0
    
    # Should identify factors and opportunities
    assert isinstance(complexity.complexity_factors, list)
    assert isinstance(complexity.simplification_opportunities, list)


def test_readiness_assessment(gap_analyzer, mock_appcat_results, mock_runtime_results):
    """Test migration readiness assessment."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        appcat_results=mock_appcat_results,
        runtime_results=mock_runtime_results
    )
    
    readiness = results.readiness_assessment
    
    # Verify all sub-scores present
    assert 0 <= readiness.technical_readiness <= 100
    assert 0 <= readiness.architectural_readiness <= 100
    assert 0 <= readiness.performance_readiness <= 100
    assert 0 <= readiness.organizational_readiness <= 100
    
    # Overall readiness
    assert 0 <= readiness.readiness_score <= 100
    assert readiness.readiness_category in ["Ready", "Nearly Ready", "Needs Work", "Not Ready"]
    
    # Go/No-Go decision
    assert readiness.go_no_go_recommendation in ["GO", "CONDITIONAL GO", "NO GO"]
    assert isinstance(readiness.go_no_go_rationale, str)
    assert len(readiness.go_no_go_rationale) > 0
    
    # Blockers and prerequisites
    assert isinstance(readiness.critical_blockers, list)
    assert isinstance(readiness.prerequisites, list)
    
    # Recommended approach
    assert readiness.recommended_approach in ["Big Bang", "Strangler Fig", "Parallel Run"]
    assert readiness.estimated_timeline_months > 0
    assert 0 <= readiness.confidence_level <= 1.0


def test_performance_gap_detection(gap_analyzer):
    """Test performance gap detection with high P95."""
    # Create baseline with high P95 (>500ms threshold)
    high_p95_baseline = PerformanceBaseline(
        baseline_id="baseline_high_p95",
        application_name="slow-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=100.0,
        response_time_mean=400.0,
        response_time_median=350.0,
        response_time_p95=1200.0,  # Above 500ms threshold - should flag
        response_time_p99=2000.0,
        response_time_max=3000.0,
        requests_per_second=10.0,
        error_rate=0.01,
        errors_by_type={},
        statistical_confidence=0.95,
        sample_size=1000,
        data_quality_score=0.90
    )
    
    runtime_results = RuntimeAnalysisResults(
        analysis_id="runtime_slow",
        application_name="slow-app",
        output_directory=Path("/tmp/test"),
        baseline=high_p95_baseline
    )
    
    results = gap_analyzer.analyze_gaps(
        application_name="slow-app",
        runtime_results=runtime_results
    )
    
    # Should detect high P95 issue
    perf_issues = [d for d in results.discrepancies 
                  if d.finding_id == "perf_p95_high"]
    assert len(perf_issues) > 0
    assert perf_issues[0].severity in [DiscrepancySeverity.HIGH, DiscrepancySeverity.MEDIUM]


def test_error_rate_gap_detection(gap_analyzer):
    """Test error rate gap detection."""
    # Create baseline with high error rate (>5% threshold)
    high_error_baseline = PerformanceBaseline(
        baseline_id="baseline_high_error",
        application_name="unstable-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=10.0,
        response_time_mean=50.0,
        response_time_median=45.0,
        response_time_p95=120.0,
        response_time_p99=200.0,
        response_time_max=500.0,
        requests_per_second=16.67,
        error_rate=0.15,  # 15% error rate - should flag
        errors_by_type={"timeout": 100, "connection_error": 50},
        statistical_confidence=0.95,
        sample_size=1000,
        data_quality_score=0.75
    )
    
    runtime_results = RuntimeAnalysisResults(
        analysis_id="runtime_unstable",
        application_name="unstable-app",
        output_directory=Path("/tmp/test"),
        baseline=high_error_baseline
    )
    
    results = gap_analyzer.analyze_gaps(
        application_name="unstable-app",
        runtime_results=runtime_results
    )
    
    # Should detect high error rate
    error_issues = [d for d in results.discrepancies 
                   if d.finding_id == "perf_error_rate_high"]
    assert len(error_issues) > 0
    assert error_issues[0].severity == DiscrepancySeverity.HIGH


def test_go_no_go_with_critical_blockers(gap_analyzer, mock_static_results):
    """Test Go/No-Go decision with critical blockers."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        static_results=mock_static_results
    )
    
    # Should have critical security blocker
    assert len(results.readiness_assessment.critical_blockers) > 0
    
    # Should be NO GO
    assert results.readiness_assessment.go_no_go_recommendation == "NO GO"


def test_go_no_go_conditional(gap_analyzer, mock_appcat_results):
    """Test conditional GO scenario."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        appcat_results=mock_appcat_results
    )
    
    # With moderate complexity and some issues, should be conditional
    # (exact outcome depends on scoring, but should not be blocked)
    assert results.readiness_assessment.go_no_go_recommendation in ["GO", "CONDITIONAL GO"]


def test_complexity_level_categorization(gap_analyzer):
    """Test complexity level categorization."""
    # Test with different configurations to trigger different levels
    
    # Low complexity scenario
    simple_appcat = AppCATResults(
        technology_assessments=[
            TechnologyAssessment(
                name="Spring Boot",
                version="3.0.0",
                assessment_status="Supported",
                migration_effort="Low",
                recommended_alternative=None,
                notes=["Modern framework"],
                confidence_level=0.98
            )
        ],
        architectural_patterns=[
            ArchitecturalPattern(
                pattern_name="Simple Layered",
                pattern_type="Layered",
                components=["Controller", "Service"],
                complexity_score=2.5,  # Low complexity
                migration_readiness="Ready",
                recommendations=["Minor improvements"]
            )
        ],
        data_access_patterns=[],
        cloud_readiness=CloudReadinessAssessment(
            overall_readiness_score=85.0,
            readiness_category="Cloud Ready",
            blockers=[],
            recommendations=["Minor optimizations"],
            estimated_effort_weeks=6
        ),
        metrics={},
        assessment_metadata={}
    )
    
    results = gap_analyzer.analyze_gaps(
        application_name="simple-app",
        appcat_results=simple_appcat
    )
    
    # Should have lower complexity
    assert results.complexity_score.complexity_level in ["Low", "Medium"]


def test_gap_metrics_calculation(gap_analyzer, mock_appcat_results, mock_runtime_results, mock_static_results):
    """Test gap metrics calculation."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        static_results=mock_static_results,
        runtime_results=mock_runtime_results,
        appcat_results=mock_appcat_results
    )
    
    metrics = results.gap_metrics
    
    # Should have total count
    assert "total_discrepancies" in metrics
    assert metrics["total_discrepancies"] == len(results.discrepancies)
    
    # Should have breakdown by severity
    assert "by_severity" in metrics
    severity_breakdown = metrics["by_severity"]
    assert all(sev in severity_breakdown for sev in ["critical", "high", "medium", "low", "info"])
    
    # Should have breakdown by category
    assert "by_category" in metrics
    
    # Should have complexity summary
    assert "complexity_summary" in metrics
    complexity_summary = metrics["complexity_summary"]
    assert "overall_score" in complexity_summary
    assert "level" in complexity_summary
    assert "estimated_effort_weeks" in complexity_summary
    
    # Should have readiness summary
    assert "readiness_summary" in metrics
    readiness_summary = metrics["readiness_summary"]
    assert "overall_score" in readiness_summary
    assert "category" in readiness_summary
    assert "recommendation" in readiness_summary
    
    # Should have average confidence
    assert "average_confidence" in metrics


def test_discrepancy_summary(gap_analyzer, mock_appcat_results, mock_static_results):
    """Test discrepancy summarization."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        static_results=mock_static_results,
        appcat_results=mock_appcat_results
    )
    
    summary = results.discrepancy_summary
    
    # Should have severity counts
    assert any(k.startswith("severity_") for k in summary.keys())
    
    # Should have category counts
    assert any(k.startswith("category_") for k in summary.keys())
    
    # Counts should match actual discrepancies
    total_by_severity = sum(v for k, v in summary.items() if k.startswith("severity_"))
    total_by_category = sum(v for k, v in summary.items() if k.startswith("category_"))
    assert total_by_severity == len(results.discrepancies)
    assert total_by_category == len(results.discrepancies)


def test_validation_status(gap_analyzer, mock_static_results):
    """Test validation status determination."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        static_results=mock_static_results
    )
    
    # Should have validation status
    assert results.validation_status in ["passed", "warnings", "failed"]
    
    # With critical security issues, should have warnings
    assert results.validation_status in ["warnings", "failed"]


def test_export_results(gap_analyzer, tmp_path):
    """Test exporting gap analysis results."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app"
    )
    
    output_file = tmp_path / "gap_analysis.json"
    gap_analyzer.export_results(results, output_file)
    
    # File should exist
    assert output_file.exists()
    
    # Should be valid JSON
    import json
    with open(output_file) as f:
        data = json.load(f)
        
    # Should have key fields
    assert data["analysis_id"] == results.analysis_id
    assert data["application_name"] == "test-app"
    assert "discrepancies" in data
    assert "complexity_score" in data
    assert "readiness_assessment" in data
    assert "gap_metrics" in data


def test_recommended_approach_selection(gap_analyzer):
    """Test migration approach recommendation."""
    # Low complexity -> Big Bang
    simple_appcat = AppCATResults(
        technology_assessments=[],
        architectural_patterns=[
            ArchitecturalPattern(
                pattern_name="Simple",
                pattern_type="Layered",
                components=["A", "B"],
                complexity_score=2.0,
                migration_readiness="Ready",
                recommendations=[]
            )
        ],
        data_access_patterns=[],
        cloud_readiness=CloudReadinessAssessment(
            overall_readiness_score=90.0,
            readiness_category="Cloud Ready",
            blockers=[],
            recommendations=[],
            estimated_effort_weeks=4
        ),
        metrics={},
        assessment_metadata={}
    )
    
    results = gap_analyzer.analyze_gaps(
        application_name="simple-app",
        appcat_results=simple_appcat
    )
    
    # Low complexity should recommend Big Bang or Strangler Fig
    assert results.readiness_assessment.recommended_approach in ["Big Bang", "Strangler Fig"]
    
    # Timeline should be reasonable
    assert results.readiness_assessment.estimated_timeline_months <= 12


def test_confidence_scoring(gap_analyzer, mock_runtime_results):
    """Test confidence level in readiness assessment."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        runtime_results=mock_runtime_results
    )
    
    # Should use runtime data quality score
    assert results.readiness_assessment.confidence_level == mock_runtime_results.baseline.data_quality_score


def test_simplification_opportunities(gap_analyzer, mock_appcat_results, mock_runtime_results):
    """Test identification of simplification opportunities."""
    results = gap_analyzer.analyze_gaps(
        application_name="test-app",
        appcat_results=mock_appcat_results,
        runtime_results=mock_runtime_results
    )
    
    opportunities = results.complexity_score.simplification_opportunities
    
    # Should identify opportunities
    assert isinstance(opportunities, list)
    
    # With cloud readiness >70, should mention it
    cloud_opportunity = [o for o in opportunities if "cloud readiness" in o.lower()]
    assert len(cloud_opportunity) > 0


def test_custom_config(gap_analyzer):
    """Test gap analyzer with custom configuration."""
    custom_config = {
        "performance_thresholds": {
            "p95_response_time_ms": 1000,  # More lenient
            "error_rate": 0.10,
            "min_throughput_rps": 5
        },
        "complexity_weights": {
            "architectural": 0.30,
            "coupling": 0.30,
            "performance": 0.15,
            "technology": 0.15,
            "data": 0.10
        },
        "severity_thresholds": {
            "critical_blocker_threshold": 2,
            "high_severity_threshold": 5
        }
    }
    
    custom_analyzer = GapAnalyzer(config=custom_config)
    
    # Verify config applied
    assert custom_analyzer.config["performance_thresholds"]["p95_response_time_ms"] == 1000
    assert custom_analyzer.config["complexity_weights"]["architectural"] == 0.30


def test_empty_inputs_handling(gap_analyzer):
    """Test handling of minimal/empty inputs."""
    results = gap_analyzer.analyze_gaps(
        application_name="minimal-app",
        static_results=None,
        runtime_results=None,
        appcat_results=None
    )
    
    # Should still produce valid results
    assert results is not None
    assert results.application_name == "minimal-app"
    assert isinstance(results.complexity_score, ComplexityScore)
    assert isinstance(results.readiness_assessment, MigrationReadinessAssessment)
    
    # Default complexity should be moderate
    assert 30 <= results.complexity_score.overall_score <= 70


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
