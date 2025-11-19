"""
Result Aggregator for Analysis Workflows.

Aggregates results from multiple analysis phases (static, runtime, gap analysis)
into a comprehensive final report with validation and quality scoring.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """Strategy for aggregating conflicting data."""
    MERGE = "merge"  # Combine all sources
    PREFER_RUNTIME = "prefer_runtime"  # Prefer runtime over static
    PREFER_STATIC = "prefer_static"  # Prefer static over runtime
    UNION = "union"  # Take union of all sources
    INTERSECTION = "intersection"  # Take intersection of all sources


class AnalysisResultType(Enum):
    """Types of analysis results."""
    STATIC_ANALYSIS = "static_analysis"
    RUNTIME_ANALYSIS = "runtime_analysis"
    GAP_ANALYSIS = "gap_analysis"
    ARCHITECTURE = "architecture"
    DEPENDENCIES = "dependencies"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    RISK_ASSESSMENT = "risk_assessment"


class ResultAggregator:
    """
    Aggregates analysis results from multiple sources.
    
    Responsibilities:
    - Merge results from static and runtime analysis
    - Resolve conflicts using configurable strategies
    - Validate result completeness and quality
    - Generate final comprehensive report
    - Track data lineage and source attribution
    """
    
    def __init__(self, analysis_id: UUID, project_id: UUID):
        """
        Initialize result aggregator for an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            project_id: UUID of the project being analyzed
        """
        self.analysis_id = analysis_id
        self.project_id = project_id
        self.created_at = datetime.utcnow()
        
        # Result storage by type
        self.results: Dict[AnalysisResultType, List[Dict[str, Any]]] = {
            result_type: [] for result_type in AnalysisResultType
        }
        
        # Metadata tracking
        self.result_metadata: Dict[AnalysisResultType, Dict[str, Any]] = {}
        
        # Validation tracking
        self.validation_errors: List[Dict[str, Any]] = []
        self.validation_warnings: List[Dict[str, Any]] = []
        
        # Aggregation configuration
        self.aggregation_strategies: Dict[str, AggregationStrategy] = {
            "dependencies": AggregationStrategy.UNION,
            "architecture": AggregationStrategy.PREFER_RUNTIME,
            "performance": AggregationStrategy.MERGE,
            "compliance": AggregationStrategy.UNION,
        }
        
        logger.info(f"Result aggregator initialized for analysis {analysis_id}")
    
    def add_result(
        self,
        result_type: AnalysisResultType,
        result_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a result from an analysis phase.
        
        Args:
            result_type: Type of analysis result
            result_data: The actual result data
            source: Source of the result (e.g., "static_analyzer", "runtime_monitor")
            metadata: Optional metadata about the result
        """
        enriched_result = {
            "data": result_data,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.results[result_type].append(enriched_result)
        logger.info(
            f"Added {result_type.value} result from {source} "
            f"for analysis {self.analysis_id}"
        )
    
    def add_static_analysis_result(
        self,
        result_data: Dict[str, Any],
        analyzer: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add static analysis result.
        
        Args:
            result_data: Static analysis findings
            analyzer: Name of the static analyzer (e.g., "javaparser", "codeql")
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.STATIC_ANALYSIS,
            result_data,
            f"static:{analyzer}",
            metadata
        )
    
    def add_runtime_analysis_result(
        self,
        result_data: Dict[str, Any],
        monitor: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add runtime analysis result.
        
        Args:
            result_data: Runtime analysis findings
            monitor: Name of the runtime monitor (e.g., "signoz", "opentelemetry")
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.RUNTIME_ANALYSIS,
            result_data,
            f"runtime:{monitor}",
            metadata
        )
    
    def add_gap_analysis_result(
        self,
        result_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add gap analysis result.
        
        Args:
            result_data: Gap analysis findings (discrepancies between static/runtime)
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.GAP_ANALYSIS,
            result_data,
            "gap_analyzer",
            metadata
        )
    
    def add_architecture_result(
        self,
        result_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add architecture discovery result.
        
        Args:
            result_data: Architecture findings (C4 diagrams, bounded contexts)
            source: Source of architecture data
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.ARCHITECTURE,
            result_data,
            source,
            metadata
        )
    
    def add_dependency_result(
        self,
        result_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add dependency graph result.
        
        Args:
            result_data: Dependency graph data
            source: Source of dependency data
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.DEPENDENCIES,
            result_data,
            source,
            metadata
        )
    
    def add_performance_result(
        self,
        result_data: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add performance baseline result.
        
        Args:
            result_data: Performance metrics and baselines
            source: Source of performance data
            metadata: Optional metadata
        """
        self.add_result(
            AnalysisResultType.PERFORMANCE,
            result_data,
            source,
            metadata
        )
    
    def merge_dependencies(
        self,
        dependencies_list: List[Dict[str, Any]],
        strategy: AggregationStrategy = AggregationStrategy.UNION
    ) -> Dict[str, Any]:
        """
        Merge dependency graphs from multiple sources.
        
        Args:
            dependencies_list: List of dependency graph results
            strategy: Merging strategy
        
        Returns:
            Merged dependency graph
        """
        if not dependencies_list:
            return {"nodes": [], "edges": [], "sources": []}
        
        if strategy == AggregationStrategy.UNION:
            # Combine all dependencies
            all_nodes: Set[str] = set()
            all_edges: Set[tuple] = set()
            sources = []
            
            for dep_result in dependencies_list:
                data = dep_result.get("data", {})
                sources.append(dep_result.get("source", "unknown"))
                
                # Extract nodes
                nodes = data.get("nodes", [])
                for node in nodes:
                    if isinstance(node, dict):
                        all_nodes.add(node.get("id", str(node)))
                    else:
                        all_nodes.add(str(node))
                
                # Extract edges
                edges = data.get("edges", [])
                for edge in edges:
                    if isinstance(edge, dict):
                        source = edge.get("source", "")
                        target = edge.get("target", "")
                        edge_type = edge.get("type", "dependency")
                        all_edges.add((source, target, edge_type))
                    elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                        all_edges.add(tuple(edge[:3]) if len(edge) >= 3 else (*edge, "dependency"))
            
            return {
                "nodes": sorted(list(all_nodes)),
                "edges": [
                    {"source": e[0], "target": e[1], "type": e[2]}
                    for e in sorted(all_edges)
                ],
                "sources": sources,
                "merged_at": datetime.utcnow().isoformat()
            }
        
        # For other strategies, take first result
        return dependencies_list[0].get("data", {})
    
    def merge_architecture(
        self,
        architecture_list: List[Dict[str, Any]],
        strategy: AggregationStrategy = AggregationStrategy.PREFER_RUNTIME
    ) -> Dict[str, Any]:
        """
        Merge architecture discoveries from multiple sources.
        
        Args:
            architecture_list: List of architecture results
            strategy: Merging strategy
        
        Returns:
            Merged architecture model
        """
        if not architecture_list:
            return {}
        
        if strategy == AggregationStrategy.PREFER_RUNTIME:
            # Prefer runtime-discovered architecture over static
            runtime_results = [
                r for r in architecture_list
                if "runtime" in r.get("source", "")
            ]
            if runtime_results:
                return runtime_results[0].get("data", {})
        
        if strategy == AggregationStrategy.PREFER_STATIC:
            # Prefer static analysis architecture
            static_results = [
                r for r in architecture_list
                if "static" in r.get("source", "")
            ]
            if static_results:
                return static_results[0].get("data", {})
        
        # Default: return first result
        return architecture_list[0].get("data", {})
    
    def merge_performance_metrics(
        self,
        performance_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge performance metrics from multiple sources.
        
        Args:
            performance_list: List of performance results
        
        Returns:
            Merged performance metrics with statistical aggregation
        """
        if not performance_list:
            return {}
        
        merged = {
            "metrics": {},
            "sources": [],
            "merged_at": datetime.utcnow().isoformat()
        }
        
        # Collect all metrics
        all_metrics: Dict[str, List[float]] = {}
        
        for perf_result in performance_list:
            data = perf_result.get("data", {})
            source = perf_result.get("source", "unknown")
            merged["sources"].append(source)
            
            metrics = data.get("metrics", {})
            for metric_name, metric_value in metrics.items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                
                # Handle different metric formats
                if isinstance(metric_value, (int, float)):
                    all_metrics[metric_name].append(float(metric_value))
                elif isinstance(metric_value, dict):
                    # Handle structured metrics (e.g., {value: 123, unit: "ms"})
                    value = metric_value.get("value")
                    if isinstance(value, (int, float)):
                        all_metrics[metric_name].append(float(value))
        
        # Calculate aggregated statistics
        for metric_name, values in all_metrics.items():
            if values:
                merged["metrics"][metric_name] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                    "values": values
                }
        
        return merged
    
    def validate_results(self) -> bool:
        """
        Validate completeness and quality of aggregated results.
        
        Returns:
            True if validation passes, False otherwise
        """
        validation_passed = True
        
        # Check for required result types
        required_types = [
            AnalysisResultType.STATIC_ANALYSIS,
            AnalysisResultType.DEPENDENCIES
        ]
        
        for result_type in required_types:
            if not self.results[result_type]:
                self.validation_errors.append({
                    "type": "missing_required_result",
                    "result_type": result_type.value,
                    "message": f"Required result type {result_type.value} is missing",
                    "timestamp": datetime.utcnow().isoformat()
                })
                validation_passed = False
        
        # Check for data quality
        for result_type, results in self.results.items():
            for result in results:
                data = result.get("data", {})
                if not data:
                    self.validation_warnings.append({
                        "type": "empty_result_data",
                        "result_type": result_type.value,
                        "source": result.get("source"),
                        "message": f"Result from {result.get('source')} has empty data",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        # Log validation results
        if validation_passed:
            logger.info(f"Validation passed for analysis {self.analysis_id}")
        else:
            logger.warning(
                f"Validation failed for analysis {self.analysis_id}: "
                f"{len(self.validation_errors)} errors"
            )
        
        return validation_passed
    
    def aggregate_results(self) -> Dict[str, Any]:
        """
        Perform final aggregation of all results.
        
        Returns:
            Comprehensive aggregated report
        """
        logger.info(f"Aggregating results for analysis {self.analysis_id}")
        
        # Validate before aggregating
        validation_passed = self.validate_results()
        
        # Merge dependencies
        merged_dependencies = self.merge_dependencies(
            self.results[AnalysisResultType.DEPENDENCIES],
            self.aggregation_strategies.get("dependencies", AggregationStrategy.UNION)
        )
        
        # Merge architecture
        merged_architecture = self.merge_architecture(
            self.results[AnalysisResultType.ARCHITECTURE],
            self.aggregation_strategies.get("architecture", AggregationStrategy.PREFER_RUNTIME)
        )
        
        # Merge performance
        merged_performance = self.merge_performance_metrics(
            self.results[AnalysisResultType.PERFORMANCE]
        )
        
        # Compile aggregated report
        aggregated_report = {
            "analysis_id": str(self.analysis_id),
            "project_id": str(self.project_id),
            "created_at": self.created_at.isoformat(),
            "aggregated_at": datetime.utcnow().isoformat(),
            "validation_passed": validation_passed,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            
            # Aggregated results
            "static_analysis": {
                "results": self.results[AnalysisResultType.STATIC_ANALYSIS],
                "count": len(self.results[AnalysisResultType.STATIC_ANALYSIS])
            },
            "runtime_analysis": {
                "results": self.results[AnalysisResultType.RUNTIME_ANALYSIS],
                "count": len(self.results[AnalysisResultType.RUNTIME_ANALYSIS])
            },
            "gap_analysis": {
                "results": self.results[AnalysisResultType.GAP_ANALYSIS],
                "count": len(self.results[AnalysisResultType.GAP_ANALYSIS])
            },
            "architecture": merged_architecture,
            "dependencies": merged_dependencies,
            "performance": merged_performance,
            "compliance": {
                "results": self.results[AnalysisResultType.COMPLIANCE],
                "count": len(self.results[AnalysisResultType.COMPLIANCE])
            },
            "risk_assessment": {
                "results": self.results[AnalysisResultType.RISK_ASSESSMENT],
                "count": len(self.results[AnalysisResultType.RISK_ASSESSMENT])
            },
            
            # Summary statistics
            "summary": {
                "total_results": sum(len(results) for results in self.results.values()),
                "result_counts_by_type": {
                    result_type.value: len(results)
                    for result_type, results in self.results.items()
                },
                "sources": self._get_all_sources(),
                "has_runtime_data": len(self.results[AnalysisResultType.RUNTIME_ANALYSIS]) > 0,
                "has_gap_analysis": len(self.results[AnalysisResultType.GAP_ANALYSIS]) > 0
            }
        }
        
        logger.info(
            f"Aggregation complete for analysis {self.analysis_id}: "
            f"{aggregated_report['summary']['total_results']} total results"
        )
        
        return aggregated_report
    
    def _get_all_sources(self) -> List[str]:
        """
        Get list of all unique sources that contributed results.
        
        Returns:
            List of source identifiers
        """
        sources: Set[str] = set()
        for results in self.results.values():
            for result in results:
                sources.add(result.get("source", "unknown"))
        return sorted(list(sources))
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of current aggregation state.
        
        Returns:
            Summary dictionary
        """
        return {
            "analysis_id": str(self.analysis_id),
            "project_id": str(self.project_id),
            "created_at": self.created_at.isoformat(),
            "total_results": sum(len(results) for results in self.results.values()),
            "result_counts": {
                result_type.value: len(results)
                for result_type, results in self.results.items()
            },
            "sources": self._get_all_sources(),
            "validation_errors": len(self.validation_errors),
            "validation_warnings": len(self.validation_warnings)
        }
