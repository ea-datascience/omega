"""Coupling metrics calculation and analysis.

This module provides comprehensive coupling metrics calculation for
assessing migration complexity and identifying service boundaries.
"""

from .coupling_analyzer import (
    CouplingAnalyzer,
    CouplingMetrics,
    ComponentCoupling,
    CouplingType,
    CouplingStrength,
    TemporalCoupling,
    CouplingHotspot
)

__all__ = [
    'CouplingAnalyzer',
    'CouplingMetrics',
    'ComponentCoupling',
    'CouplingType',
    'CouplingStrength',
    'TemporalCoupling',
    'CouplingHotspot'
]
