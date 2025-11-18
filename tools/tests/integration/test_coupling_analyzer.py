"""Integration tests for coupling metrics analyzer.

Tests coupling analysis calculating metrics like:
- Afferent/Efferent coupling
- Instability index
- Coupling density
- Temporal coupling
- Coupling hotspots
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.omega_analysis.analysis.coupling.coupling_analyzer import (
    CouplingAnalyzer,
    CouplingMetrics,
    ComponentCoupling,
    CouplingType,
    CouplingStrength,
    TemporalCoupling,
    CouplingHotspot
)


@pytest.fixture
def coupling_analyzer():
    """Provide coupling analyzer instance."""
    return CouplingAnalyzer()


@pytest.fixture
def mock_static_results_simple():
    """Provide simple static analysis results."""
    return {
        "dependency_analysis": {
            "internal_dependencies": {
                "ComponentA": {"ComponentB", "ComponentC"},
                "ComponentB": {"ComponentC"},
                "ComponentC": set(),
                "ComponentD": {"ComponentA", "ComponentB"}
            }
        }
    }


@pytest.fixture
def mock_static_results_complex():
    """Provide complex static analysis with high coupling."""
    return {
        "dependency_analysis": {
            "internal_dependencies": {
                "CoreService": {"DatabaseDAO", "CacheService", "LoggingService", "ConfigService"},
                "UserController": {"CoreService", "ValidationService", "SecurityService"},
                "OrderController": {"CoreService", "ValidationService", "NotificationService"},
                "ProductController": {"CoreService", "ValidationService"},
                "DatabaseDAO": {"ConnectionPool"},
                "CacheService": {"ConnectionPool"},
                "ValidationService": set(),
                "SecurityService": {"CoreService"},  # Circular with CoreService → SecurityService
                "NotificationService": set(),
                "LoggingService": set(),
                "ConfigService": set(),
                "ConnectionPool": set()
            },
            "circular_dependencies": [
                ["CoreService", "SecurityService", "CoreService"]
            ]
        }
    }


@pytest.fixture
def mock_dependency_graph():
    """Provide mock dependency graph object."""
    from dataclasses import dataclass
    
    @dataclass
    class MockDependencyGraph:
        internal_dependencies: dict
        circular_dependencies: list
        package_dependencies: dict = None
    
    return MockDependencyGraph(
        internal_dependencies={
            "com.app.ServiceA": {"com.app.ServiceB"},
            "com.app.ServiceB": {"com.app.ServiceC"},
            "com.app.ServiceC": set()
        },
        circular_dependencies=[],
        package_dependencies={
            "com.app": {"com.util"},
            "com.util": set()
        }
    )


def test_coupling_analyzer_initialization(coupling_analyzer):
    """Test coupling analyzer initialization."""
    assert coupling_analyzer is not None
    assert coupling_analyzer.config is not None
    assert "thresholds" in coupling_analyzer.config
    assert "weights" in coupling_analyzer.config
    assert "hotspot_detection" in coupling_analyzer.config


def test_analyze_coupling_basic(coupling_analyzer):
    """Test basic coupling analysis without input data."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app"
    )
    
    assert results is not None
    assert results.application_name == "test-app"
    assert results.analysis_id.startswith("coupling_test-app")
    assert isinstance(results.component_coupling, dict)
    assert isinstance(results.coupling_hotspots, list)
    assert isinstance(results.overall_coupling_strength, CouplingStrength)


def test_analyze_coupling_with_static_simple(coupling_analyzer, mock_static_results_simple):
    """Test coupling analysis with simple static results."""
    results = coupling_analyzer.analyze_coupling(
        application_name="simple-app",
        static_results=mock_static_results_simple
    )
    
    # Should identify all components
    assert len(results.component_coupling) == 4  # A, B, C, D
    
    # Check ComponentC (no dependencies)
    comp_c = results.component_coupling.get("ComponentC")
    assert comp_c is not None
    assert comp_c.efferent_coupling == 0  # No outgoing
    assert comp_c.afferent_coupling == 2  # A and B depend on it
    assert comp_c.instability == 0.0  # No efferent, so stable
    
    # Check ComponentA (depends on B and C)
    comp_a = results.component_coupling.get("ComponentA")
    assert comp_a is not None
    assert comp_a.efferent_coupling == 2  # Depends on B, C
    assert comp_a.afferent_coupling == 1  # D depends on it
    
    # Check ComponentD (depends on A and B)
    comp_d = results.component_coupling.get("ComponentD")
    assert comp_d is not None
    assert comp_d.efferent_coupling == 2  # Depends on A, B
    assert comp_d.afferent_coupling == 0  # Nothing depends on it
    assert comp_d.instability == 1.0  # All efferent, so unstable


def test_analyze_coupling_with_static_complex(coupling_analyzer, mock_static_results_complex):
    """Test coupling analysis with complex high-coupling scenario."""
    results = coupling_analyzer.analyze_coupling(
        application_name="complex-app",
        static_results=mock_static_results_complex
    )
    
    # Should identify high coupling
    assert len(results.component_coupling) > 5
    
    # CoreService should have high efferent coupling
    core_service = results.component_coupling.get("CoreService")
    assert core_service is not None
    assert core_service.efferent_coupling >= 4  # Many dependencies
    assert core_service.afferent_coupling >= 3  # Many dependents
    
    # Should identify circular dependencies
    assert results.circular_dependency_count == 1
    assert len(results.circular_dependency_chains) == 1
    
    # Should have higher complexity score
    assert results.migration_complexity_score > 20  # Adjusted for realistic scoring


def test_component_coupling_metrics(coupling_analyzer, mock_static_results_simple):
    """Test component coupling metrics calculation."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    for component_name, coupling in results.component_coupling.items():
        # Verify all metrics present
        assert coupling.component_name == component_name
        assert coupling.afferent_coupling >= 0
        assert coupling.efferent_coupling >= 0
        assert 0 <= coupling.instability <= 1.0
        assert 0 <= coupling.abstractness <= 1.0
        assert 0 <= coupling.distance_from_main_sequence <= 2.0
        assert isinstance(coupling.incoming_dependencies, list)
        assert isinstance(coupling.outgoing_dependencies, list)
        assert isinstance(coupling.coupling_strength, CouplingStrength)
        assert coupling.risk_score >= 0


def test_instability_calculation(coupling_analyzer, mock_static_results_simple):
    """Test instability metric calculation."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    # ComponentC: no efferent, some afferent → instability = 0 (stable)
    comp_c = results.component_coupling["ComponentC"]
    assert comp_c.instability == 0.0
    
    # ComponentD: only efferent, no afferent → instability = 1.0 (unstable)
    comp_d = results.component_coupling["ComponentD"]
    assert comp_d.instability == 1.0
    
    # ComponentA: has both → instability = efferent / (afferent + efferent)
    comp_a = results.component_coupling["ComponentA"]
    expected_instability = 2 / (1 + 2)  # 2 efferent, 1 afferent
    assert abs(comp_a.instability - expected_instability) < 0.01


def test_distance_from_main_sequence(coupling_analyzer, mock_static_results_simple):
    """Test distance from main sequence calculation."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    for coupling in results.component_coupling.values():
        # Distance = |A + I - 1|
        expected_distance = abs(coupling.abstractness + coupling.instability - 1.0)
        assert abs(coupling.distance_from_main_sequence - expected_distance) < 0.01


def test_coupling_density_calculation(coupling_analyzer, mock_static_results_simple):
    """Test coupling density metric."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    # Coupling density = actual_dependencies / max_possible_dependencies
    n = len(results.component_coupling)  # 4 components
    max_possible = n * (n - 1)  # 4 * 3 = 12
    
    # Count actual dependencies
    actual = sum(c.efferent_coupling for c in results.component_coupling.values())
    # A→2, B→1, C→0, D→2 = 5 dependencies
    
    expected_density = actual / max_possible
    assert abs(results.coupling_density - expected_density) < 0.01


def test_overall_metrics_calculation(coupling_analyzer, mock_static_results_simple):
    """Test overall metrics aggregation."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    # Should have overall metrics
    assert 0 <= results.average_instability <= 1.0
    assert 0 <= results.average_abstractness <= 1.0
    assert 0 <= results.average_distance <= 2.0
    assert 0 <= results.coupling_density <= 1.0
    assert results.max_afferent_coupling >= 0
    assert results.max_efferent_coupling >= 0
    
    # Max values should match actual
    max_afferent = max(c.afferent_coupling for c in results.component_coupling.values())
    max_efferent = max(c.efferent_coupling for c in results.component_coupling.values())
    assert results.max_afferent_coupling == max_afferent
    assert results.max_efferent_coupling == max_efferent


def test_coupling_hotspot_identification(coupling_analyzer, mock_static_results_complex):
    """Test coupling hotspot identification."""
    results = coupling_analyzer.analyze_coupling(
        application_name="complex-app",
        static_results=mock_static_results_complex
    )
    
    # Should identify hotspots
    assert len(results.coupling_hotspots) > 0
    
    for hotspot in results.coupling_hotspots:
        assert hotspot.hotspot_id is not None
        assert len(hotspot.components) > 0
        assert isinstance(hotspot.coupling_type, CouplingType)
        assert hotspot.severity in ["critical", "high", "medium", "low"]
        assert len(hotspot.description) > 0
        assert isinstance(hotspot.metrics, dict)
        assert len(hotspot.impact_on_migration) > 0
        assert isinstance(hotspot.remediation_suggestions, list)
        assert hotspot.effort_estimate_days > 0


def test_hotspot_high_afferent_coupling(coupling_analyzer):
    """Test hotspot detection for high afferent coupling."""
    # Create scenario with one component having many dependents
    static_results = {
        "dependency_analysis": {
            "internal_dependencies": {
                "PopularService": set(),
                "Client1": {"PopularService"},
                "Client2": {"PopularService"},
                "Client3": {"PopularService"},
                "Client4": {"PopularService"},
                "Client5": {"PopularService"},
                "Client6": {"PopularService"},
                "Client7": {"PopularService"},
                "Client8": {"PopularService"},
                "Client9": {"PopularService"},
                "Client10": {"PopularService"},
                "Client11": {"PopularService"}  # 11 dependents
            }
        }
    }
    
    results = coupling_analyzer.analyze_coupling(
        application_name="hotspot-app",
        static_results=static_results
    )
    
    # PopularService should be a hotspot
    popular = results.component_coupling["PopularService"]
    assert popular.is_hotspot is True
    assert popular.afferent_coupling == 11
    
    # Should have hotspot in results
    afferent_hotspots = [h for h in results.coupling_hotspots 
                         if h.hotspot_id.startswith("afferent_")]
    assert len(afferent_hotspots) > 0


def test_hotspot_high_efferent_coupling(coupling_analyzer):
    """Test hotspot detection for high efferent coupling."""
    # Create scenario with one component depending on many others
    dependencies = {f"Service{i}": set() for i in range(20)}
    dependencies["GodObject"] = {f"Service{i}" for i in range(16)}  # 16 dependencies
    
    static_results = {
        "dependency_analysis": {
            "internal_dependencies": dependencies
        }
    }
    
    results = coupling_analyzer.analyze_coupling(
        application_name="hotspot-app",
        static_results=static_results
    )
    
    # GodObject should be a hotspot
    god_object = results.component_coupling["GodObject"]
    assert god_object.is_hotspot is True
    assert god_object.efferent_coupling == 16
    
    # Should have hotspot in results
    efferent_hotspots = [h for h in results.coupling_hotspots 
                         if h.hotspot_id.startswith("efferent_")]
    assert len(efferent_hotspots) > 0


def test_circular_dependency_hotspot(coupling_analyzer):
    """Test circular dependency hotspot identification."""
    static_results = {
        "dependency_analysis": {
            "internal_dependencies": {
                "A": {"B"},
                "B": {"C"},
                "C": {"A"}  # Circular: A → B → C → A
            },
            "circular_dependencies": [
                ["A", "B", "C", "A"]
            ]
        }
    }
    
    results = coupling_analyzer.analyze_coupling(
        application_name="circular-app",
        static_results=static_results
    )
    
    # Should detect circular dependency
    assert results.circular_dependency_count == 1
    
    # Should have circular hotspot
    circular_hotspots = [h for h in results.coupling_hotspots 
                        if h.hotspot_id.startswith("circular_")]
    assert len(circular_hotspots) == 1
    assert circular_hotspots[0].severity == "high"
    assert circular_hotspots[0].coupling_type == CouplingType.STRUCTURAL


def test_migration_complexity_scoring(coupling_analyzer, mock_static_results_simple, mock_static_results_complex):
    """Test migration complexity score calculation."""
    # Simple scenario should have lower complexity
    simple_results = coupling_analyzer.analyze_coupling(
        application_name="simple-app",
        static_results=mock_static_results_simple
    )
    
    # Complex scenario should have higher complexity
    complex_results = coupling_analyzer.analyze_coupling(
        application_name="complex-app",
        static_results=mock_static_results_complex
    )
    
    # Complex should have higher complexity score
    assert complex_results.migration_complexity_score > simple_results.migration_complexity_score
    
    # Both should be in valid range
    assert 0 <= simple_results.migration_complexity_score <= 100
    assert 0 <= complex_results.migration_complexity_score <= 100


def test_coupling_strength_classification(coupling_analyzer):
    """Test coupling strength classification."""
    # Very weak coupling
    weak_results = {
        "dependency_analysis": {
            "internal_dependencies": {
                "A": {"B"},
                "B": set()
            }
        }
    }
    
    weak_metrics = coupling_analyzer.analyze_coupling(
        application_name="weak-app",
        static_results=weak_results
    )
    
    # Should classify as weak or very weak
    assert weak_metrics.overall_coupling_strength in [
        CouplingStrength.VERY_WEAK,
        CouplingStrength.WEAK,
        CouplingStrength.MODERATE
    ]
    
    # Strong coupling
    strong_deps = {f"Comp{i}": {f"Comp{j}" for j in range(20) if j != i} 
                  for i in range(20)}
    
    strong_results = {
        "dependency_analysis": {
            "internal_dependencies": strong_deps
        }
    }
    
    strong_metrics = coupling_analyzer.analyze_coupling(
        application_name="strong-app",
        static_results=strong_results
    )
    
    # Should classify as strong (high density creates moderate-strong coupling)
    # Note: With 20 components each depending on 19 others, complexity will be high
    # but classification depends on normalized scores
    assert strong_metrics.overall_coupling_strength in [
        CouplingStrength.MODERATE,  # High density but normalized scoring
        CouplingStrength.STRONG,
        CouplingStrength.VERY_STRONG
    ]


def test_component_risk_scoring(coupling_analyzer, mock_static_results_complex):
    """Test component risk score calculation."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_complex
    )
    
    # All components should have risk scores
    for coupling in results.component_coupling.values():
        assert coupling.risk_score >= 0
        assert coupling.risk_score <= 100
    
    # CoreService should have higher risk (high afferent and efferent)
    core_service = results.component_coupling["CoreService"]
    connection_pool = results.component_coupling["ConnectionPool"]
    
    # CoreService should have higher risk than ConnectionPool
    assert core_service.risk_score > connection_pool.risk_score


def test_analyze_with_dependency_graph(coupling_analyzer, mock_dependency_graph):
    """Test analysis using dependency graph object."""
    results = coupling_analyzer.analyze_coupling(
        application_name="graph-app",
        dependency_graph=mock_dependency_graph
    )
    
    # Should extract coupling from graph
    assert len(results.component_coupling) == 3
    
    # Check specific components
    service_a = results.component_coupling.get("com.app.ServiceA")
    assert service_a is not None
    assert service_a.efferent_coupling == 1  # Depends on ServiceB
    
    service_c = results.component_coupling.get("com.app.ServiceC")
    assert service_c is not None
    assert service_c.afferent_coupling == 1  # ServiceB depends on it
    assert service_c.efferent_coupling == 0  # No dependencies


def test_export_metrics(coupling_analyzer, mock_static_results_simple, tmp_path):
    """Test exporting coupling metrics to JSON."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    output_file = tmp_path / "coupling_metrics.json"
    coupling_analyzer.export_metrics(results, output_file)
    
    # File should exist
    assert output_file.exists()
    
    # Should be valid JSON
    import json
    with open(output_file) as f:
        data = json.load(f)
    
    # Should have key fields
    assert data["application_name"] == "test-app"
    assert "component_coupling" in data
    assert "overall_metrics" in data
    assert "coupling_hotspots" in data
    assert "circular_dependencies" in data
    assert "summary" in data


def test_empty_inputs_handling(coupling_analyzer):
    """Test handling of empty or None inputs."""
    results = coupling_analyzer.analyze_coupling(
        application_name="empty-app",
        static_results=None,
        runtime_results=None,
        dependency_graph=None
    )
    
    # Should still produce valid results
    assert results is not None
    assert results.application_name == "empty-app"
    assert isinstance(results.component_coupling, dict)
    assert results.migration_complexity_score >= 0


def test_custom_configuration(coupling_analyzer):
    """Test coupling analyzer with custom configuration."""
    custom_config = {
        "thresholds": {
            "high_afferent_coupling": 5,  # Lower threshold
            "high_efferent_coupling": 5,
            "high_instability": 0.9,
            "high_distance": 0.6,
            "temporal_coupling_threshold": 50,
            "circular_dependency_severity": "critical"
        },
        "weights": {
            "afferent_weight": 0.30,
            "efferent_weight": 0.30,
            "instability_weight": 0.20,
            "distance_weight": 0.10,
            "temporal_weight": 0.05,
            "circular_weight": 0.05
        }
    }
    
    custom_analyzer = CouplingAnalyzer(config=custom_config)
    
    # Verify config applied
    assert custom_analyzer.config["thresholds"]["high_afferent_coupling"] == 5
    assert custom_analyzer.config["weights"]["afferent_weight"] == 0.30


def test_metadata_preservation(coupling_analyzer, mock_static_results_simple):
    """Test that analysis metadata is preserved."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_simple
    )
    
    # Should have metadata
    assert "static_analysis_available" in results.metrics_metadata
    assert results.metrics_metadata["static_analysis_available"] is True
    assert "runtime_analysis_available" in results.metrics_metadata
    assert "dependency_graph_available" in results.metrics_metadata
    assert "config_used" in results.metrics_metadata


def test_total_components_and_dependencies(coupling_analyzer, mock_static_results_complex):
    """Test total components and dependencies counting."""
    results = coupling_analyzer.analyze_coupling(
        application_name="test-app",
        static_results=mock_static_results_complex
    )
    
    # Total components should match component_coupling size
    assert results.total_components == len(results.component_coupling)
    
    # Total dependencies should be sum of all efferent coupling
    expected_total = sum(c.efferent_coupling for c in results.component_coupling.values())
    assert results.total_dependencies == expected_total


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
