# Coupling Metrics Analyzer Setup

## Overview

The Coupling Metrics Analyzer quantifies coupling strength between components to assess migration complexity and identify service boundaries. It calculates comprehensive coupling metrics from static dependency analysis and runtime call patterns.

## Purpose

The coupling analyzer provides:

1. **Structural Coupling Metrics**: Afferent/Efferent coupling from static analysis
2. **Instability Index**: Measure of component stability (I = Ce / (Ca + Ce))
3. **Abstractness**: Ratio of abstract types to concrete types
4. **Distance from Main Sequence**: Architectural violation indicator (D = |A + I - 1|)
5. **Coupling Density**: Percentage of possible couplings that exist
6. **Temporal Coupling**: Runtime call frequency and patterns
7. **Coupling Hotspots**: Problematic coupling areas requiring attention

## Key Metrics

### Afferent Coupling (Ca)

Number of components that depend on this component.
- **High Ca**: Many dependents - changes have wide impact
- **Indicator**: Central components, shared utilities
- **Migration Impact**: Difficult to extract or modify

### Efferent Coupling (Ce)

Number of components this component depends on.
- **High Ce**: Many dependencies - component is unstable
- **Indicator**: God objects, complex components
- **Migration Impact**: Fragile, changes in dependencies propagate

### Instability (I)

Formula: `I = Ce / (Ca + Ce)`
- **Range**: 0 (stable) to 1 (unstable)
- **I = 0**: No outgoing dependencies - maximally stable
- **I = 1**: No incoming dependencies - maximally unstable
- **Sweet Spot**: 0.3-0.7 depending on component type

### Abstractness (A)

Formula: `A = abstract_classes / total_classes`
- **Range**: 0 (concrete) to 1 (abstract)
- **A = 0**: All concrete implementations
- **A = 1**: All abstract/interfaces
- **Goal**: Match abstraction level to stability

### Distance from Main Sequence (D)

Formula: `D = |A + I - 1|`
- **Range**: 0 (on main sequence) to 1 (maximum deviation)
- **D ≈ 0**: Balanced architecture
- **D > 0.5**: Architectural violation
- **Zone of Pain**: High I, Low A (unstable and concrete)
- **Zone of Uselessness**: Low I, High A (stable but too abstract)

### Coupling Density

Formula: `Density = actual_dependencies / max_possible_dependencies`
- **Range**: 0% (no coupling) to 100% (fully coupled)
- **Low Density (<10%)**: Loosely coupled, good for microservices
- **High Density (>50%)**: Tightly coupled, migration challenges

## Architecture

```
CouplingAnalyzer
├── analyze_coupling()           # Main entry point
├── _calculate_component_coupling()   # Per-component metrics
├── _calculate_package_metrics()      # Package-level aggregation
├── _analyze_temporal_coupling()      # Runtime patterns
├── _identify_circular_dependencies() # Cycle detection
├── _identify_coupling_hotspots()     # Problem area identification
├── _calculate_migration_complexity() # Overall complexity score
└── export_metrics()                  # JSON export
```

## Installation

Prerequisites already met in dev container. No additional setup needed.

## Usage

### Basic Analysis

```python
from src.omega_analysis.analysis.coupling.coupling_analyzer import CouplingAnalyzer

# Initialize analyzer
analyzer = CouplingAnalyzer()

# Run coupling analysis
metrics = analyzer.analyze_coupling(
    application_name="my-app",
    static_results=static_analysis_results
)

# Review results
print(f"Coupling Density: {metrics.coupling_density:.2%}")
print(f"Migration Complexity: {metrics.migration_complexity_score:.1f}/100")
print(f"Coupling Hotspots: {len(metrics.coupling_hotspots)}")
```

### With Dependency Graph

```python
from src.omega_analysis.analysis.static.dependency_extractor import DependencyExtractor

# Extract dependencies
extractor = DependencyExtractor()
dep_graph = extractor.analyze_dependencies(source_path)

# Analyze coupling
metrics = analyzer.analyze_coupling(
    application_name="my-app",
    dependency_graph=dep_graph
)
```

### Custom Configuration

```python
custom_config = {
    "thresholds": {
        "high_afferent_coupling": 8,   # Components with >8 dependents
        "high_efferent_coupling": 12,  # Components with >12 dependencies
        "high_instability": 0.85,       # Instability > 0.85
        "high_distance": 0.6,           # Distance > 0.6
        "temporal_coupling_threshold": 200
    },
    "weights": {
        "afferent_weight": 0.30,
        "efferent_weight": 0.30,
        "instability_weight": 0.20,
        "distance_weight": 0.15,
        "temporal_weight": 0.05
    }
}

analyzer = CouplingAnalyzer(config=custom_config)
```

## Interpreting Results

### Component Coupling

```python
for name, coupling in metrics.component_coupling.items():
    print(f"{name}:")
    print(f"  Afferent: {coupling.afferent_coupling}")
    print(f"  Efferent: {coupling.efferent_coupling}")
    print(f"  Instability: {coupling.instability:.3f}")
    print(f"  Distance: {coupling.distance_from_main_sequence:.3f}")
    print(f"  Risk Score: {coupling.risk_score:.1f}")
    print(f"  Hotspot: {coupling.is_hotspot}")
```

### Coupling Hotspots

```python
for hotspot in metrics.coupling_hotspots:
    print(f"\n{hotspot.severity.upper()}: {hotspot.description}")
    print(f"Components: {', '.join(hotspot.components[:3])}")
    print(f"Impact: {hotspot.impact_on_migration}")
    print(f"Effort: {hotspot.effort_estimate_days} days")
    print(f"Remediation:")
    for suggestion in hotspot.remediation_suggestions:
        print(f"  - {suggestion}")
```

### Export Results

```python
from pathlib import Path

output_path = Path("/workspace/output/coupling_metrics.json")
analyzer.export_metrics(metrics, output_path)
```

## Migration Complexity Scoring

The analyzer calculates a migration complexity score (0-100) based on:

```python
complexity = (
    afferent_score * 0.25 +    # Impact of changes
    efferent_score * 0.25 +    # Fragility
    instability_score * 0.20 + # Stability issues
    distance_score * 0.15 +    # Architectural violations
    temporal_score * 0.10 +    # Runtime coupling
    circular_score * 0.05      # Circular dependencies
)
```

**Score Interpretation**:
- **0-20**: Low complexity - straightforward migration
- **20-40**: Moderate complexity - manageable with planning
- **40-60**: High complexity - requires significant refactoring
- **60-80**: Very high complexity - major architectural changes needed
- **80-100**: Extreme complexity - consider phased approach

## Coupling Strength Classification

- **Very Weak** (0-20): Minimal coupling, easy to separate
- **Weak** (20-40): Some coupling, manageable extraction
- **Moderate** (40-60): Moderate coupling, requires refactoring
- **Strong** (60-80): Strong coupling, difficult to separate
- **Very Strong** (80-100): Extremely tight coupling, major rework needed

## Hotspot Types

### High Afferent Coupling

**Issue**: Many components depend on this component
**Impact**: Changes have wide ripple effects
**Remediation**:
- Extract interface to decouple dependents
- Apply dependency inversion principle
- Split into smaller, focused components

### High Efferent Coupling

**Issue**: Component depends on many others
**Impact**: High fragility, unstable
**Remediation**:
- Reduce dependencies through refactoring
- Apply facade pattern
- Consider extracting to microservice

### Circular Dependencies

**Issue**: Components form dependency cycles
**Impact**: Prevents clean service boundaries
**Remediation**:
- Break cycle with abstraction layer
- Apply dependency inversion at weakest link
- Restructure to eliminate circular reference

### Temporal Coupling

**Issue**: High-frequency runtime calls between components
**Impact**: Performance degradation if separated
**Remediation**:
- Keep in same service if performance critical
- Implement caching layer
- Use event-driven architecture

## Best Practices

### Analyzing Coupling

1. **Run on Complete Codebase**: Ensure all dependencies captured
2. **Include Runtime Data**: Temporal coupling reveals hidden dependencies
3. **Focus on Hotspots**: Address high-severity issues first
4. **Track Over Time**: Monitor coupling trends during refactoring

### Interpreting Metrics

1. **Context Matters**: Infrastructure components naturally have high Ca
2. **Balance Needed**: Some coupling is necessary and acceptable
3. **Prioritize by Risk**: Focus on high risk scores and hotspots
4. **Consider Business Impact**: Technical coupling vs business coupling

### Migration Planning

1. **Start with Low Coupling**: Extract loosely coupled components first
2. **Break Circular Dependencies**: Essential before microservices extraction
3. **Address Hotspots**: Refactor problem areas before migration
4. **Monitor Progress**: Use coupling metrics to track improvements

## Testing

```bash
# Run coupling analyzer tests
cd /workspace/tools
python -m pytest tests/integration/test_coupling_analyzer.py -v
```

**Test Coverage**: 22 tests covering:
- Component coupling calculation
- Instability and distance metrics
- Coupling density
- Hotspot identification
- Circular dependency detection
- Migration complexity scoring
- Export functionality

## References

- **Robert C. Martin**: "Design Principles and Design Patterns" (Stability Metrics)
- **Dependency Extractor**: `/workspace/tools/src/omega_analysis/analysis/static/dependency_extractor.py`
- **Tests**: `/workspace/tools/tests/integration/test_coupling_analyzer.py`
- **Epic 1.1 PRD**: `/workspace/prds/epic-1.1-system-discovery-baseline-assessment.md`
