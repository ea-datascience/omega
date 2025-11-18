"""Integration tests for runtime analysis orchestrator.

Tests end-to-end runtime analysis workflow including:
- SigNoz deployment coordination
- OTel instrumentation generation
- Synthetic load testing
- Performance baseline collection
- Results validation
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
from datetime import datetime

from src.omega_analysis.services.orchestration.runtime_analyzer import (
    RuntimeAnalysisOrchestrator,
    RuntimeAnalysisTask,
    PerformanceBaseline,
    RuntimeAnalysisResults,
)
from src.omega_analysis.analysis.runtime.load_generator import LoadPattern, Endpoint


@pytest.fixture
def output_dir():
    """Provide temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def orchestrator(output_dir):
    """Provide runtime orchestrator instance."""
    return RuntimeAnalysisOrchestrator(base_output_dir=output_dir)


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator, output_dir):
    """Test orchestrator initialization."""
    assert orchestrator.base_output_dir == output_dir
    assert output_dir.exists()
    assert isinstance(orchestrator.active_tasks, dict)
    assert isinstance(orchestrator.completed_analyses, dict)
    assert orchestrator.signoz_deployer is not None
    assert orchestrator.load_orchestrator is not None


@pytest.mark.asyncio
async def test_task_creation(orchestrator):
    """Test runtime analysis task creation."""
    task = await orchestrator._create_task(
        task_type="deploy",
        application_name="test-app",
        config={"environment": "docker-compose"}
    )
    
    assert task.task_id in orchestrator.active_tasks
    assert task.task_type == "deploy"
    assert task.application_name == "test-app"
    assert task.status == "pending"
    assert task.config["environment"] == "docker-compose"


@pytest.mark.asyncio
async def test_signoz_deployment_execution(orchestrator):
    """Test SigNoz deployment task execution."""
    task = await orchestrator._create_task(
        task_type="deploy",
        application_name="test-app"
    )
    
    deployment_status = await orchestrator._execute_signoz_deployment(task)
    
    assert task.status == "completed"
    assert task.start_time is not None
    assert task.end_time is not None
    assert deployment_status.deployment_id is not None
    # Will be mock mode since SigNoz services not guaranteed
    assert deployment_status.status in ["healthy", "mock"]
    assert deployment_status.performance_overhead < 1.0  # FR-002


@pytest.mark.asyncio
async def test_instrumentation_generation_execution(orchestrator, output_dir):
    """Test OTel instrumentation generation task execution."""
    task = await orchestrator._create_task(
        task_type="instrument",
        application_name="test-app",
        config={
            "namespace": "test",
            "mode": "hybrid",
        }
    )
    
    artifacts = await orchestrator._execute_instrumentation_generation(task, output_dir)
    
    assert task.status == "completed"
    assert task.start_time is not None
    assert task.end_time is not None
    assert artifacts.config_id is not None
    assert artifacts.mode == "hybrid"
    assert len(artifacts.files) == 9  # All artifact types


@pytest.mark.asyncio
async def test_load_testing_execution(orchestrator):
    """Test synthetic load testing task execution."""
    # Use httpbin.org as reliable test endpoint
    base_url = "https://httpbin.org"
    
    task = await orchestrator._create_task(
        task_type="load_test",
        application_name="test-app",
        base_url=base_url,
        config={
            "scenarios": [
                {
                    "name": "quick-test",
                    "pattern": "constant",
                    "duration": 0.1,  # 6 seconds
                    "users": 2,
                    "endpoints": [
                        {"path": "/status/200", "method": "GET", "weight": 1}
                    ]
                }
            ]
        }
    )
    
    results = await orchestrator._execute_load_testing(task, base_url)
    
    assert task.status == "completed"
    assert "quick-test" in results
    assert results["quick-test"].total_requests > 0
    assert results["quick-test"].error_rate < 0.1  # Less than 10% errors


@pytest.mark.asyncio
async def test_performance_baseline_collection(orchestrator):
    """Test performance baseline collection from load test results."""
    from src.omega_analysis.analysis.runtime.load_generator import LoadTestResults
    
    # Create mock load test results
    mock_results = {
        "baseline": LoadTestResults(
            scenario_name="baseline",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_requests=1000,
            successful_requests=950,
            failed_requests=50,
            response_times=[50.0] * 1000,  # Required field
            min_response_time=10.0,
            max_response_time=500.0,
            mean_response_time=50.0,
            median_response_time=45.0,
            p95_response_time=120.0,
            p99_response_time=200.0,
            requests_per_second=16.67,
            error_rate=0.05,
            errors_by_type={"timeout": 50},
            statistical_confidence=0.95,
            sample_size=1000
        )
    }
    
    task = await orchestrator._create_task(
        task_type="collect_baseline",
        application_name="test-app",
        config={"primary_scenario": "baseline"}
    )
    
    baseline = await orchestrator._collect_performance_baseline(task, mock_results)
    
    assert task.status == "completed"
    assert baseline.baseline_id is not None
    assert baseline.application_name == "test-app"
    assert baseline.total_requests == 1000
    assert baseline.response_time_mean == 50.0
    assert baseline.response_time_p95 == 120.0
    assert baseline.statistical_confidence == 0.95
    assert baseline.data_quality_score > 0.7


@pytest.mark.asyncio
async def test_load_scenario_generation(orchestrator):
    """Test load scenario generation from configuration."""
    scenarios = orchestrator._generate_load_scenarios(
        application_name="test-app",
        base_url="http://localhost:8080",
        config={
            "scenarios": [
                {
                    "name": "test-constant",
                    "pattern": "constant",
                    "duration": 5,
                    "users": 10,
                },
                {
                    "name": "test-stepped",
                    "pattern": "stepped",
                    "duration": 10,
                    "base_users": 10,
                    "peak_users": 50,
                }
            ]
        }
    )
    
    assert len(scenarios) == 2
    assert scenarios[0].name == "test-constant"
    assert scenarios[0].pattern.pattern_type == "constant"
    assert scenarios[0].pattern.base_users == 10
    assert scenarios[1].name == "test-stepped"
    assert scenarios[1].pattern.pattern_type == "stepped"
    assert scenarios[1].pattern.peak_users == 50


@pytest.mark.asyncio
async def test_data_quality_score_calculation(orchestrator):
    """Test data quality score calculation."""
    from src.omega_analysis.analysis.runtime.load_generator import LoadTestResults
    
    # High quality: many samples, low errors, high confidence
    high_quality = LoadTestResults(
        scenario_name="high-quality",
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_requests=2000,
        successful_requests=1999,
        failed_requests=1,
        response_times=[50.0] * 2000,
        min_response_time=10.0,
        max_response_time=100.0,
        mean_response_time=50.0,
        median_response_time=48.0,
        p95_response_time=80.0,
        p99_response_time=95.0,
        requests_per_second=33.33,
        error_rate=0.0005,
        errors_by_type={},
        statistical_confidence=0.99,
        sample_size=2000
    )
    
    score = orchestrator._calculate_data_quality_score(high_quality)
    assert score > 0.9  # High quality
    
    # Low quality: few samples, high errors, low confidence
    low_quality = LoadTestResults(
        scenario_name="low-quality",
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_requests=100,
        successful_requests=70,
        failed_requests=30,
        response_times=[200.0] * 100,
        min_response_time=10.0,
        max_response_time=1000.0,
        mean_response_time=200.0,
        median_response_time=150.0,
        p95_response_time=500.0,
        p99_response_time=900.0,
        requests_per_second=1.67,
        error_rate=0.30,
        errors_by_type={"timeout": 30},
        statistical_confidence=0.80,
        sample_size=100
    )
    
    score = orchestrator._calculate_data_quality_score(low_quality)
    assert score < 0.7  # Low quality


@pytest.mark.asyncio
async def test_summary_metrics_generation(orchestrator):
    """Test summary metrics generation."""
    from src.omega_analysis.analysis.runtime.signoz_deployer import DeploymentStatus
    from src.omega_analysis.analysis.runtime.otel_instrumentation import InstrumentationArtifacts
    from src.omega_analysis.analysis.runtime.load_generator import LoadTestResults
    
    results = RuntimeAnalysisResults(
        analysis_id="test-123",
        application_name="test-app",
        output_directory=Path("/tmp/test"),
    )
    
    # Add deployment status
    results.signoz_deployment = DeploymentStatus(
        deployment_id="deploy-123",
        status="healthy",
        performance_overhead=0.5,
        health_checks={"collector": True, "query": True},
        endpoints={},
        deployment_time=datetime.now()
    )
    
    # Add instrumentation artifacts
    results.instrumentation_artifacts = InstrumentationArtifacts(
        config_id="config-123",
        application_name="test-app",
        mode="hybrid",
        files={"agent": Path("/tmp/agent.conf")},
        jvm_args=["-javaagent:/path/to/agent.jar"],
        maven_dependencies=["io.opentelemetry:opentelemetry-api:2.10.0"],
        spring_boot_properties={"management.otlp.tracing.endpoint": "http://localhost:4318"},
        annotations_usage={"@WithSpan": ["public void method()"]},
        generated_at=datetime.now()
    )
    
    # Add load test results
    results.load_test_results = {
        "test1": LoadTestResults(
            scenario_name="test1",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_requests=1000,
            successful_requests=950,
            failed_requests=50,
            response_times=[50.0] * 1000,
            min_response_time=10.0,
            max_response_time=100.0,
            mean_response_time=50.0,
            median_response_time=48.0,
            p95_response_time=80.0,
            p99_response_time=95.0,
            requests_per_second=16.67,
            error_rate=0.05,
            errors_by_type={},
            statistical_confidence=0.95,
            sample_size=1000
        )
    }
    
    # Add baseline
    results.baseline = PerformanceBaseline(
        baseline_id="baseline-123",
        application_name="test-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=10.0,
        response_time_mean=50.0,
        response_time_median=48.0,
        response_time_p95=80.0,
        response_time_p99=95.0,
        response_time_max=100.0,
        requests_per_second=16.67,
        error_rate=0.05,
        errors_by_type={},
        statistical_confidence=0.95,
        sample_size=1000,
        data_quality_score=0.85
    )
    
    summary = orchestrator._generate_summary_metrics(results)
    
    assert summary["analysis_id"] == "test-123"
    assert summary["signoz_status"] == "healthy"
    assert summary["performance_overhead"] == 0.5
    assert summary["instrumentation_mode"] == "hybrid"
    assert summary["load_test_scenarios"] == 1
    assert summary["baseline_collected"] is True
    assert summary["baseline_p95_ms"] == 80.0
    assert summary["data_quality_score"] == 0.85


@pytest.mark.asyncio
async def test_results_validation_success(orchestrator):
    """Test results validation with passing requirements."""
    from src.omega_analysis.analysis.runtime.signoz_deployer import DeploymentStatus
    
    results = RuntimeAnalysisResults(
        analysis_id="test-valid",
        application_name="test-app",
        output_directory=Path("/tmp/test"),
    )
    
    # Add valid deployment (<1% overhead)
    results.signoz_deployment = DeploymentStatus(
        deployment_id="deploy-123",
        status="healthy",
        performance_overhead=0.5,  # <1%
        health_checks={},
        endpoints={},
        deployment_time=datetime.now()
    )
    
    # Add valid baseline (95% confidence, good sample size)
    results.baseline = PerformanceBaseline(
        baseline_id="baseline-123",
        application_name="test-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=10.0,
        response_time_mean=50.0,
        response_time_median=48.0,
        response_time_p95=80.0,
        response_time_p99=95.0,
        response_time_max=100.0,
        requests_per_second=16.67,
        error_rate=0.02,
        errors_by_type={},
        statistical_confidence=0.95,  # 95%
        sample_size=1000,  # >100
        data_quality_score=0.85  # >0.7
    )
    
    is_valid = await orchestrator._validate_results(results)
    
    assert is_valid is True
    assert len(results.validation_errors) == 0


@pytest.mark.asyncio
async def test_results_validation_failure_overhead(orchestrator):
    """Test results validation with excessive overhead."""
    from src.omega_analysis.analysis.runtime.signoz_deployer import DeploymentStatus
    
    results = RuntimeAnalysisResults(
        analysis_id="test-invalid",
        application_name="test-app",
        output_directory=Path("/tmp/test"),
    )
    
    # Add invalid deployment (>1% overhead)
    results.signoz_deployment = DeploymentStatus(
        deployment_id="deploy-123",
        status="healthy",
        performance_overhead=1.5,  # >1% - VIOLATES FR-002
        health_checks={},
        endpoints={},
        deployment_time=datetime.now()
    )
    
    # Add valid baseline
    results.baseline = PerformanceBaseline(
        baseline_id="baseline-123",
        application_name="test-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=1000,
        response_time_min=10.0,
        response_time_mean=50.0,
        response_time_median=48.0,
        response_time_p95=80.0,
        response_time_p99=95.0,
        response_time_max=100.0,
        requests_per_second=16.67,
        error_rate=0.02,
        errors_by_type={},
        statistical_confidence=0.95,
        sample_size=1000,
        data_quality_score=0.85
    )
    
    is_valid = await orchestrator._validate_results(results)
    
    assert is_valid is False
    assert any("FR-002" in err for err in results.validation_errors)


@pytest.mark.asyncio
async def test_results_validation_failure_confidence(orchestrator):
    """Test results validation with low statistical confidence."""
    from src.omega_analysis.analysis.runtime.signoz_deployer import DeploymentStatus
    
    results = RuntimeAnalysisResults(
        analysis_id="test-invalid",
        application_name="test-app",
        output_directory=Path("/tmp/test"),
    )
    
    # Add valid deployment
    results.signoz_deployment = DeploymentStatus(
        deployment_id="deploy-123",
        status="healthy",
        performance_overhead=0.5,
        health_checks={},
        endpoints={},
        deployment_time=datetime.now()
    )
    
    # Add invalid baseline (low confidence)
    results.baseline = PerformanceBaseline(
        baseline_id="baseline-123",
        application_name="test-app",
        collection_period_start=datetime.now(),
        collection_period_end=datetime.now(),
        environment_type="synthetic",
        load_pattern="constant",
        concurrent_users=50,
        total_requests=50,
        response_time_min=10.0,
        response_time_mean=50.0,
        response_time_median=48.0,
        response_time_p95=80.0,
        response_time_p99=95.0,
        response_time_max=100.0,
        requests_per_second=0.83,
        error_rate=0.02,
        errors_by_type={},
        statistical_confidence=0.85,  # <95% - VIOLATES FR-004
        sample_size=50,  # <100 - Too small
        data_quality_score=0.60  # <0.7 - Low quality
    )
    
    is_valid = await orchestrator._validate_results(results)
    
    assert is_valid is False
    assert any("FR-004" in err for err in results.validation_errors)
    assert any("sample size" in err.lower() for err in results.validation_errors)
    assert any("quality" in err.lower() for err in results.validation_errors)


@pytest.mark.asyncio
async def test_default_config_generation(orchestrator):
    """Test default configuration generation."""
    config = orchestrator._get_default_config()
    
    assert "signoz" in config
    assert "instrumentation" in config
    assert "load_testing" in config
    assert "baseline" in config
    
    # Check SigNoz config
    assert config["signoz"]["environment"] == "docker-compose"
    
    # Check instrumentation config
    assert config["instrumentation"]["mode"] == "hybrid"
    assert config["instrumentation"]["sampling_rate"] == 0.01
    
    # Check load testing config
    assert config["load_testing"]["sequential"] is True
    assert len(config["load_testing"]["scenarios"]) == 2
    
    # Check baseline config
    assert config["baseline"]["primary_scenario"] == "baseline-stepped"


@pytest.mark.asyncio
async def test_full_orchestration_workflow(orchestrator):
    """Test complete runtime analysis workflow."""
    # Use httpbin.org for reliable testing
    base_url = "https://httpbin.org"
    
    # Custom config with short durations for testing
    config = orchestrator._get_default_config()
    config["load_testing"]["scenarios"] = [
        {
            "name": "quick-baseline",
            "pattern": "constant",
            "duration": 0.1,  # 6 seconds
            "users": 2,
            "endpoints": [
                {"path": "/status/200", "method": "GET", "weight": 1}
            ]
        }
    ]
    config["baseline"]["primary_scenario"] = "quick-baseline"
    
    results = await orchestrator.orchestrate_full_runtime_analysis(
        application_name="httpbin-test",
        base_url=base_url,
        config=config
    )
    
    # Verify results structure
    assert results.analysis_id is not None
    assert results.application_name == "httpbin-test"
    assert results.output_directory.exists()
    
    # Verify deployment
    assert results.signoz_deployment is not None
    assert results.signoz_deployment.status in ["healthy", "mock"]
    
    # Verify instrumentation
    assert results.instrumentation_artifacts is not None
    assert len(results.instrumentation_artifacts.files) == 9
    
    # Verify load testing
    assert "quick-baseline" in results.load_test_results
    assert results.load_test_results["quick-baseline"].total_requests > 0
    
    # Verify baseline
    assert results.baseline is not None
    assert results.baseline.sample_size > 0
    
    # Verify summary metrics
    assert "load_test_scenarios" in results.summary_metrics
    assert "baseline_collected" in results.summary_metrics
    
    # Verify results file exported
    results_file = results.output_directory / "runtime_analysis_results.json"
    assert results_file.exists()
    
    # Verify analysis stored
    assert results.analysis_id in orchestrator.completed_analyses


@pytest.mark.asyncio
async def test_orchestrator_error_handling(orchestrator):
    """Test orchestrator error handling with invalid inputs."""
    # Invalid base URL should cause load testing to fail
    # The orchestrator handles the exception and still completes with validation errors
    results = await orchestrator.orchestrate_full_runtime_analysis(
        application_name="test-app",
        base_url="http://invalid-url-that-does-not-exist-12345.com",
        config={
            "load_testing": {
                "scenarios": [
                    {
                        "name": "fail-test",
                        "pattern": "constant",
                        "duration": 0.05,
                        "users": 1,
                    }
                ]
            }
        }
    )
    
    # Should complete but have validation errors due to failed tests
    assert results is not None
    assert results.meets_requirements is False
    assert len(results.validation_errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
