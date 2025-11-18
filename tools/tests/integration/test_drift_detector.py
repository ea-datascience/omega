"""Integration tests for drift detector."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from omega_analysis.analysis.drift.drift_detector import (
    DriftDetector,
    DriftAnalysis,
    DriftSeverity,
    Trend,
    MetricDrift,
    BaselineComparison,
    DriftPattern
)


@pytest.fixture
def drift_detector():
    """Create drift detector with default config."""
    return DriftDetector()


@pytest.fixture
def custom_drift_detector():
    """Create drift detector with custom thresholds."""
    config = {
        "thresholds": {
            "performance_degradation_pct": 20.0,
            "coupling_increase_pct": 25.0,
            "complexity_increase_pct": 20.0,
            "quality_decline_pct": 15.0,
            "critical_threshold_pct": 50.0,
            "volatile_variance": 0.4
        },
        "trend_analysis": {
            "min_data_points": 3,
            "stable_range_pct": 10.0,
            "improvement_threshold_pct": 10.0
        },
        "weights": {
            "performance": 0.40,
            "coupling": 0.30,
            "complexity": 0.20,
            "quality": 0.10
        }
    }
    return DriftDetector(config)


@pytest.fixture
def baseline_analysis():
    """Create baseline analysis data."""
    return {
        "analysis_id": "baseline_001",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "application_name": "test-app",
        "performance_baseline": {
            "response_time_p95": 150.0,  # ms
            "error_rate": 0.01,  # 1%
            "requests_per_second": 100.0
        },
        "coupling_metrics": {
            "coupling_density": 0.25,
            "average_instability": 0.45,
            "circular_dependency_count": 2
        },
        "complexity_score": {
            "overall_score": 65.0,
            "estimated_effort_weeks": 12.0
        },
        "quality_metrics": {
            "maintainability_index": 72.0,
            "test_coverage": 0.75
        }
    }


@pytest.fixture
def current_analysis_degraded(baseline_analysis):
    """Create current analysis showing degradation."""
    return {
        "analysis_id": "current_001",
        "timestamp": datetime.now().isoformat(),
        "application_name": "test-app",
        "performance_baseline": {
            "response_time_p95": 200.0,  # +33% slower
            "error_rate": 0.025,  # +150% more errors
            "requests_per_second": 80.0  # -20% throughput
        },
        "coupling_metrics": {
            "coupling_density": 0.35,  # +40% more coupling
            "average_instability": 0.58,  # +29% more unstable
            "circular_dependency_count": 5  # +150% circular deps
        },
        "complexity_score": {
            "overall_score": 85.0,  # +31% more complex
            "estimated_effort_weeks": 18.0  # +50% more effort
        },
        "quality_metrics": {
            "maintainability_index": 60.0,  # -17% less maintainable
            "test_coverage": 0.65  # -13% less coverage
        }
    }


@pytest.fixture
def current_analysis_improved(baseline_analysis):
    """Create current analysis showing improvement."""
    return {
        "analysis_id": "current_002",
        "timestamp": datetime.now().isoformat(),
        "application_name": "test-app",
        "performance_baseline": {
            "response_time_p95": 120.0,  # -20% faster
            "error_rate": 0.005,  # -50% fewer errors
            "requests_per_second": 130.0  # +30% throughput
        },
        "coupling_metrics": {
            "coupling_density": 0.20,  # -20% less coupling
            "average_instability": 0.35,  # -22% more stable
            "circular_dependency_count": 1  # -50% fewer cycles
        },
        "complexity_score": {
            "overall_score": 50.0,  # -23% less complex
            "estimated_effort_weeks": 9.0  # -25% less effort
        },
        "quality_metrics": {
            "maintainability_index": 82.0,  # +14% more maintainable
            "test_coverage": 0.85  # +13% more coverage
        }
    }


@pytest.fixture
def current_analysis_stable(baseline_analysis):
    """Create current analysis showing stability."""
    return {
        "analysis_id": "current_003",
        "timestamp": datetime.now().isoformat(),
        "application_name": "test-app",
        "performance_baseline": {
            "response_time_p95": 152.0,  # +1.3% (stable)
            "error_rate": 0.0105,  # +5% (stable)
            "requests_per_second": 98.0  # -2% (stable)
        },
        "coupling_metrics": {
            "coupling_density": 0.26,  # +4% (stable)
            "average_instability": 0.46,  # +2.2% (stable)
            "circular_dependency_count": 2  # Same
        },
        "complexity_score": {
            "overall_score": 67.0,  # +3% (stable)
            "estimated_effort_weeks": 12.5  # +4.2% (stable)
        },
        "quality_metrics": {
            "maintainability_index": 71.0,  # -1.4% (stable)
            "test_coverage": 0.74  # -1.3% (stable)
        }
    }


def test_drift_detector_initialization(drift_detector):
    """Test drift detector initializes correctly."""
    assert drift_detector is not None
    assert "thresholds" in drift_detector.config
    assert "trend_analysis" in drift_detector.config
    assert "weights" in drift_detector.config


def test_custom_configuration(custom_drift_detector):
    """Test custom configuration is applied."""
    assert custom_drift_detector.config["thresholds"]["performance_degradation_pct"] == 20.0
    assert custom_drift_detector.config["weights"]["performance"] == 0.40


def test_detect_drift_with_degradation(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test drift detection with degraded metrics."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    assert isinstance(analysis, DriftAnalysis)
    assert analysis.application_name == "test-app"
    assert analysis.baselines_analyzed == 1
    assert len(analysis.baseline_comparisons) == 1
    
    # Should detect degradation
    comparison = analysis.baseline_comparisons[0]
    assert comparison.overall_trend == Trend.DEGRADING
    assert comparison.overall_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
    
    # Health score should be low
    assert analysis.overall_health_score < 70.0


def test_detect_drift_with_improvement(drift_detector, baseline_analysis, current_analysis_improved):
    """Test drift detection with improved metrics."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_improved,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should detect improvement
    comparison = analysis.baseline_comparisons[0]
    assert comparison.overall_trend == Trend.IMPROVING
    
    # Health score should be high
    assert analysis.overall_health_score > 80.0
    assert analysis.improved_metrics_count > 0


def test_detect_drift_with_stability(drift_detector, baseline_analysis, current_analysis_stable):
    """Test drift detection with stable metrics."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_stable,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should detect stability
    comparison = analysis.baseline_comparisons[0]
    assert comparison.overall_trend in [Trend.STABLE, Trend.IMPROVING]
    assert comparison.overall_severity in [DriftSeverity.NONE, DriftSeverity.LOW]
    
    # Health score should be high
    assert analysis.overall_health_score > 85.0


def test_performance_drift_detection(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test performance metric drift detection."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Check P95 response time drift
    assert "p95_response_time" in comparison.performance_drift
    p95_drift = comparison.performance_drift["p95_response_time"]
    assert p95_drift.change_percentage > 30.0  # 33% increase
    assert p95_drift.trend == Trend.DEGRADING
    assert p95_drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
    
    # Check error rate drift
    assert "error_rate" in comparison.performance_drift
    error_drift = comparison.performance_drift["error_rate"]
    assert error_drift.change_percentage > 100.0  # 150% increase
    assert error_drift.trend == Trend.DEGRADING
    
    # Check throughput drift
    assert "throughput" in comparison.performance_drift
    throughput_drift = comparison.performance_drift["throughput"]
    assert throughput_drift.change_percentage < 0  # Negative change
    assert throughput_drift.trend == Trend.DEGRADING


def test_coupling_drift_detection(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test coupling metric drift detection."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Check coupling density drift
    assert "coupling_density" in comparison.coupling_drift
    density_drift = comparison.coupling_drift["coupling_density"]
    assert density_drift.change_percentage > 35.0  # 40% increase
    assert density_drift.trend == Trend.DEGRADING
    
    # Check instability drift
    assert "avg_instability" in comparison.coupling_drift
    instability_drift = comparison.coupling_drift["avg_instability"]
    assert instability_drift.change_percentage > 25.0  # 29% increase
    assert instability_drift.trend == Trend.DEGRADING
    
    # Check circular dependencies drift
    assert "circular_dependencies" in comparison.coupling_drift
    circular_drift = comparison.coupling_drift["circular_dependencies"]
    assert circular_drift.change_percentage > 100.0  # 150% increase
    assert circular_drift.trend == Trend.DEGRADING


def test_complexity_drift_detection(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test complexity metric drift detection."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Check complexity score drift
    assert "complexity_score" in comparison.complexity_drift
    complexity_drift = comparison.complexity_drift["complexity_score"]
    assert complexity_drift.change_percentage > 30.0  # 31% increase
    assert complexity_drift.trend == Trend.DEGRADING
    
    # Check effort estimate drift
    assert "effort_estimate" in comparison.complexity_drift
    effort_drift = comparison.complexity_drift["effort_estimate"]
    assert effort_drift.change_percentage > 45.0  # 50% increase
    assert effort_drift.trend == Trend.DEGRADING


def test_quality_drift_detection(drift_detector, baseline_analysis, current_analysis_improved):
    """Test quality metric drift detection."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_improved,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Check maintainability drift
    assert "maintainability" in comparison.quality_drift
    maintainability_drift = comparison.quality_drift["maintainability"]
    assert maintainability_drift.change_percentage > 10.0  # 14% increase
    assert maintainability_drift.trend == Trend.IMPROVING
    
    # Check test coverage drift
    assert "test_coverage" in comparison.quality_drift
    coverage_drift = comparison.quality_drift["test_coverage"]
    assert coverage_drift.change_percentage > 10.0  # 13% increase
    assert coverage_drift.trend == Trend.IMPROVING


def test_trend_calculation(drift_detector):
    """Test trend calculation from change percentage."""
    # Degrading (higher is worse)
    trend = drift_detector._determine_trend(15.0, higher_is_worse=True)
    assert trend == Trend.DEGRADING
    
    # Improving (higher is worse)
    trend = drift_detector._determine_trend(-15.0, higher_is_worse=True)
    assert trend == Trend.IMPROVING
    
    # Improving (higher is better)
    trend = drift_detector._determine_trend(15.0, higher_is_worse=False)
    assert trend == Trend.IMPROVING
    
    # Degrading (higher is better)
    trend = drift_detector._determine_trend(-15.0, higher_is_worse=False)
    assert trend == Trend.DEGRADING
    
    # Stable
    trend = drift_detector._determine_trend(2.0, higher_is_worse=True)
    assert trend == Trend.STABLE


def test_severity_calculation(drift_detector):
    """Test severity calculation from change percentage."""
    # None (good direction)
    severity = drift_detector._determine_severity(-10.0, higher_is_worse=True)
    assert severity == DriftSeverity.NONE
    
    # Low
    severity = drift_detector._determine_severity(8.0, higher_is_worse=True)
    assert severity == DriftSeverity.LOW
    
    # Medium
    severity = drift_detector._determine_severity(15.0, higher_is_worse=True)
    assert severity == DriftSeverity.MEDIUM
    
    # High
    severity = drift_detector._determine_severity(25.0, higher_is_worse=True)
    assert severity == DriftSeverity.HIGH
    
    # Critical
    severity = drift_detector._determine_severity(35.0, higher_is_worse=True)
    assert severity == DriftSeverity.CRITICAL


def test_multiple_baselines(drift_detector, baseline_analysis):
    """Test drift detection with multiple historical baselines."""
    # Create additional baselines
    baseline_2 = {
        **baseline_analysis,
        "analysis_id": "baseline_002",
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "performance_baseline": {
            "response_time_p95": 160.0,
            "error_rate": 0.015,
            "requests_per_second": 95.0
        }
    }
    
    current = {
        **baseline_analysis,
        "analysis_id": "current_001",
        "timestamp": datetime.now().isoformat(),
        "performance_baseline": {
            "response_time_p95": 180.0,
            "error_rate": 0.020,
            "requests_per_second": 85.0
        }
    }
    
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current,
        baseline_analyses=[baseline_2, baseline_analysis]  # Most recent first
    )
    
    assert analysis.baselines_analyzed == 2
    assert len(analysis.baseline_comparisons) == 2


def test_drift_pattern_identification(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test identification of drift patterns."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should identify multiple drift patterns
    assert len(analysis.drift_patterns) > 0
    
    # Check for specific patterns
    pattern_types = [p["pattern"] for p in analysis.drift_patterns]
    assert DriftPattern.PERFORMANCE_DEGRADATION.value in pattern_types
    assert DriftPattern.COUPLING_INCREASE.value in pattern_types
    assert DriftPattern.COMPLEXITY_GROWTH.value in pattern_types


def test_alerts_generation(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test alert generation for critical drift."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should have critical alerts
    assert len(analysis.critical_alerts) > 0
    
    # Should have degradation warnings
    assert len(analysis.degradation_warnings) > 0
    
    # Should have recommendations
    assert len(analysis.recommendations) > 0


def test_improvement_highlights(drift_detector, baseline_analysis, current_analysis_improved):
    """Test improvement highlights for positive changes."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_improved,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should have improvement highlights
    assert len(analysis.improvement_highlights) > 0


def test_summary_statistics(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test summary statistics calculation."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    # Should track all metrics
    assert analysis.total_metrics_tracked > 0
    assert analysis.degraded_metrics_count > 0
    assert analysis.improved_metrics_count + analysis.degraded_metrics_count + analysis.stable_metrics_count == analysis.total_metrics_tracked


def test_health_score_calculation(drift_detector, baseline_analysis, current_analysis_degraded, current_analysis_improved):
    """Test health score calculation."""
    # Degraded scenario
    degraded_analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    # Improved scenario
    improved_analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_improved,
        baseline_analyses=[baseline_analysis]
    )
    
    # Health score should be between 0-100
    assert 0 <= degraded_analysis.overall_health_score <= 100
    assert 0 <= improved_analysis.overall_health_score <= 100
    
    # Improved should have higher health score
    assert improved_analysis.overall_health_score > degraded_analysis.overall_health_score


def test_export_analysis(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test exporting drift analysis to JSON."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "drift_analysis.json"
        
        drift_detector.export_analysis(analysis, output_path)
        
        # Verify file was created
        assert output_path.exists()
        
        # Verify content is valid JSON
        with open(output_path) as f:
            data = json.load(f)
        
        assert data["analysis_id"] == analysis.analysis_id
        assert data["application_name"] == "test-app"
        assert len(data["baseline_comparisons"]) == 1
        assert "drift_patterns" in data
        assert "trends" in data
        assert "summary" in data


def test_empty_inputs_handling(drift_detector):
    """Test handling of empty inputs."""
    current = {
        "analysis_id": "current_001",
        "timestamp": datetime.now().isoformat(),
        "application_name": "test-app"
    }
    
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current,
        baseline_analyses=[]
    )
    
    # Should handle gracefully
    assert analysis.baselines_analyzed == 0
    assert len(analysis.baseline_comparisons) == 0
    assert analysis.overall_health_score == 100.0  # No drift detected


def test_metadata_preservation(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test that metadata is preserved in analysis."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    assert "current_analysis_timestamp" in analysis.analysis_metadata
    assert "oldest_baseline_timestamp" in analysis.analysis_metadata
    assert "config_used" in analysis.analysis_metadata


def test_time_calculation(drift_detector, baseline_analysis, current_analysis_degraded):
    """Test time since baseline calculation."""
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_analysis_degraded,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Should be approximately 30 days
    assert 28 <= comparison.time_since_baseline_days <= 32


def test_overall_drift_score_calculation(drift_detector, baseline_analysis):
    """Test overall drift score calculation with weights."""
    current_high_performance_drift = {
        **baseline_analysis,
        "timestamp": datetime.now().isoformat(),
        "performance_baseline": {
            "response_time_p95": 300.0,  # 100% increase
            "error_rate": 0.05,  # 400% increase
            "requests_per_second": 50.0  # 50% decrease
        }
    }
    
    analysis = drift_detector.detect_drift(
        application_name="test-app",
        current_analysis=current_high_performance_drift,
        baseline_analyses=[baseline_analysis]
    )
    
    comparison = analysis.baseline_comparisons[0]
    
    # Overall drift score should be high due to significant performance degradation
    assert comparison.overall_drift_score > 50.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
