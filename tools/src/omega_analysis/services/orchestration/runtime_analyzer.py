"""Runtime analysis orchestration service using Microsoft Agent Framework.

This module coordinates SigNoz deployment, OpenTelemetry instrumentation, and synthetic
load testing to establish performance baselines and runtime behavior analysis.

Per FR-002: Deploy runtime observability with <1% overhead, fallback to synthetic load.
Per FR-004: Collect performance baselines with 95% confidence intervals.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import json
import tempfile

from ...analysis.runtime.signoz_deployer import (
    SigNozDeployer, SigNozConfig, DeploymentStatus
)
from ...analysis.runtime.otel_instrumentation import (
    OTelInstrumentationGenerator, InstrumentationConfig, InstrumentationArtifacts
)
from ...analysis.runtime.load_generator import (
    LoadTestOrchestrator, LoadScenario, LoadPattern, Endpoint, LoadTestResults
)

logger = logging.getLogger(__name__)


@dataclass
class RuntimeAnalysisTask:
    """Represents a runtime analysis task."""
    task_id: str
    task_type: str  # 'deploy', 'instrument', 'load_test', 'collect_baseline'
    application_name: str
    base_url: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Any] = None


@dataclass
class PerformanceBaseline:
    """Performance baseline collected from runtime analysis."""
    baseline_id: str
    application_name: str
    collection_period_start: datetime
    collection_period_end: datetime
    environment_type: str  # 'production', 'staging', 'development', 'synthetic'
    
    # Load characteristics
    load_pattern: str
    concurrent_users: int
    total_requests: int
    
    # Response time metrics (milliseconds)
    response_time_min: float
    response_time_mean: float
    response_time_median: float
    response_time_p95: float
    response_time_p99: float
    response_time_max: float
    
    # Throughput metrics
    requests_per_second: float
    
    # Error metrics
    error_rate: float
    errors_by_type: Dict[str, int]
    
    # Statistical confidence
    statistical_confidence: float = 0.95
    sample_size: int = 0
    
    # Data quality
    data_quality_score: float = 1.0


@dataclass
class RuntimeAnalysisResults:
    """Comprehensive runtime analysis results."""
    analysis_id: str
    application_name: str
    output_directory: Path
    
    # Deployment results
    signoz_deployment: Optional[DeploymentStatus] = None
    instrumentation_artifacts: Optional[InstrumentationArtifacts] = None
    
    # Load testing results
    load_test_results: Dict[str, LoadTestResults] = field(default_factory=dict)
    
    # Performance baseline
    baseline: Optional[PerformanceBaseline] = None
    
    # Orchestration metadata
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    summary_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Validation status
    meets_requirements: bool = False
    validation_errors: List[str] = field(default_factory=list)


class RuntimeAnalysisOrchestrator:
    """Orchestrates runtime analysis using Microsoft Agent Framework patterns."""
    
    def __init__(self, base_output_dir: Optional[Path] = None):
        """Initialize runtime analysis orchestrator.
        
        Args:
            base_output_dir: Base directory for analysis outputs
        """
        self.base_output_dir = base_output_dir or Path(tempfile.gettempdir()) / "omega_runtime_analysis"
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.signoz_deployer = SigNozDeployer()
        self.load_orchestrator = LoadTestOrchestrator()
        
        # Task tracking
        self.active_tasks: Dict[str, RuntimeAnalysisTask] = {}
        self.completed_analyses: Dict[str, RuntimeAnalysisResults] = {}
        
        logger.info(f"Runtime analysis orchestrator initialized: {self.base_output_dir}")
        
    async def orchestrate_full_runtime_analysis(
        self,
        application_name: str,
        base_url: str,
        analysis_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> RuntimeAnalysisResults:
        """Orchestrate complete runtime analysis workflow.
        
        This coordinates:
        1. SigNoz deployment (or mock)
        2. OTel instrumentation generation
        3. Synthetic load testing
        4. Performance baseline collection
        5. Results validation
        
        Args:
            application_name: Name of application to analyze
            base_url: Base URL of running application
            analysis_id: Optional analysis identifier
            config: Optional configuration overrides
            
        Returns:
            RuntimeAnalysisResults with complete analysis
        """
        logger.info(f"Starting full runtime analysis for: {application_name}")
        
        if analysis_id is None:
            analysis_id = f"runtime_{application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        if config is None:
            config = self._get_default_config()
            
        # Create output directory
        output_dir = self.base_output_dir / analysis_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results
        results = RuntimeAnalysisResults(
            analysis_id=analysis_id,
            application_name=application_name,
            output_directory=output_dir,
            execution_metadata={
                "start_time": datetime.now().isoformat(),
                "config": config,
                "orchestrator_version": "1.0.0"
            }
        )
        
        try:
            # Phase 1: Deploy SigNoz observability stack
            logger.info("Phase 1: Deploying SigNoz observability stack...")
            signoz_task = await self._create_task(
                task_type="deploy",
                application_name=application_name,
                config=config.get("signoz", {})
            )
            results.signoz_deployment = await self._execute_signoz_deployment(signoz_task)
            
            # Phase 2: Generate OTel instrumentation
            logger.info("Phase 2: Generating OpenTelemetry instrumentation...")
            instrument_task = await self._create_task(
                task_type="instrument",
                application_name=application_name,
                config=config.get("instrumentation", {})
            )
            results.instrumentation_artifacts = await self._execute_instrumentation_generation(
                instrument_task, output_dir
            )
            
            # Phase 3: Execute synthetic load testing
            logger.info("Phase 3: Executing synthetic load tests...")
            load_test_task = await self._create_task(
                task_type="load_test",
                application_name=application_name,
                base_url=base_url,
                config=config.get("load_testing", {})
            )
            results.load_test_results = await self._execute_load_testing(
                load_test_task, base_url
            )
            
            # Phase 4: Collect performance baseline
            logger.info("Phase 4: Collecting performance baseline...")
            baseline_task = await self._create_task(
                task_type="collect_baseline",
                application_name=application_name,
                config=config.get("baseline", {})
            )
            results.baseline = await self._collect_performance_baseline(
                baseline_task, results.load_test_results
            )
            
            # Phase 5: Generate summary metrics
            logger.info("Phase 5: Generating summary metrics...")
            results.summary_metrics = self._generate_summary_metrics(results)
            
            # Phase 6: Validate results
            logger.info("Phase 6: Validating analysis results...")
            results.meets_requirements = await self._validate_results(results)
            
            # Export results
            await self._export_results(results)
            
            # Store completed analysis
            self.completed_analyses[analysis_id] = results
            
            logger.info(f"Runtime analysis completed: {analysis_id}")
            logger.info(f"Meets requirements: {results.meets_requirements}")
            
            return results
            
        except Exception as e:
            logger.error(f"Runtime analysis failed: {e}", exc_info=True)
            results.execution_metadata["error"] = str(e)
            results.execution_metadata["end_time"] = datetime.now().isoformat()
            raise
            
    async def _create_task(
        self,
        task_type: str,
        application_name: str,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> RuntimeAnalysisTask:
        """Create runtime analysis task.
        
        Args:
            task_type: Type of task to create
            application_name: Application name
            base_url: Optional base URL
            config: Optional configuration
            
        Returns:
            RuntimeAnalysisTask ready for execution
        """
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = RuntimeAnalysisTask(
            task_id=task_id,
            task_type=task_type,
            application_name=application_name,
            base_url=base_url,
            config=config or {}
        )
        
        self.active_tasks[task_id] = task
        logger.info(f"Created task: {task_id} ({task_type})")
        
        return task
        
    async def _execute_signoz_deployment(
        self,
        task: RuntimeAnalysisTask
    ) -> DeploymentStatus:
        """Execute SigNoz deployment task.
        
        Args:
            task: Deployment task
            
        Returns:
            DeploymentStatus from SigNoz deployer
        """
        task.status = "running"
        task.start_time = datetime.now()
        
        try:
            # Deploy SigNoz stack (will use mock if services unavailable)
            deployment_status = await self.signoz_deployer.deploy_stack(
                target_environment=task.config.get("environment", "docker-compose")
            )
            
            # Validate deployment
            is_valid = await self.signoz_deployer.validate_deployment(deployment_status)
            
            if not is_valid:
                logger.warning("SigNoz deployment validation failed, continuing with mock mode")
                
            task.status = "completed"
            task.end_time = datetime.now()
            task.result = deployment_status
            
            logger.info(f"SigNoz deployment completed: {deployment_status.deployment_id}")
            logger.info(f"  Status: {deployment_status.status}")
            logger.info(f"  Performance overhead: {deployment_status.performance_overhead}%")
            
            return deployment_status
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"SigNoz deployment failed: {e}")
            raise
            
    async def _execute_instrumentation_generation(
        self,
        task: RuntimeAnalysisTask,
        output_dir: Path
    ) -> InstrumentationArtifacts:
        """Execute OTel instrumentation generation task.
        
        Args:
            task: Instrumentation task
            output_dir: Output directory for artifacts
            
        Returns:
            InstrumentationArtifacts with generated files
        """
        task.status = "running"
        task.start_time = datetime.now()
        
        try:
            # Create instrumentation configuration
            instrumentation_config = InstrumentationConfig(
                application_name=task.application_name,
                service_namespace=task.config.get("namespace", "omega-migration"),
                otel_endpoint=task.config.get("otel_endpoint", "http://signoz-otel-collector:4318"),
                sampling_rate=task.config.get("sampling_rate", 0.01),
                instrumentation_mode=task.config.get("mode", "hybrid")
            )
            
            # Generate instrumentation artifacts
            generator = OTelInstrumentationGenerator(instrumentation_config)
            artifacts_dir = output_dir / "instrumentation"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            artifacts = generator.generate_all_artifacts(artifacts_dir)
            
            task.status = "completed"
            task.end_time = datetime.now()
            task.result = artifacts
            
            logger.info(f"Instrumentation generation completed: {artifacts.config_id}")
            logger.info(f"  Mode: {artifacts.mode}")
            logger.info(f"  Files generated: {len(artifacts.files)}")
            
            return artifacts
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"Instrumentation generation failed: {e}")
            raise
            
    async def _execute_load_testing(
        self,
        task: RuntimeAnalysisTask,
        base_url: str
    ) -> Dict[str, LoadTestResults]:
        """Execute synthetic load testing task.
        
        Args:
            task: Load testing task
            base_url: Base URL of application
            
        Returns:
            Dictionary mapping scenario names to results
        """
        task.status = "running"
        task.start_time = datetime.now()
        
        try:
            # Generate load test scenarios
            scenarios = self._generate_load_scenarios(task.application_name, base_url, task.config)
            
            # Add scenarios to orchestrator
            for scenario in scenarios:
                self.load_orchestrator.add_scenario(scenario)
                
            # Execute all scenarios
            logger.info(f"Executing {len(scenarios)} load test scenarios...")
            results = await self.load_orchestrator.run_all_scenarios(
                sequential=task.config.get("sequential", True)
            )
            
            task.status = "completed"
            task.end_time = datetime.now()
            task.result = results
            
            logger.info(f"Load testing completed: {len(results)} scenarios")
            for name, result in results.items():
                logger.info(f"  {name}: {result.total_requests} requests, "
                          f"{result.mean_response_time:.2f}ms mean, "
                          f"{(1 - result.error_rate) * 100:.1f}% success rate")
                          
            return results
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"Load testing failed: {e}")
            raise
            
    async def _collect_performance_baseline(
        self,
        task: RuntimeAnalysisTask,
        load_test_results: Dict[str, LoadTestResults]
    ) -> PerformanceBaseline:
        """Collect performance baseline from load test results.
        
        Args:
            task: Baseline collection task
            load_test_results: Results from load testing
            
        Returns:
            PerformanceBaseline with aggregated metrics
        """
        task.status = "running"
        task.start_time = datetime.now()
        
        try:
            # Select primary scenario for baseline (typically constant or stepped load)
            primary_scenario = task.config.get("primary_scenario", "baseline")
            
            if primary_scenario in load_test_results:
                primary_result = load_test_results[primary_scenario]
            elif load_test_results:
                # Use first available result
                primary_result = next(iter(load_test_results.values()))
            else:
                raise ValueError("No load test results available for baseline")
                
            # Create baseline from primary result
            baseline = PerformanceBaseline(
                baseline_id=f"baseline_{task.application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                application_name=task.application_name,
                collection_period_start=primary_result.start_time,
                collection_period_end=primary_result.end_time,
                environment_type=task.config.get("environment_type", "synthetic"),
                load_pattern=primary_result.scenario_name,
                concurrent_users=task.config.get("concurrent_users", 50),
                total_requests=primary_result.total_requests,
                response_time_min=primary_result.min_response_time,
                response_time_mean=primary_result.mean_response_time,
                response_time_median=primary_result.median_response_time,
                response_time_p95=primary_result.p95_response_time,
                response_time_p99=primary_result.p99_response_time,
                response_time_max=primary_result.max_response_time,
                requests_per_second=primary_result.requests_per_second,
                error_rate=primary_result.error_rate,
                errors_by_type=primary_result.errors_by_type,
                statistical_confidence=primary_result.statistical_confidence,
                sample_size=primary_result.sample_size,
                data_quality_score=self._calculate_data_quality_score(primary_result)
            )
            
            task.status = "completed"
            task.end_time = datetime.now()
            task.result = baseline
            
            logger.info(f"Performance baseline collected: {baseline.baseline_id}")
            logger.info(f"  Sample size: {baseline.sample_size}")
            logger.info(f"  Mean response time: {baseline.response_time_mean:.2f}ms")
            logger.info(f"  P95 response time: {baseline.response_time_p95:.2f}ms")
            logger.info(f"  Throughput: {baseline.requests_per_second:.2f} req/s")
            logger.info(f"  Data quality: {baseline.data_quality_score:.2f}")
            
            return baseline
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"Baseline collection failed: {e}")
            raise
            
    def _generate_load_scenarios(
        self,
        application_name: str,
        base_url: str,
        config: Dict[str, Any]
    ) -> List[LoadScenario]:
        """Generate load test scenarios.
        
        Args:
            application_name: Application name
            base_url: Base URL
            config: Load testing configuration
            
        Returns:
            List of LoadScenario objects
        """
        scenarios = []
        
        # Default scenarios if not specified
        scenario_configs = config.get("scenarios", [
            {"name": "baseline", "pattern": "constant", "duration": 5, "users": 10},
            {"name": "ramp-up", "pattern": "stepped", "duration": 10, "base_users": 10, "peak_users": 50},
        ])
        
        for scenario_config in scenario_configs:
            # Create load pattern
            pattern = LoadPattern(
                pattern_type=scenario_config.get("pattern", "constant"),
                duration_minutes=scenario_config.get("duration", 5),
                base_users=scenario_config.get("base_users", scenario_config.get("users", 10)),
                peak_users=scenario_config.get("peak_users", scenario_config.get("users", 10)),
                step_duration_minutes=scenario_config.get("step_duration", 2),
                step_increment=scenario_config.get("step_increment", 10)
            )
            
            # Create endpoints (use Spring Boot defaults if not specified)
            endpoints_config = scenario_config.get("endpoints", [
                {"path": "/actuator/health", "method": "GET", "weight": 1},
                {"path": "/api/v1/data", "method": "GET", "weight": 5},
            ])
            
            endpoints = [
                Endpoint(
                    path=ep.get("path", "/"),
                    method=ep.get("method", "GET"),
                    weight=ep.get("weight", 1),
                    expected_status=ep.get("expected_status", 200)
                )
                for ep in endpoints_config
            ]
            
            # Create scenario
            scenario = LoadScenario(
                name=scenario_config.get("name", f"{application_name}-scenario"),
                base_url=base_url,
                endpoints=endpoints,
                pattern=pattern,
                think_time_ms=tuple(scenario_config.get("think_time_ms", [1000, 3000])),
                timeout_seconds=scenario_config.get("timeout", 30)
            )
            
            scenarios.append(scenario)
            
        return scenarios
        
    def _calculate_data_quality_score(self, results: LoadTestResults) -> float:
        """Calculate data quality score for baseline.
        
        Args:
            results: Load test results
            
        Returns:
            Quality score 0.0-1.0
        """
        # Factors affecting quality:
        # 1. Sample size (more is better)
        # 2. Error rate (lower is better)
        # 3. Statistical confidence
        
        sample_score = min(results.sample_size / 1000, 1.0)  # 1000+ samples = 1.0
        error_score = 1.0 - results.error_rate
        confidence_score = results.statistical_confidence
        
        # Weighted average
        quality_score = (
            sample_score * 0.3 +
            error_score * 0.4 +
            confidence_score * 0.3
        )
        
        return round(quality_score, 3)
        
    def _generate_summary_metrics(self, results: RuntimeAnalysisResults) -> Dict[str, Any]:
        """Generate summary metrics from analysis results.
        
        Args:
            results: Runtime analysis results
            
        Returns:
            Dictionary of summary metrics
        """
        summary = {
            "analysis_id": results.analysis_id,
            "application_name": results.application_name,
            "execution_time_seconds": 0,
        }
        
        # Deployment metrics
        if results.signoz_deployment:
            summary["signoz_status"] = results.signoz_deployment.status
            summary["performance_overhead"] = results.signoz_deployment.performance_overhead
            summary["instrumentation_enabled"] = results.signoz_deployment.status == "healthy"
            
        # Instrumentation metrics
        if results.instrumentation_artifacts:
            summary["instrumentation_mode"] = results.instrumentation_artifacts.mode
            summary["artifacts_generated"] = len(results.instrumentation_artifacts.files)
            
        # Load testing metrics
        if results.load_test_results:
            summary["load_test_scenarios"] = len(results.load_test_results)
            summary["total_requests"] = sum(r.total_requests for r in results.load_test_results.values())
            summary["avg_success_rate"] = sum(
                (r.successful_requests / r.total_requests) for r in results.load_test_results.values()
            ) / len(results.load_test_results) if results.load_test_results else 0
            
        # Baseline metrics
        if results.baseline:
            summary["baseline_collected"] = True
            summary["baseline_sample_size"] = results.baseline.sample_size
            summary["baseline_p95_ms"] = results.baseline.response_time_p95
            summary["baseline_throughput"] = results.baseline.requests_per_second
            summary["data_quality_score"] = results.baseline.data_quality_score
        else:
            summary["baseline_collected"] = False
            
        return summary
        
    async def _validate_results(self, results: RuntimeAnalysisResults) -> bool:
        """Validate analysis results against requirements.
        
        Validates:
        - FR-002: <1% performance overhead
        - FR-004: 95% confidence intervals
        
        Args:
            results: Runtime analysis results
            
        Returns:
            True if all requirements met
        """
        validation_errors = []
        
        # FR-002: Performance overhead <1%
        if results.signoz_deployment:
            if results.signoz_deployment.performance_overhead >= 1.0:
                validation_errors.append(
                    f"Performance overhead {results.signoz_deployment.performance_overhead}% exceeds 1% limit (FR-002)"
                )
        else:
            validation_errors.append("SigNoz deployment not executed (FR-002)")
            
        # FR-004: 95% confidence intervals
        if results.baseline:
            if results.baseline.statistical_confidence < 0.95:
                validation_errors.append(
                    f"Statistical confidence {results.baseline.statistical_confidence} below 95% requirement (FR-004)"
                )
                
            # Check minimum sample size (arbitrary threshold: 100 requests)
            if results.baseline.sample_size < 100:
                validation_errors.append(
                    f"Sample size {results.baseline.sample_size} too small for reliable statistics (FR-004)"
                )
        else:
            validation_errors.append("Performance baseline not collected (FR-004)")
            
        # Data quality check
        if results.baseline and results.baseline.data_quality_score < 0.7:
            validation_errors.append(
                f"Data quality score {results.baseline.data_quality_score} below 0.7 threshold"
            )
            
        results.validation_errors = validation_errors
        
        if validation_errors:
            logger.warning("Validation failures:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
            return False
        else:
            logger.info("All validation checks passed")
            return True
            
    async def _export_results(self, results: RuntimeAnalysisResults) -> None:
        """Export analysis results to JSON file.
        
        Args:
            results: Runtime analysis results
        """
        output_file = results.output_directory / "runtime_analysis_results.json"
        
        export_data = {
            "analysis_id": results.analysis_id,
            "application_name": results.application_name,
            "output_directory": str(results.output_directory),
            "execution_metadata": results.execution_metadata,
            "summary_metrics": results.summary_metrics,
            "meets_requirements": results.meets_requirements,
            "validation_errors": results.validation_errors,
        }
        
        # Add deployment info
        if results.signoz_deployment:
            export_data["signoz_deployment"] = {
                "deployment_id": results.signoz_deployment.deployment_id,
                "status": results.signoz_deployment.status,
                "performance_overhead": results.signoz_deployment.performance_overhead,
                "health_checks": results.signoz_deployment.health_checks,
                "endpoints": results.signoz_deployment.endpoints,
            }
            
        # Add instrumentation info
        if results.instrumentation_artifacts:
            export_data["instrumentation"] = {
                "config_id": results.instrumentation_artifacts.config_id,
                "mode": results.instrumentation_artifacts.mode,
                "files": {k: str(v) for k, v in results.instrumentation_artifacts.files.items()},
            }
            
        # Add load test results
        if results.load_test_results:
            export_data["load_tests"] = {}
            for name, result in results.load_test_results.items():
                export_data["load_tests"][name] = {
                    "scenario_name": result.scenario_name,
                    "total_requests": result.total_requests,
                    "success_rate": (result.successful_requests / result.total_requests) if result.total_requests > 0 else 0,
                    "response_time_p95": result.p95_response_time,
                    "throughput": result.requests_per_second,
                }
                
        # Add baseline
        if results.baseline:
            export_data["baseline"] = asdict(results.baseline)
            export_data["baseline"]["collection_period_start"] = results.baseline.collection_period_start.isoformat()
            export_data["baseline"]["collection_period_end"] = results.baseline.collection_period_end.isoformat()
            
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Results exported to: {output_file}")
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default runtime analysis configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "signoz": {
                "environment": "docker-compose",
            },
            "instrumentation": {
                "mode": "hybrid",
                "namespace": "omega-migration",
                "otel_endpoint": "http://signoz-otel-collector:4318",
                "sampling_rate": 0.01,
            },
            "load_testing": {
                "sequential": True,
                "scenarios": [
                    {
                        "name": "baseline-constant",
                        "pattern": "constant",
                        "duration": 5,
                        "users": 10,
                    },
                    {
                        "name": "baseline-stepped",
                        "pattern": "stepped",
                        "duration": 10,
                        "base_users": 10,
                        "peak_users": 50,
                        "step_duration": 2,
                        "step_increment": 10,
                    },
                ],
            },
            "baseline": {
                "primary_scenario": "baseline-stepped",
                "environment_type": "synthetic",
                "concurrent_users": 50,
            },
        }


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Runtime analysis orchestrator')
    parser.add_argument('--app-name', default='spring-modulith', help='Application name')
    parser.add_argument('--base-url', default='http://localhost:8080', help='Base URL')
    parser.add_argument('--output-dir', default='/tmp/runtime-analysis', help='Output directory')
    parser.add_argument('--duration', type=int, default=5, help='Load test duration (minutes)')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def main():
        orchestrator = RuntimeAnalysisOrchestrator(Path(args.output_dir))
        
        # Custom configuration
        config = orchestrator._get_default_config()
        config["load_testing"]["scenarios"][0]["duration"] = args.duration
        config["load_testing"]["scenarios"][1]["duration"] = args.duration * 2
        
        print(f"\n=== Runtime Analysis Orchestration ===")
        print(f"Application: {args.app_name}")
        print(f"Base URL: {args.base_url}")
        print(f"Output: {args.output_dir}")
        print()
        
        results = await orchestrator.orchestrate_full_runtime_analysis(
            application_name=args.app_name,
            base_url=args.base_url,
            config=config
        )
        
        print(f"\n=== Analysis Complete ===")
        print(f"Analysis ID: {results.analysis_id}")
        print(f"Meets Requirements: {results.meets_requirements}")
        print(f"\nSummary Metrics:")
        for key, value in results.summary_metrics.items():
            print(f"  {key}: {value}")
            
        if results.validation_errors:
            print(f"\nValidation Errors ({len(results.validation_errors)}):")
            for error in results.validation_errors:
                print(f"  - {error}")
                
        print(f"\nResults exported to: {results.output_directory}")
        
    asyncio.run(main())
