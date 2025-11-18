"""Architectural drift detection and trend analysis.

This module provides drift detection capabilities for tracking architectural
changes and performance degradation over time.
"""

from .drift_detector import (
    DriftDetector,
    DriftAnalysis,
    DriftPattern,
    DriftSeverity,
    Trend,
    BaselineComparison,
    MetricDrift
)

__all__ = [
    'DriftDetector',
    'DriftAnalysis',
    'DriftPattern',
    'DriftSeverity',
    'Trend',
    'BaselineComparison',
    'MetricDrift'
]
