# Architectural Drift Detection Setup Guide

## Overview

The Architectural Drift Detection system monitors how an application's architecture evolves over time by comparing current analysis against historical baselines. It identifies performance degradation, coupling increases, complexity growth, and quality declines to help teams maintain architectural integrity.

## Purpose

Track architectural evolution and detect:
- **Performance Degradation**: Response time increases, error rate spikes, throughput drops
- **Coupling Increases**: Growing dependencies between components
- **Complexity Growth**: Rising migration effort and architectural complexity
- **Quality Decline**: Decreasing maintainability and test coverage
- **Trend Analysis**: IMPROVING, STABLE, DEGRADING, or VOLATILE trends

## Installation

The drift detector is part of the `omega_analysis.analysis.drift` package:

```python
from omega_analysis.analysis.drift import (
    DriftDetector,
    DriftAnalysis,
    DriftSeverity,
    Trend
)
```

## Core Concepts

### 1. Drift Severity Levels

| Severity | Description | Threshold |
|----------|-------------|-----------|
| `NONE` | No significant drift or improving | Change in positive direction |
| `LOW` | Minor drift detected | 6-12% change |
| `MEDIUM` | Moderate drift requiring attention | 12-21% change |
| `HIGH` | Significant drift needing action | 21-30% change |
| `CRITICAL` | Critical drift requiring immediate action | >30% change |

### 2. Trend Analysis

| Trend | Description | Detection |
|-------|-------------|-----------|
| `IMPROVING` | Metrics moving in positive direction | >5% improvement |
| `STABLE` | Metrics within acceptable range | ±5% change |
| `DEGRADING` | Metrics moving in negative direction | >5% degradation |
| `VOLATILE` | Erratic changes with high variance | CV > 0.3 |

### 3. Drift Patterns

| Pattern | Description |
|---------|-------------|
| `PERFORMANCE_DEGRADATION` | Response time, error rate, or throughput degradation |
| `COUPLING_INCREASE` | Growing dependencies between components |
| `COMPLEXITY_GROWTH` | Rising migration effort and complexity scores |
| `QUALITY_DECLINE` | Decreasing maintainability or test coverage |
| `DEPENDENCY_PROLIFERATION` | Rapid growth in dependency count |
| `ARCHITECTURAL_EROSION` | Deviation from architectural principles |

## Metric Categories

### Performance Metrics

- **P95 Response Time**: 95th percentile latency
  - Higher is worse
  - Threshold: >10% increase is degradation
  
- **Error Rate**: Percentage of failed requests
  - Higher is worse
  - Threshold: >10% increase is degradation
  
- **Throughput (RPS)**: Requests per second
  - Higher is better
  - Threshold: >10% decrease is degradation

### Coupling Metrics

- **Coupling Density**: Actual dependencies / maximum possible
  - Higher is worse
  - Threshold: >15% increase is degradation
  
- **Average Instability**: Mean instability index across components
  - Higher is worse (more unstable)
  - Threshold: >15% increase is degradation
  
- **Circular Dependencies**: Count of dependency cycles
  - Higher is worse
  - Threshold: >15% increase is degradation

### Complexity Metrics

- **Complexity Score**: Overall migration complexity (0-100)
  - Higher is worse
  - Threshold: >15% increase is degradation
  
- **Estimated Effort**: Weeks required for migration
  - Higher is worse
  - Threshold: >15% increase is degradation

### Quality Metrics

- **Maintainability Index**: Code maintainability score
  - Higher is better
  - Threshold: >10% decrease is degradation
  
- **Test Coverage**: Percentage of code covered by tests
  - Higher is better
  - Threshold: >10% decrease is degradation

## Configuration

### Default Configuration

```python
default_config = {
    "thresholds": {
        "performance_degradation_pct": 10.0,  # >10% slower is degradation
        "coupling_increase_pct": 15.0,  # >15% more coupling
        "complexity_increase_pct": 15.0,  # >15% more complex
        "quality_decline_pct": 10.0,  # >10% quality drop
        "critical_threshold_pct": 30.0,  # >30% change is critical
        "volatile_variance": 0.3  # CV >0.3 is volatile
    },
    "trend_analysis": {
        "min_data_points": 3,  # Need 3+ points for trend
        "stable_range_pct": 5.0,  # ±5% is stable
        "improvement_threshold_pct": 5.0  # >5% better is improvement
    },
    "weights": {
        "performance": 0.35,  # 35% weight
        "coupling": 0.25,  # 25% weight
        "complexity": 0.20,  # 20% weight
        "quality": 0.20  # 20% weight
    }
}
```

### Custom Configuration

```python
custom_config = {
    "thresholds": {
        "performance_degradation_pct": 20.0,  # More lenient
        "coupling_increase_pct": 25.0,
        "complexity_increase_pct": 20.0,
        "quality_decline_pct": 15.0,
        "critical_threshold_pct": 50.0,  # Higher critical threshold
        "volatile_variance": 0.4
    },
    "trend_analysis": {
        "min_data_points": 5,  # Require more data points
        "stable_range_pct": 10.0,  # Wider stable range
        "improvement_threshold_pct": 10.0
    },
    "weights": {
        "performance": 0.40,  # Prioritize performance
        "coupling": 0.30,
        "complexity": 0.20,
        "quality": 0.10
    }
}

detector = DriftDetector(config=custom_config)
```

## Usage Examples

### Basic Drift Detection

```python
from omega_analysis.analysis.drift import DriftDetector
from datetime import datetime, timedelta
import json

# Initialize detector
detector = DriftDetector()

# Load current analysis
with open("current_analysis.json") as f:
    current_analysis = json.load(f)

# Load historical baselines (ordered by time, most recent first)
with open("baseline_30days_ago.json") as f:
    baseline_30d = json.load(f)
    
with open("baseline_60days_ago.json") as f:
    baseline_60d = json.load(f)

# Detect drift
analysis = detector.detect_drift(
    application_name="my-app",
    current_analysis=current_analysis,
    baseline_analyses=[baseline_30d, baseline_60d]
)

# Review results
print(f"Overall Health Score: {analysis.overall_health_score:.1f}/100")
print(f"Degraded Metrics: {analysis.degraded_metrics_count}")
print(f"Improved Metrics: {analysis.improved_metrics_count}")

# Check for critical alerts
if analysis.critical_alerts:
    print("\nCRITICAL ALERTS:")
    for alert in analysis.critical_alerts:
        print(f"  - {alert}")

# Review drift patterns
for pattern in analysis.drift_patterns:
    print(f"\n{pattern['pattern']}: {pattern['description']}")
    print(f"  Affected metrics: {', '.join(pattern['affected_metrics'])}")
```

### Exporting Drift Analysis

```python
from pathlib import Path

# Export to JSON
output_path = Path("drift_analysis_20241118.json")
detector.export_analysis(analysis, output_path)
```

### Monitoring Specific Metrics

```python
# Check performance drift
comparison = analysis.baseline_comparisons[0]

if "p95_response_time" in comparison.performance_drift:
    p95_drift = comparison.performance_drift["p95_response_time"]
    print(f"P95 Response Time:")
    print(f"  Current: {p95_drift.current_value:.1f}ms")
    print(f"  Baseline: {p95_drift.baseline_value:.1f}ms")
    print(f"  Change: {p95_drift.change_percentage:+.1f}%")
    print(f"  Trend: {p95_drift.trend.value}")
    print(f"  Severity: {p95_drift.severity.value}")

# Check coupling drift
if "coupling_density" in comparison.coupling_drift:
    density_drift = comparison.coupling_drift["coupling_density"]
    print(f"\nCoupling Density:")
    print(f"  Current: {density_drift.current_value:.1f}%")
    print(f"  Baseline: {density_drift.baseline_value:.1f}%")
    print(f"  Change: {density_drift.change_percentage:+.1f}%")
    print(f"  Trend: {density_drift.trend.value}")
```

### Trend Analysis Over Time

```python
# Review long-term trends
print("\nPerformance Trends:")
for metric_name, trend in analysis.performance_trends.items():
    print(f"  {metric_name}: {trend.value}")

print("\nCoupling Trends:")
for metric_name, trend in analysis.coupling_trends.items():
    print(f"  {metric_name}: {trend.value}")

print("\nComplexity Trends:")
for metric_name, trend in analysis.complexity_trends.items():
    print(f"  {metric_name}: {trend.value}")
```

## Analysis Structure

### Baseline Format

```python
baseline = {
    "analysis_id": "baseline_001",
    "timestamp": "2024-10-18T00:00:00",
    "application_name": "my-app",
    "performance_baseline": {
        "response_time_p95": 150.0,  # milliseconds
        "error_rate": 0.01,  # 1%
        "requests_per_second": 100.0
    },
    "coupling_metrics": {
        "coupling_density": 0.25,  # 25%
        "average_instability": 0.45,
        "circular_dependency_count": 2
    },
    "complexity_score": {
        "overall_score": 65.0,  # 0-100
        "estimated_effort_weeks": 12.0
    },
    "quality_metrics": {
        "maintainability_index": 72.0,  # 0-100
        "test_coverage": 0.75  # 75%
    }
}
```

### DriftAnalysis Output

```python
DriftAnalysis(
    analysis_id="drift_my-app_20241118_123456",
    application_name="my-app",
    analyzed_at=datetime(2024, 11, 18, 12, 34, 56),
    baselines_analyzed=2,
    
    baseline_comparisons=[
        BaselineComparison(
            baseline_id="baseline_001",
            time_since_baseline_days=30,
            overall_drift_score=18.5,  # Percentage
            overall_trend=Trend.DEGRADING,
            overall_severity=DriftSeverity.MEDIUM,
            performance_drift={...},
            coupling_drift={...},
            complexity_drift={...},
            quality_drift={...}
        )
    ],
    
    drift_patterns=[
        {
            "pattern": "performance_degradation",
            "severity": "high",
            "description": "Significant performance degradation detected",
            "affected_metrics": ["P95 Response Time", "Error Rate"]
        }
    ],
    
    critical_alerts=[
        "CRITICAL: P95 Response Time degraded by 33.3%"
    ],
    degradation_warnings=[
        "WARNING: Error Rate degraded by 150.0%"
    ],
    improvement_highlights=[],
    recommendations=[
        "Profile application to identify performance bottlenecks",
        "Review recent code changes for performance regressions"
    ],
    
    total_metrics_tracked=10,
    degraded_metrics_count=7,
    improved_metrics_count=0,
    stable_metrics_count=3,
    overall_health_score=62.3
)
```

## Interpreting Results

### Health Score (0-100)

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | No action needed |
| 80-89 | Good | Monitor trends |
| 70-79 | Fair | Review degraded metrics |
| 60-69 | Poor | Address high-priority issues |
| <60 | Critical | Immediate remediation required |

**Calculation:**
- Start at 100
- Subtract: drift_score × 0.5 (max 30 points)
- Subtract: degraded_ratio × 30
- Add: improved_ratio × 20

### Overall Drift Score

Weighted average of metric changes across categories:

```
drift_score = (
    performance_drift × 0.35 +
    coupling_drift × 0.25 +
    complexity_drift × 0.20 +
    quality_drift × 0.20
)
```

Where each category drift is the average absolute change percentage.

### Overall Trend Determination

Based on majority vote across all metrics:
- **DEGRADING**: >40% of metrics degrading
- **IMPROVING**: >40% of metrics improving
- **STABLE**: >60% of metrics stable
- **VOLATILE**: No clear majority (mixed signals)

### Overall Severity

Based on highest severity found:
- Takes maximum severity across all metrics
- Single CRITICAL metric → Overall CRITICAL
- Any HIGH metric → Overall HIGH (if no CRITICAL)
- Any MEDIUM metric → Overall MEDIUM (if no HIGH/CRITICAL)

## Best Practices

### 1. Baseline Management

- **Frequency**: Create baselines weekly or bi-weekly
- **Retention**: Keep at least 3-6 months of baselines
- **Versioning**: Tag baselines with deployment versions
- **Storage**: Store in time-series database for trend analysis

```python
# Example baseline creation schedule
baseline_schedule = {
    "weekly": "Every Monday at 00:00",
    "post_deployment": "After each production deployment",
    "milestone": "At each sprint/release boundary"
}
```

### 2. Alert Configuration

```python
# Configure alerting thresholds based on criticality
critical_apps_config = {
    "thresholds": {
        "performance_degradation_pct": 5.0,  # Strict
        "critical_threshold_pct": 15.0  # Lower critical bar
    }
}

standard_apps_config = {
    "thresholds": {
        "performance_degradation_pct": 10.0,  # Normal
        "critical_threshold_pct": 30.0  # Standard critical bar
    }
}
```

### 3. Continuous Monitoring

```python
# Daily drift detection
def daily_drift_check():
    detector = DriftDetector()
    
    # Load latest analysis
    current = load_latest_analysis()
    
    # Load baselines from last 30 days
    baselines = load_baselines_last_n_days(30)
    
    # Detect drift
    analysis = detector.detect_drift(
        application_name="my-app",
        current_analysis=current,
        baseline_analyses=baselines
    )
    
    # Alert if health score drops
    if analysis.overall_health_score < 70:
        send_alert(analysis)
    
    # Store for historical tracking
    store_drift_analysis(analysis)
```

### 4. Remediation Workflow

1. **Triage**:
   - Review critical alerts first
   - Group related drift patterns
   - Prioritize by business impact

2. **Root Cause Analysis**:
   - Compare code changes between baselines
   - Profile performance bottlenecks
   - Analyze dependency changes

3. **Remediation**:
   - Refactor high-coupling areas
   - Optimize performance hotspots
   - Improve test coverage

4. **Verification**:
   - Create new baseline
   - Run drift detection
   - Confirm improvement

### 5. Integration with CI/CD

```python
# Pre-deployment drift check
def pre_deployment_check():
    detector = DriftDetector()
    
    # Run analysis on staging environment
    staging_analysis = run_full_analysis("staging")
    
    # Compare with production baseline
    prod_baseline = load_prod_baseline()
    
    drift = detector.detect_drift(
        application_name="my-app",
        current_analysis=staging_analysis,
        baseline_analyses=[prod_baseline]
    )
    
    # Block deployment if critical drift detected
    if drift.overall_severity == DriftSeverity.CRITICAL:
        raise DeploymentBlockedError(
            f"Critical drift detected: {drift.critical_alerts}"
        )
    
    # Warn if high severity
    if drift.overall_severity == DriftSeverity.HIGH:
        log_warning(f"High severity drift: {drift.degradation_warnings}")
    
    return drift.overall_health_score > 75  # Require >75 to deploy
```

## Troubleshooting

### Issue: No Drift Detected When Expected

**Causes:**
- Baseline too recent (< threshold change)
- Thresholds too lenient
- Incomplete metric data

**Solutions:**
```python
# Use older baselines
baselines = load_baselines_older_than_days(14)

# Tighten thresholds
strict_config = {
    "thresholds": {
        "performance_degradation_pct": 5.0,
        "stable_range_pct": 2.0
    }
}

# Verify data completeness
assert all_metrics_present(current_analysis)
```

### Issue: Too Many False Positives

**Causes:**
- Thresholds too strict
- Natural variance in metrics
- Insufficient baseline samples

**Solutions:**
```python
# Relax thresholds
lenient_config = {
    "thresholds": {
        "performance_degradation_pct": 20.0,
        "volatile_variance": 0.5
    }
}

# Require more data points
trend_config = {
    "trend_analysis": {
        "min_data_points": 5,  # More samples
        "stable_range_pct": 10.0  # Wider range
    }
}
```

### Issue: Trend Analysis Not Available

**Cause:** Insufficient historical data points (< 3 required)

**Solution:**
```python
# Accumulate more baselines first
if len(baselines) < 3:
    logger.warning("Need 3+ baselines for trend analysis")
    # Continue with simple comparison
```

## CLI Usage

```bash
# Run drift detection from command line
python -m omega_analysis.analysis.drift.drift_detector \
    --application-name my-app \
    --current current_analysis.json \
    --baseline baseline_30days.json \
    --output drift_report.json
```

## References

- **Baseline Collection**: See `/workspace/docs/setup/runtime-analysis-setup.md`
- **Coupling Metrics**: See `/workspace/docs/setup/coupling-metrics-setup.md`
- **Gap Analysis**: See `/workspace/docs/setup/gap-analysis-setup.md`
- **PRD**: Epic 1.1 Milestone 2.1 - System Discovery Baseline Assessment
