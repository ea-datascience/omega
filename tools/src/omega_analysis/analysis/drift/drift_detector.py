"""Architectural drift detector for baseline comparison and trend analysis.

Detects architectural drift by comparing current analysis against historical baselines:
- Performance degradation detection
- Coupling trend analysis
- Complexity evolution tracking
- Quality metric changes
- Architectural pattern drift
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import json
import statistics

logger = logging.getLogger(__name__)


class DriftSeverity(Enum):
    """Severity of detected drift."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Trend(Enum):
    """Trend direction for metrics."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


class DriftPattern(Enum):
    """Types of drift patterns."""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    COUPLING_INCREASE = "coupling_increase"
    COMPLEXITY_GROWTH = "complexity_growth"
    QUALITY_DECLINE = "quality_decline"
    DEPENDENCY_PROLIFERATION = "dependency_proliferation"
    ARCHITECTURAL_EROSION = "architectural_erosion"
    SECURITY_REGRESSION = "security_regression"


@dataclass
class MetricDrift:
    """Drift information for a single metric."""
    metric_name: str
    current_value: float
    baseline_value: float
    change_percentage: float
    trend: Trend
    severity: DriftSeverity
    threshold_exceeded: bool
    historical_values: List[float] = field(default_factory=list)


@dataclass
class BaselineComparison:
    """Comparison between current and baseline analysis."""
    baseline_id: str
    baseline_timestamp: datetime
    current_timestamp: datetime
    time_since_baseline_days: int
    
    # Performance metrics drift
    performance_drift: Dict[str, MetricDrift] = field(default_factory=dict)
    
    # Coupling metrics drift
    coupling_drift: Dict[str, MetricDrift] = field(default_factory=dict)
    
    # Complexity metrics drift
    complexity_drift: Dict[str, MetricDrift] = field(default_factory=dict)
    
    # Quality metrics drift
    quality_drift: Dict[str, MetricDrift] = field(default_factory=dict)
    
    # Overall drift assessment
    overall_drift_score: float = 0.0
    overall_trend: Trend = Trend.STABLE
    overall_severity: DriftSeverity = DriftSeverity.NONE


@dataclass
class DriftAnalysis:
    """Complete drift analysis results."""
    analysis_id: str
    application_name: str
    analyzed_at: datetime
    
    # Baseline comparisons (can compare against multiple baselines)
    baseline_comparisons: List[BaselineComparison]
    
    # Detected drift patterns
    drift_patterns: List[Dict[str, Any]] = field(default_factory=list)
    
    # Trend analysis
    performance_trends: Dict[str, Trend] = field(default_factory=dict)
    coupling_trends: Dict[str, Trend] = field(default_factory=dict)
    complexity_trends: Dict[str, Trend] = field(default_factory=dict)
    
    # Alerts and recommendations
    critical_alerts: List[str] = field(default_factory=list)
    degradation_warnings: List[str] = field(default_factory=list)
    improvement_highlights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Summary statistics
    total_metrics_tracked: int = 0
    degraded_metrics_count: int = 0
    improved_metrics_count: int = 0
    stable_metrics_count: int = 0
    overall_health_score: float = 100.0  # 0-100
    
    # Metadata
    baselines_analyzed: int = 0
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)


class DriftDetector:
    """Detects architectural drift by comparing current with historical baselines."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize drift detector.
        
        Args:
            config: Optional configuration for thresholds and weights
        """
        self.config = config or self._default_config()
        logger.info("Drift detector initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for drift detection."""
        return {
            "thresholds": {
                "performance_degradation_pct": 10.0,  # >10% slower is degradation
                "coupling_increase_pct": 15.0,  # >15% more coupling
                "complexity_increase_pct": 15.0,  # >15% more complex
                "quality_decline_pct": 10.0,  # >10% quality drop
                "critical_threshold_pct": 30.0,  # >30% change is critical
                "volatile_variance": 0.3  # Coefficient of variation >0.3 is volatile
            },
            "trend_analysis": {
                "min_data_points": 3,  # Need at least 3 points for trend
                "stable_range_pct": 5.0,  # Within ±5% is stable
                "improvement_threshold_pct": 5.0  # >5% better is improvement
            },
            "weights": {
                "performance": 0.35,
                "coupling": 0.25,
                "complexity": 0.20,
                "quality": 0.20
            }
        }
    
    def detect_drift(
        self,
        application_name: str,
        current_analysis: Dict[str, Any],
        baseline_analyses: List[Dict[str, Any]]
    ) -> DriftAnalysis:
        """Detect architectural drift by comparing current with baselines.
        
        Args:
            application_name: Name of the application
            current_analysis: Current analysis results
            baseline_analyses: List of historical baseline analyses (ordered by time)
            
        Returns:
            DriftAnalysis with complete drift detection results
        """
        logger.info(f"Detecting drift for: {application_name}")
        
        analysis_id = f"drift_{application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Compare against each baseline
        comparisons = []
        for baseline in baseline_analyses:
            comparison = self._compare_with_baseline(
                current_analysis, baseline
            )
            comparisons.append(comparison)
        
        # Analyze trends across all baselines
        performance_trends = self._analyze_performance_trends(
            current_analysis, baseline_analyses
        )
        
        coupling_trends = self._analyze_coupling_trends(
            current_analysis, baseline_analyses
        )
        
        complexity_trends = self._analyze_complexity_trends(
            current_analysis, baseline_analyses
        )
        
        # Identify drift patterns
        drift_patterns = self._identify_drift_patterns(
            comparisons, performance_trends, coupling_trends, complexity_trends
        )
        
        # Generate alerts and recommendations
        alerts, warnings, highlights, recommendations = self._generate_alerts(
            comparisons, drift_patterns
        )
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(comparisons)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(
            comparisons, summary_stats
        )
        
        # Build complete drift analysis
        drift_analysis = DriftAnalysis(
            analysis_id=analysis_id,
            application_name=application_name,
            analyzed_at=datetime.now(),
            baseline_comparisons=comparisons,
            drift_patterns=drift_patterns,
            performance_trends=performance_trends,
            coupling_trends=coupling_trends,
            complexity_trends=complexity_trends,
            critical_alerts=alerts,
            degradation_warnings=warnings,
            improvement_highlights=highlights,
            recommendations=recommendations,
            total_metrics_tracked=summary_stats.get("total_metrics", 0),
            degraded_metrics_count=summary_stats.get("degraded_count", 0),
            improved_metrics_count=summary_stats.get("improved_count", 0),
            stable_metrics_count=summary_stats.get("stable_count", 0),
            overall_health_score=health_score,
            baselines_analyzed=len(baseline_analyses),
            analysis_metadata={
                "current_analysis_timestamp": current_analysis.get("timestamp", datetime.now().isoformat()),
                "oldest_baseline_timestamp": baseline_analyses[-1].get("timestamp") if baseline_analyses else None,
                "config_used": self.config
            }
        )
        
        logger.info(f"Drift detection complete: {len(drift_patterns)} patterns detected")
        return drift_analysis
    
    def _compare_with_baseline(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> BaselineComparison:
        """Compare current analysis with a specific baseline."""
        baseline_id = baseline.get("analysis_id", "unknown")
        baseline_timestamp = datetime.fromisoformat(baseline.get("timestamp", datetime.now().isoformat()))
        current_timestamp = datetime.fromisoformat(current.get("timestamp", datetime.now().isoformat()))
        time_diff = (current_timestamp - baseline_timestamp).days
        
        comparison = BaselineComparison(
            baseline_id=baseline_id,
            baseline_timestamp=baseline_timestamp,
            current_timestamp=current_timestamp,
            time_since_baseline_days=time_diff
        )
        
        # Compare performance metrics
        if current.get("performance_baseline") and baseline.get("performance_baseline"):
            comparison.performance_drift = self._compare_performance_metrics(
                current["performance_baseline"],
                baseline["performance_baseline"]
            )
        
        # Compare coupling metrics
        if current.get("coupling_metrics") and baseline.get("coupling_metrics"):
            comparison.coupling_drift = self._compare_coupling_metrics(
                current["coupling_metrics"],
                baseline["coupling_metrics"]
            )
        
        # Compare complexity metrics
        if current.get("complexity_score") and baseline.get("complexity_score"):
            comparison.complexity_drift = self._compare_complexity_metrics(
                current["complexity_score"],
                baseline["complexity_score"]
            )
        
        # Compare quality metrics
        if current.get("quality_metrics") and baseline.get("quality_metrics"):
            comparison.quality_drift = self._compare_quality_metrics(
                current["quality_metrics"],
                baseline["quality_metrics"]
            )
        
        # Calculate overall drift
        comparison.overall_drift_score = self._calculate_overall_drift(comparison)
        comparison.overall_trend = self._determine_overall_trend(comparison)
        comparison.overall_severity = self._determine_overall_severity(comparison)
        
        return comparison
    
    def _compare_performance_metrics(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> Dict[str, MetricDrift]:
        """Compare performance metrics."""
        drift_metrics = {}
        
        # P95 response time
        if "response_time_p95" in current and "response_time_p95" in baseline:
            current_val = current["response_time_p95"]
            baseline_val = baseline["response_time_p95"]
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["p95_response_time"] = MetricDrift(
                metric_name="P95 Response Time",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["performance_degradation_pct"]
            )
        
        # Error rate
        if "error_rate" in current and "error_rate" in baseline:
            current_val = current["error_rate"] * 100  # Convert to percentage
            baseline_val = baseline["error_rate"] * 100
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["error_rate"] = MetricDrift(
                metric_name="Error Rate",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["performance_degradation_pct"]
            )
        
        # Throughput
        if "requests_per_second" in current and "requests_per_second" in baseline:
            current_val = current["requests_per_second"]
            baseline_val = baseline["requests_per_second"]
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["throughput"] = MetricDrift(
                metric_name="Throughput (RPS)",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=False),
                severity=self._determine_severity(change_pct, higher_is_worse=False),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["performance_degradation_pct"]
            )
        
        return drift_metrics
    
    def _compare_coupling_metrics(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> Dict[str, MetricDrift]:
        """Compare coupling metrics."""
        drift_metrics = {}
        
        # Coupling density
        if "coupling_density" in current and "coupling_density" in baseline:
            current_val = current["coupling_density"] * 100
            baseline_val = baseline["coupling_density"] * 100
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["coupling_density"] = MetricDrift(
                metric_name="Coupling Density",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["coupling_increase_pct"]
            )
        
        # Average instability
        if "average_instability" in current and "average_instability" in baseline:
            current_val = current["average_instability"]
            baseline_val = baseline["average_instability"]
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["avg_instability"] = MetricDrift(
                metric_name="Average Instability",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["coupling_increase_pct"]
            )
        
        # Circular dependencies
        if "circular_dependency_count" in current and "circular_dependency_count" in baseline:
            current_val = float(current["circular_dependency_count"])
            baseline_val = float(baseline["circular_dependency_count"])
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["circular_dependencies"] = MetricDrift(
                metric_name="Circular Dependencies",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["coupling_increase_pct"]
            )
        
        return drift_metrics
    
    def _compare_complexity_metrics(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> Dict[str, MetricDrift]:
        """Compare complexity metrics."""
        drift_metrics = {}
        
        # Overall complexity score
        if "overall_score" in current and "overall_score" in baseline:
            current_val = current["overall_score"]
            baseline_val = baseline["overall_score"]
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["complexity_score"] = MetricDrift(
                metric_name="Complexity Score",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["complexity_increase_pct"]
            )
        
        # Estimated effort weeks
        if "estimated_effort_weeks" in current and "estimated_effort_weeks" in baseline:
            current_val = float(current["estimated_effort_weeks"])
            baseline_val = float(baseline["estimated_effort_weeks"])
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["effort_estimate"] = MetricDrift(
                metric_name="Estimated Effort (weeks)",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=True),
                severity=self._determine_severity(change_pct, higher_is_worse=True),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["complexity_increase_pct"]
            )
        
        return drift_metrics
    
    def _compare_quality_metrics(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> Dict[str, MetricDrift]:
        """Compare quality metrics."""
        drift_metrics = {}
        
        # Maintainability index
        if "maintainability_index" in current and "maintainability_index" in baseline:
            current_val = current["maintainability_index"]
            baseline_val = baseline["maintainability_index"]
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["maintainability"] = MetricDrift(
                metric_name="Maintainability Index",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=False),  # Higher is better
                severity=self._determine_severity(change_pct, higher_is_worse=False),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["quality_decline_pct"]
            )
        
        # Test coverage
        if "test_coverage" in current and "test_coverage" in baseline:
            current_val = current["test_coverage"] * 100
            baseline_val = baseline["test_coverage"] * 100
            change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
            
            drift_metrics["test_coverage"] = MetricDrift(
                metric_name="Test Coverage",
                current_value=current_val,
                baseline_value=baseline_val,
                change_percentage=change_pct,
                trend=self._determine_trend(change_pct, higher_is_worse=False),
                severity=self._determine_severity(change_pct, higher_is_worse=False),
                threshold_exceeded=abs(change_pct) > self.config["thresholds"]["quality_decline_pct"]
            )
        
        return drift_metrics
    
    def _determine_trend(self, change_pct: float, higher_is_worse: bool = True) -> Trend:
        """Determine trend based on change percentage."""
        stable_range = self.config["trend_analysis"]["stable_range_pct"]
        improvement_threshold = self.config["trend_analysis"]["improvement_threshold_pct"]
        
        if abs(change_pct) <= stable_range:
            return Trend.STABLE
        
        if higher_is_worse:
            # For metrics where higher is worse (latency, coupling, complexity)
            if change_pct > improvement_threshold:
                return Trend.DEGRADING
            elif change_pct < -improvement_threshold:
                return Trend.IMPROVING
        else:
            # For metrics where higher is better (throughput, quality)
            if change_pct > improvement_threshold:
                return Trend.IMPROVING
            elif change_pct < -improvement_threshold:
                return Trend.DEGRADING
        
        return Trend.STABLE
    
    def _determine_severity(self, change_pct: float, higher_is_worse: bool = True) -> DriftSeverity:
        """Determine severity based on change percentage."""
        abs_change = abs(change_pct)
        
        # If metric moved in good direction, no severity
        if higher_is_worse and change_pct < 0:
            return DriftSeverity.NONE
        elif not higher_is_worse and change_pct > 0:
            return DriftSeverity.NONE
        
        # Determine severity based on magnitude
        critical_threshold = self.config["thresholds"]["critical_threshold_pct"]
        
        if abs_change >= critical_threshold:
            return DriftSeverity.CRITICAL
        elif abs_change >= critical_threshold * 0.7:
            return DriftSeverity.HIGH
        elif abs_change >= critical_threshold * 0.4:
            return DriftSeverity.MEDIUM
        elif abs_change >= critical_threshold * 0.2:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE
    
    def _calculate_overall_drift(self, comparison: BaselineComparison) -> float:
        """Calculate overall drift score."""
        weights = self.config["weights"]
        
        # Calculate weighted drift for each category
        perf_drift = sum(abs(m.change_percentage) for m in comparison.performance_drift.values())
        coupling_drift = sum(abs(m.change_percentage) for m in comparison.coupling_drift.values())
        complexity_drift = sum(abs(m.change_percentage) for m in comparison.complexity_drift.values())
        quality_drift = sum(abs(m.change_percentage) for m in comparison.quality_drift.values())
        
        # Normalize by number of metrics
        perf_avg = perf_drift / len(comparison.performance_drift) if comparison.performance_drift else 0
        coupling_avg = coupling_drift / len(comparison.coupling_drift) if comparison.coupling_drift else 0
        complexity_avg = complexity_drift / len(comparison.complexity_drift) if comparison.complexity_drift else 0
        quality_avg = quality_drift / len(comparison.quality_drift) if comparison.quality_drift else 0
        
        # Weighted average
        overall_drift = (
            perf_avg * weights["performance"] +
            coupling_avg * weights["coupling"] +
            complexity_avg * weights["complexity"] +
            quality_avg * weights["quality"]
        )
        
        return round(overall_drift, 2)
    
    def _determine_overall_trend(self, comparison: BaselineComparison) -> Trend:
        """Determine overall trend from all metrics."""
        all_trends = []
        
        for metric in comparison.performance_drift.values():
            all_trends.append(metric.trend)
        for metric in comparison.coupling_drift.values():
            all_trends.append(metric.trend)
        for metric in comparison.complexity_drift.values():
            all_trends.append(metric.trend)
        for metric in comparison.quality_drift.values():
            all_trends.append(metric.trend)
        
        if not all_trends:
            return Trend.STABLE
        
        # Count trend occurrences
        degrading = sum(1 for t in all_trends if t == Trend.DEGRADING)
        improving = sum(1 for t in all_trends if t == Trend.IMPROVING)
        stable = sum(1 for t in all_trends if t == Trend.STABLE)
        
        # Majority vote
        total = len(all_trends)
        if degrading > total * 0.4:
            return Trend.DEGRADING
        elif improving > total * 0.4:
            return Trend.IMPROVING
        elif stable > total * 0.6:
            return Trend.STABLE
        else:
            return Trend.VOLATILE
    
    def _determine_overall_severity(self, comparison: BaselineComparison) -> DriftSeverity:
        """Determine overall severity from all metrics."""
        all_severities = []
        
        for metric in comparison.performance_drift.values():
            all_severities.append(metric.severity)
        for metric in comparison.coupling_drift.values():
            all_severities.append(metric.severity)
        for metric in comparison.complexity_drift.values():
            all_severities.append(metric.severity)
        for metric in comparison.quality_drift.values():
            all_severities.append(metric.severity)
        
        if not all_severities:
            return DriftSeverity.NONE
        
        # Take highest severity
        if any(s == DriftSeverity.CRITICAL for s in all_severities):
            return DriftSeverity.CRITICAL
        elif any(s == DriftSeverity.HIGH for s in all_severities):
            return DriftSeverity.HIGH
        elif any(s == DriftSeverity.MEDIUM for s in all_severities):
            return DriftSeverity.MEDIUM
        elif any(s == DriftSeverity.LOW for s in all_severities):
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE
    
    def _analyze_performance_trends(
        self,
        current: Dict[str, Any],
        baselines: List[Dict[str, Any]]
    ) -> Dict[str, Trend]:
        """Analyze performance trends over time."""
        trends = {}
        
        # Collect P95 response time history
        p95_values = [b.get("performance_baseline", {}).get("response_time_p95") 
                     for b in baselines if b.get("performance_baseline", {}).get("response_time_p95")]
        if current.get("performance_baseline", {}).get("response_time_p95"):
            p95_values.append(current["performance_baseline"]["response_time_p95"])
        
        if len(p95_values) >= self.config["trend_analysis"]["min_data_points"]:
            trends["p95_response_time"] = self._calculate_trend(p95_values, higher_is_worse=True)
        
        return trends
    
    def _analyze_coupling_trends(
        self,
        current: Dict[str, Any],
        baselines: List[Dict[str, Any]]
    ) -> Dict[str, Trend]:
        """Analyze coupling trends over time."""
        trends = {}
        
        # Collect coupling density history
        density_values = [b.get("coupling_metrics", {}).get("coupling_density") 
                         for b in baselines if b.get("coupling_metrics", {}).get("coupling_density")]
        if current.get("coupling_metrics", {}).get("coupling_density"):
            density_values.append(current["coupling_metrics"]["coupling_density"])
        
        if len(density_values) >= self.config["trend_analysis"]["min_data_points"]:
            trends["coupling_density"] = self._calculate_trend(density_values, higher_is_worse=True)
        
        return trends
    
    def _analyze_complexity_trends(
        self,
        current: Dict[str, Any],
        baselines: List[Dict[str, Any]]
    ) -> Dict[str, Trend]:
        """Analyze complexity trends over time."""
        trends = {}
        
        # Collect complexity score history
        complexity_values = [b.get("complexity_score", {}).get("overall_score") 
                            for b in baselines if b.get("complexity_score", {}).get("overall_score")]
        if current.get("complexity_score", {}).get("overall_score"):
            complexity_values.append(current["complexity_score"]["overall_score"])
        
        if len(complexity_values) >= self.config["trend_analysis"]["min_data_points"]:
            trends["complexity_score"] = self._calculate_trend(complexity_values, higher_is_worse=True)
        
        return trends
    
    def _calculate_trend(self, values: List[float], higher_is_worse: bool = True) -> Trend:
        """Calculate trend from historical values."""
        if len(values) < 2:
            return Trend.STABLE
        
        # Calculate linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate coefficient of variation for volatility
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / y_mean if y_mean != 0 else 0
        
        # Check for volatility
        if cv > self.config["thresholds"]["volatile_variance"]:
            return Trend.VOLATILE
        
        # Determine trend direction
        stable_threshold = y_mean * 0.01  # 1% of mean is stable
        
        if abs(slope) <= stable_threshold:
            return Trend.STABLE
        
        if higher_is_worse:
            return Trend.DEGRADING if slope > 0 else Trend.IMPROVING
        else:
            return Trend.IMPROVING if slope > 0 else Trend.DEGRADING
    
    def _identify_drift_patterns(
        self,
        comparisons: List[BaselineComparison],
        perf_trends: Dict[str, Trend],
        coupling_trends: Dict[str, Trend],
        complexity_trends: Dict[str, Trend]
    ) -> List[Dict[str, Any]]:
        """Identify specific drift patterns."""
        patterns = []
        
        if not comparisons:
            return patterns
        
        latest_comparison = comparisons[0]
        
        # Performance degradation pattern
        if any(m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL] 
              for m in latest_comparison.performance_drift.values()):
            patterns.append({
                "pattern": DriftPattern.PERFORMANCE_DEGRADATION.value,
                "severity": "high",
                "description": "Significant performance degradation detected",
                "affected_metrics": [m.metric_name for m in latest_comparison.performance_drift.values() 
                                    if m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]
            })
        
        # Coupling increase pattern
        if any(m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL] 
              for m in latest_comparison.coupling_drift.values()):
            patterns.append({
                "pattern": DriftPattern.COUPLING_INCREASE.value,
                "severity": "high",
                "description": "Coupling has increased significantly",
                "affected_metrics": [m.metric_name for m in latest_comparison.coupling_drift.values() 
                                    if m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]
            })
        
        # Complexity growth pattern
        if any(m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL] 
              for m in latest_comparison.complexity_drift.values()):
            patterns.append({
                "pattern": DriftPattern.COMPLEXITY_GROWTH.value,
                "severity": "high",
                "description": "System complexity has grown significantly",
                "affected_metrics": [m.metric_name for m in latest_comparison.complexity_drift.values() 
                                    if m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]
            })
        
        # Quality decline pattern
        if any(m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL] 
              for m in latest_comparison.quality_drift.values()):
            patterns.append({
                "pattern": DriftPattern.QUALITY_DECLINE.value,
                "severity": "high",
                "description": "Code quality metrics have declined",
                "affected_metrics": [m.metric_name for m in latest_comparison.quality_drift.values() 
                                    if m.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]
            })
        
        return patterns
    
    def _generate_alerts(
        self,
        comparisons: List[BaselineComparison],
        patterns: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Generate alerts, warnings, highlights, and recommendations."""
        alerts = []
        warnings = []
        highlights = []
        recommendations = []
        
        if not comparisons:
            return alerts, warnings, highlights, recommendations
        
        latest = comparisons[0]
        
        # Critical alerts
        if latest.overall_severity == DriftSeverity.CRITICAL:
            alerts.append(f"CRITICAL: Overall drift severity is CRITICAL ({latest.overall_drift_score:.1f}% drift)")
        
        # Collect all metrics
        all_metrics = (
            list(latest.performance_drift.values()) +
            list(latest.coupling_drift.values()) +
            list(latest.complexity_drift.values()) +
            list(latest.quality_drift.values())
        )
        
        # Critical and high severity alerts
        for metric in all_metrics:
            if metric.severity == DriftSeverity.CRITICAL:
                alerts.append(f"CRITICAL: {metric.metric_name} degraded by {metric.change_percentage:.1f}%")
            elif metric.severity == DriftSeverity.HIGH:
                warnings.append(f"WARNING: {metric.metric_name} degraded by {metric.change_percentage:.1f}%")
        
        # Improvements
        for metric in all_metrics:
            if metric.trend == Trend.IMPROVING and abs(metric.change_percentage) > 10:
                highlights.append(f"IMPROVEMENT: {metric.metric_name} improved by {abs(metric.change_percentage):.1f}%")
        
        # Recommendations based on patterns
        for pattern in patterns:
            if pattern["pattern"] == DriftPattern.PERFORMANCE_DEGRADATION.value:
                recommendations.extend([
                    "Profile application to identify performance bottlenecks",
                    "Review recent code changes for performance regressions",
                    "Consider rolling back recent deployments if degradation is severe"
                ])
            elif pattern["pattern"] == DriftPattern.COUPLING_INCREASE.value:
                recommendations.extend([
                    "Review recent architectural changes for coupling violations",
                    "Refactor high-coupling areas before they become technical debt",
                    "Implement architectural fitness functions to prevent further drift"
                ])
        
        return alerts, warnings, highlights, recommendations
    
    def _calculate_summary_statistics(
        self,
        comparisons: List[BaselineComparison]
    ) -> Dict[str, Any]:
        """Calculate summary statistics across all comparisons."""
        if not comparisons:
            return {"total_metrics": 0, "degraded_count": 0, "improved_count": 0, "stable_count": 0}
        
        latest = comparisons[0]
        
        all_metrics = (
            list(latest.performance_drift.values()) +
            list(latest.coupling_drift.values()) +
            list(latest.complexity_drift.values()) +
            list(latest.quality_drift.values())
        )
        
        degraded = sum(1 for m in all_metrics if m.trend == Trend.DEGRADING)
        improved = sum(1 for m in all_metrics if m.trend == Trend.IMPROVING)
        stable = sum(1 for m in all_metrics if m.trend == Trend.STABLE)
        
        return {
            "total_metrics": len(all_metrics),
            "degraded_count": degraded,
            "improved_count": improved,
            "stable_count": stable
        }
    
    def _calculate_health_score(
        self,
        comparisons: List[BaselineComparison],
        summary_stats: Dict[str, Any]
    ) -> float:
        """Calculate overall health score (0-100)."""
        if not comparisons or summary_stats["total_metrics"] == 0:
            return 100.0
        
        latest = comparisons[0]
        
        # Start with 100, subtract for degradation
        health = 100.0
        
        # Subtract based on overall drift score
        health -= min(latest.overall_drift_score * 0.5, 30)
        
        # Subtract for degraded metrics
        degraded_ratio = summary_stats["degraded_count"] / summary_stats["total_metrics"]
        health -= degraded_ratio * 30
        
        # Add back for improved metrics
        improved_ratio = summary_stats["improved_count"] / summary_stats["total_metrics"]
        health += improved_ratio * 20
        
        return max(min(health, 100.0), 0.0)
    
    def export_analysis(
        self,
        analysis: DriftAnalysis,
        output_path: Path
    ) -> None:
        """Export drift analysis to JSON file.
        
        Args:
            analysis: Drift analysis to export
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        export_data = {
            "analysis_id": analysis.analysis_id,
            "application_name": analysis.application_name,
            "analyzed_at": analysis.analyzed_at.isoformat(),
            "baselines_analyzed": analysis.baselines_analyzed,
            "baseline_comparisons": [
                {
                    "baseline_id": comp.baseline_id,
                    "baseline_timestamp": comp.baseline_timestamp.isoformat(),
                    "current_timestamp": comp.current_timestamp.isoformat(),
                    "time_since_baseline_days": comp.time_since_baseline_days,
                    "overall_drift_score": comp.overall_drift_score,
                    "overall_trend": comp.overall_trend.value,
                    "overall_severity": comp.overall_severity.value,
                    "performance_drift": {k: self._metric_to_dict(v) for k, v in comp.performance_drift.items()},
                    "coupling_drift": {k: self._metric_to_dict(v) for k, v in comp.coupling_drift.items()},
                    "complexity_drift": {k: self._metric_to_dict(v) for k, v in comp.complexity_drift.items()},
                    "quality_drift": {k: self._metric_to_dict(v) for k, v in comp.quality_drift.items()}
                }
                for comp in analysis.baseline_comparisons
            ],
            "drift_patterns": analysis.drift_patterns,
            "trends": {
                "performance": {k: v.value for k, v in analysis.performance_trends.items()},
                "coupling": {k: v.value for k, v in analysis.coupling_trends.items()},
                "complexity": {k: v.value for k, v in analysis.complexity_trends.items()}
            },
            "alerts": {
                "critical": analysis.critical_alerts,
                "warnings": analysis.degradation_warnings,
                "improvements": analysis.improvement_highlights
            },
            "recommendations": analysis.recommendations,
            "summary": {
                "total_metrics_tracked": analysis.total_metrics_tracked,
                "degraded_metrics_count": analysis.degraded_metrics_count,
                "improved_metrics_count": analysis.improved_metrics_count,
                "stable_metrics_count": analysis.stable_metrics_count,
                "overall_health_score": analysis.overall_health_score
            },
            "metadata": analysis.analysis_metadata
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Drift analysis exported to: {output_path}")
    
    def _metric_to_dict(self, metric: MetricDrift) -> Dict[str, Any]:
        """Convert MetricDrift to dictionary."""
        return {
            "metric_name": metric.metric_name,
            "current_value": metric.current_value,
            "baseline_value": metric.baseline_value,
            "change_percentage": metric.change_percentage,
            "trend": metric.trend.value,
            "severity": metric.severity.value,
            "threshold_exceeded": metric.threshold_exceeded
        }


# CLI interface for standalone testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect architectural drift')
    parser.add_argument('--application-name', required=True, help='Application name')
    parser.add_argument('--current', required=True, help='Current analysis JSON file')
    parser.add_argument('--baseline', required=True, help='Baseline analysis JSON file')
    parser.add_argument('--output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Load analyses
    with open(args.current) as f:
        current_analysis = json.load(f)
    
    with open(args.baseline) as f:
        baseline_analysis = json.load(f)
    
    # Run drift detection
    detector = DriftDetector()
    analysis = detector.detect_drift(
        application_name=args.application_name,
        current_analysis=current_analysis,
        baseline_analyses=[baseline_analysis]
    )
    
    # Print summary
    print(f"\nDrift Analysis: {analysis.application_name}")
    print(f"="*60)
    print(f"Overall Health Score: {analysis.overall_health_score:.1f}/100")
    print(f"Baselines Analyzed: {analysis.baselines_analyzed}")
    print(f"Total Metrics Tracked: {analysis.total_metrics_tracked}")
    print(f"Degraded: {analysis.degraded_metrics_count}, Improved: {analysis.improved_metrics_count}, Stable: {analysis.stable_metrics_count}")
    print(f"\nDrift Patterns: {len(analysis.drift_patterns)}")
    for pattern in analysis.drift_patterns:
        print(f"  - {pattern['pattern']}: {pattern['description']}")
    print(f"\nCritical Alerts: {len(analysis.critical_alerts)}")
    for alert in analysis.critical_alerts:
        print(f"  - {alert}")
    
    # Export if requested
    if args.output:
        detector.export_analysis(analysis, Path(args.output))
