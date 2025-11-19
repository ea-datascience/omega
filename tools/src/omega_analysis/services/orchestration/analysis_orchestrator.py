"""
Analysis Orchestrator Service.

Coordinates the complete analysis workflow including static analysis, runtime analysis,
gap analysis, architecture discovery, dependency mapping, and performance baselining.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from omega_analysis.services.orchestration.progress_tracker import (
    ProgressTracker,
    AnalysisPhase
)
from omega_analysis.services.orchestration.result_aggregator import (
    ResultAggregator
)


logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    Main orchestrator for coordinating analysis workflows.
    
    Responsibilities:
    - Coordinate static and runtime analysis
    - Manage analysis lifecycle (start, stop, cancel)
    - Track analysis progress
    - Aggregate analysis results
    - Provide status updates
    """
    
    def __init__(self):
        """Initialize the analysis orchestrator."""
        self.active_analyses: Dict[UUID, Dict[str, Any]] = {}
        self.progress_trackers: Dict[UUID, ProgressTracker] = {}
        self.result_aggregators: Dict[UUID, ResultAggregator] = {}
        logger.info("Analysis Orchestrator initialized")
    
    async def start_analysis(
        self,
        project_id: UUID,
        analysis_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start comprehensive analysis for a project.
        
        Args:
            project_id: UUID of the project to analyze
            analysis_config: Optional configuration for analysis execution
        
        Returns:
            Dict containing analysis ID and initial status
        """
        analysis_id = uuid4()
        
        logger.info(f"Starting analysis {analysis_id} for project {project_id}")
        
        # Initialize progress tracker
        tracker = ProgressTracker(analysis_id, project_id)
        self.progress_trackers[analysis_id] = tracker
        
        # Initialize result aggregator
        aggregator = ResultAggregator(analysis_id, project_id)
        self.result_aggregators[analysis_id] = aggregator
        
        # Initialize analysis tracking
        self.active_analyses[analysis_id] = {
            "analysis_id": analysis_id,
            "project_id": project_id,
            "status": "running",
            "config": analysis_config or {},
        }
        
        # Start initialization phase
        tracker.start_phase(AnalysisPhase.INITIALIZING)
        tracker.complete_phase(AnalysisPhase.INITIALIZING)
        
        # Start static analysis phase
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        # TODO: Trigger actual analysis workflow
        # This will be implemented in subsequent phases:
        # 1. Static analysis (JavaParser, AppCAT, CodeQL, SonarQube)
        # 2. Runtime analysis (OpenTelemetry, SigNoz, load testing)
        # 3. Gap analysis (coupling metrics, drift detection)
        # 4. Result aggregation
        
        return {
            "analysis_id": str(analysis_id),
            "project_id": str(project_id),
            "status": "running",
            "message": "Analysis started successfully"
        }
    
    async def get_analysis_status(self, analysis_id: UUID) -> Dict[str, Any]:
        """
        Get current status of an analysis.
        
        Args:
            analysis_id: UUID of the analysis
        
        Returns:
            Dict containing current analysis status and progress
        
        Raises:
            ValueError: If analysis ID not found
        """
        if analysis_id not in self.progress_trackers:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        tracker = self.progress_trackers[analysis_id]
        return tracker.get_status()
    
    async def cancel_analysis(self, analysis_id: UUID, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a running analysis.
        
        Args:
            analysis_id: UUID of the analysis to cancel
            reason: Optional reason for cancellation
        
        Returns:
            Dict containing cancellation confirmation
        
        Raises:
            ValueError: If analysis ID not found or already completed
        """
        if analysis_id not in self.progress_trackers:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        tracker = self.progress_trackers[analysis_id]
        
        if tracker.current_phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            raise ValueError(f"Cannot cancel analysis in phase: {tracker.current_phase.value}")
        
        logger.info(f"Cancelling analysis {analysis_id}. Reason: {reason}")
        
        tracker.mark_cancelled(reason)
        
        return {
            "analysis_id": str(analysis_id),
            "status": "cancelled",
            "message": "Analysis cancelled successfully"
        }
    
    async def get_analysis_results(self, project_id: UUID) -> Dict[str, Any]:
        """
        Get aggregated results for a project's most recent analysis.
        
        Args:
            project_id: UUID of the project
        
        Returns:
            Dict containing complete analysis results
        
        Raises:
            ValueError: If no completed analysis found for project
        """
        # Find most recent completed analysis for this project
        completed_analyses = [
            a for a in self.active_analyses.values()
            if a["project_id"] == project_id and a["status"] == "completed"
        ]
        
        if not completed_analyses:
            raise ValueError(f"No completed analysis found for project {project_id}")
        
        # Get most recent
        latest = max(completed_analyses, key=lambda x: x["started_at"])
        
        return {
            "project_id": str(project_id),
            "analysis_id": str(latest["analysis_id"]),
            "completed_at": latest.get("completed_at", datetime.utcnow()).isoformat(),
            "static_analysis": latest.get("static_results", {}),
            "runtime_analysis": latest.get("runtime_results", {}),
            "gap_analysis": latest.get("gap_results", {}),
            "recommendations": latest.get("recommendations", [])
        }
    
    async def get_aggregated_results(self, analysis_id: UUID) -> Dict[str, Any]:
        """
        Get fully aggregated results for an analysis using ResultAggregator.
        
        Args:
            analysis_id: UUID of the analysis
        
        Returns:
            Dict containing comprehensive aggregated report
        
        Raises:
            ValueError: If analysis ID not found
        """
        if analysis_id not in self.result_aggregators:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        aggregator = self.result_aggregators[analysis_id]
        return aggregator.aggregate_results()
    
    async def add_analysis_result(
        self,
        analysis_id: UUID,
        result_type: str,
        result_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a result to an analysis's aggregator.
        
        Args:
            analysis_id: UUID of the analysis
            result_type: Type of result (static_analysis, runtime_analysis, etc.)
            result_data: The actual result data
            source: Source of the result
            metadata: Optional metadata
        
        Raises:
            ValueError: If analysis ID not found
        """
        if analysis_id not in self.result_aggregators:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        aggregator = self.result_aggregators[analysis_id]
        
        # Map result type string to aggregator method
        if result_type == "static_analysis":
            aggregator.add_static_analysis_result(result_data, source, metadata)
        elif result_type == "runtime_analysis":
            aggregator.add_runtime_analysis_result(result_data, source, metadata)
        elif result_type == "gap_analysis":
            aggregator.add_gap_analysis_result(result_data, metadata)
        elif result_type == "architecture":
            aggregator.add_architecture_result(result_data, source, metadata)
        elif result_type == "dependencies":
            aggregator.add_dependency_result(result_data, source, metadata)
        elif result_type == "performance":
            aggregator.add_performance_result(result_data, source, metadata)
        else:
            logger.warning(f"Unknown result type: {result_type}")
    
    async def get_system_architecture(self, project_id: UUID):
        """
        Get architecture analysis results for a project.
        
        Args:
            project_id: UUID of the project
        
        Returns:
            SystemArchitecture model instance
        """
        from omega_analysis.api.analysis.architecture import SystemArchitecture
        
        logger.info(f"Retrieving architecture for project {project_id}")
        
        # TODO: Integrate with actual architecture service
        # For now, return mock data structure
        return SystemArchitecture(
            id=uuid4(),
            analysis_project_id=project_id,
            architecture_style="modular_monolith",
            domain_model={
                "bounded_contexts": [],
                "aggregates": [],
                "entities": []
            },
            c4_model={
                "system_context": {},
                "containers": [],
                "components": []
            },
            technology_stack={
                "languages": ["Java"],
                "frameworks": ["Spring Boot"],
                "databases": ["PostgreSQL"]
            },
            architectural_patterns={
                "layered_architecture": True,
                "event_driven": False,
                "microservices": False
            },
            quality_metrics={
                "modularity_score": 0.75,
                "coupling_score": 0.65
            },
            documentation_coverage=0.60,
            test_coverage=0.70,
            generated_diagrams={},
            discovered_at=datetime.utcnow().isoformat(),
            tool_versions={
                "javaparser": "3.25.0",
                "appcat": "latest"
            }
        )
    
    async def get_service_boundaries(self, project_id: UUID):
        """
        Get recommended service boundaries for microservices decomposition.
        
        Args:
            project_id: UUID of the project
        
        Returns:
            List of ServiceBoundary model instances
        """
        from omega_analysis.api.analysis.architecture import ServiceBoundary
        
        logger.info(f"Retrieving service boundaries for project {project_id}")
        
        # TODO: Integrate with actual boundary detection
        return [
            ServiceBoundary(
                id=uuid4(),
                name="Order Management",
                description="Handles order processing and fulfillment",
                components=["OrderService", "OrderRepository", "OrderController"],
                dependencies=["PaymentService", "InventoryService"],
                data_ownership=["orders", "order_items"],
                api_contracts=[],
                cohesion_score=0.85,
                coupling_score=0.30,
                business_capability="Order Processing",
                team_alignment="Order Team"
            ),
            ServiceBoundary(
                id=uuid4(),
                name="Payment Processing",
                description="Manages payment transactions",
                components=["PaymentService", "PaymentRepository", "PaymentController"],
                dependencies=[],
                data_ownership=["payments", "transactions"],
                api_contracts=[],
                cohesion_score=0.90,
                coupling_score=0.20,
                business_capability="Payment Processing",
                team_alignment="Payment Team"
            )
        ]
    
    async def get_component_details(
        self,
        project_id: UUID,
        boundary_id: Optional[UUID] = None
    ):
        """
        Get detailed component information, optionally filtered by boundary.
        
        Args:
            project_id: UUID of the project
            boundary_id: Optional UUID to filter components by boundary
        
        Returns:
            List of ComponentDetail model instances
        """
        from omega_analysis.api.analysis.architecture import ComponentDetail
        
        logger.info(f"Retrieving components for project {project_id}, boundary {boundary_id}")
        
        # TODO: Integrate with actual component analysis
        components = [
            ComponentDetail(
                id=uuid4(),
                name="OrderService",
                type="service",
                package="com.example.orders",
                responsibilities=["Create orders", "Update order status"],
                dependencies=["PaymentService", "InventoryService"],
                lines_of_code=450,
                complexity_score=0.65,
                test_coverage=0.80,
                documentation_status="adequate"
            ),
            ComponentDetail(
                id=uuid4(),
                name="PaymentService",
                type="service",
                package="com.example.payments",
                responsibilities=["Process payments", "Handle refunds"],
                dependencies=[],
                lines_of_code=320,
                complexity_score=0.55,
                test_coverage=0.85,
                documentation_status="comprehensive"
            )
        ]
        
        # Filter by boundary if specified
        if boundary_id:
            # In a real implementation, this would filter based on actual boundary membership
            logger.debug(f"Filtering components by boundary {boundary_id}")
        
        return components
    
    async def get_dependency_graph(
        self,
        project_id: UUID,
        graph_type: str = "combined"
    ):
        """
        Get dependency graph for a project.
        
        Args:
            project_id: UUID of the project
            graph_type: Type of graph (static, runtime, or combined)
        
        Returns:
            DependencyGraph model instance
        """
        from omega_analysis.api.analysis.dependencies import DependencyGraph
        
        logger.info(f"Retrieving {graph_type} dependency graph for project {project_id}")
        
        # TODO: Integrate with actual dependency analysis
        return DependencyGraph(
            id=uuid4(),
            analysis_project_id=project_id,
            graph_type=graph_type,
            nodes={
                "modules": [
                    {"id": "order-service", "type": "module", "size": 5400},
                    {"id": "payment-service", "type": "module", "size": 3200}
                ]
            },
            edges={
                "dependencies": [
                    {
                        "source": "order-service",
                        "target": "payment-service",
                        "type": graph_type,
                        "weight": 12
                    }
                ]
            },
            coupling_metrics={
                "afferent_coupling": {"order-service": 3, "payment-service": 8},
                "efferent_coupling": {"order-service": 8, "payment-service": 2},
                "instability": {"order-service": 0.73, "payment-service": 0.2}
            },
            external_dependencies={
                "libraries": ["spring-boot", "hibernate", "jackson"],
                "services": []
            },
            data_dependencies={
                "database_schemas": ["orders", "payments"],
                "shared_tables": []
            },
            circular_dependencies={
                "cycles": []
            },
            critical_path_analysis={
                "longest_paths": [
                    {"path": ["ui", "order-service", "payment-service", "database"], "length": 4}
                ]
            },
            confidence_score=0.85,
            generated_at=datetime.utcnow().isoformat(),
            validation_status="validated"
        )
    
    async def get_performance_baselines(
        self,
        project_id: UUID,
        environment_type: Optional[str] = None
    ):
        """
        Get performance baselines for a project.
        
        Args:
            project_id: UUID of the project
            environment_type: Optional filter by environment type
        
        Returns:
            List of PerformanceBaseline model instances
        """
        from omega_analysis.api.analysis.baselines import PerformanceBaseline
        
        logger.info(f"Retrieving performance baselines for project {project_id}, environment {environment_type}")
        
        # TODO: Integrate with actual performance monitoring
        baselines = [
            PerformanceBaseline(
                id=uuid4(),
                analysis_project_id=project_id,
                collection_period_start=datetime.utcnow().isoformat(),
                collection_period_end=datetime.utcnow().isoformat(),
                environment_type="production",
                load_characteristics={
                    "avg_rps": 150,
                    "peak_rps": 350,
                    "user_sessions": 500
                },
                response_time_metrics={
                    "p50": 45.2,
                    "p95": 120.5,
                    "p99": 250.8
                },
                throughput_metrics={
                    "requests_per_second": 150,
                    "transactions_per_minute": 8500
                },
                error_rate_metrics={
                    "total_errors": 25,
                    "error_rate": 0.002
                },
                resource_utilization={
                    "cpu_percent": 65.0,
                    "memory_percent": 70.0,
                    "disk_io": 45.0
                },
                database_performance={
                    "avg_query_time_ms": 15.5,
                    "slow_queries": 3
                },
                statistical_confidence=0.95,
                sample_size=100000
            )
        ]
        
        # Filter by environment if specified
        if environment_type:
            baselines = [b for b in baselines if b.environment_type == environment_type]
        
        return baselines


# Global orchestrator instance
_orchestrator_instance: Optional[AnalysisOrchestrator] = None


def get_orchestrator_instance() -> AnalysisOrchestrator:
    """
    Get or create the global orchestrator instance.
    
    Returns:
        AnalysisOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AnalysisOrchestrator()
    return _orchestrator_instance
