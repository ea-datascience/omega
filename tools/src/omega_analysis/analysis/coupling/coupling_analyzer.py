"""Coupling metrics analyzer for migration complexity assessment.

Calculates comprehensive coupling metrics from static and runtime analysis:
- Afferent/Efferent coupling
- Instability index
- Abstractness
- Distance from main sequence
- Coupling density
- Temporal coupling from runtime patterns
- Coupling hotspots identification
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import json

logger = logging.getLogger(__name__)


class CouplingType(Enum):
    """Type of coupling between components."""
    STRUCTURAL = "structural"  # Static code dependencies
    BEHAVIORAL = "behavioral"  # Runtime call patterns
    DATA = "data"  # Shared data access
    TEMPORAL = "temporal"  # Co-change patterns
    SEMANTIC = "semantic"  # Logical/domain coupling


class CouplingStrength(Enum):
    """Strength classification of coupling."""
    VERY_WEAK = "very_weak"  # Score 0-20
    WEAK = "weak"  # Score 20-40
    MODERATE = "moderate"  # Score 40-60
    STRONG = "strong"  # Score 60-80
    VERY_STRONG = "very_strong"  # Score 80-100


@dataclass
class ComponentCoupling:
    """Coupling metrics for a single component."""
    component_name: str
    afferent_coupling: int  # Ca: number of components depending on this
    efferent_coupling: int  # Ce: number of components this depends on
    instability: float  # I = Ce / (Ca + Ce)
    abstractness: float  # A = abstract_classes / total_classes
    distance_from_main_sequence: float  # D = |A + I - 1|
    incoming_dependencies: List[str] = field(default_factory=list)
    outgoing_dependencies: List[str] = field(default_factory=list)
    coupling_strength: CouplingStrength = CouplingStrength.MODERATE
    is_hotspot: bool = False
    risk_score: float = 0.0


@dataclass
class TemporalCoupling:
    """Temporal coupling from runtime call patterns."""
    source_component: str
    target_component: str
    call_frequency: int  # Number of calls observed
    calls_per_second: float  # Average call rate
    temporal_correlation: float  # How often called together (0-1)
    latency_p95: float  # P95 latency in ms
    error_rate: float  # Error rate for these calls
    coupling_strength: CouplingStrength = CouplingStrength.MODERATE


@dataclass
class CouplingHotspot:
    """Identifies coupling hotspots - areas with problematic coupling."""
    hotspot_id: str
    components: List[str]
    coupling_type: CouplingType
    severity: str  # critical, high, medium, low
    description: str
    metrics: Dict[str, Any]
    impact_on_migration: str
    remediation_suggestions: List[str]
    effort_estimate_days: int


@dataclass
class CouplingMetrics:
    """Complete coupling metrics analysis results."""
    analysis_id: str
    application_name: str
    analyzed_at: datetime
    
    # Component-level metrics
    component_coupling: Dict[str, ComponentCoupling]  # component -> metrics
    
    # Package-level metrics (for languages with packages)
    package_instability: Dict[str, float]  # package -> instability
    package_abstractness: Dict[str, float]  # package -> abstractness
    package_distance: Dict[str, float]  # package -> distance from main sequence
    
    # Overall metrics
    average_instability: float
    average_abstractness: float
    average_distance: float
    coupling_density: float  # Percentage of possible couplings that exist
    max_afferent_coupling: int
    max_efferent_coupling: int
    
    # Temporal coupling from runtime
    temporal_couplings: List[TemporalCoupling] = field(default_factory=list)
    
    # Hotspot identification
    coupling_hotspots: List[CouplingHotspot] = field(default_factory=list)
    
    # Circular dependencies
    circular_dependency_count: int = 0
    circular_dependency_chains: List[List[str]] = field(default_factory=list)
    
    # Classification
    overall_coupling_strength: CouplingStrength = CouplingStrength.MODERATE
    migration_complexity_score: float = 50.0  # 0-100
    
    # Metadata
    total_components: int = 0
    total_dependencies: int = 0
    metrics_metadata: Dict[str, Any] = field(default_factory=dict)


class CouplingAnalyzer:
    """Analyzes coupling metrics from static and runtime analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize coupling analyzer.
        
        Args:
            config: Optional configuration for thresholds and weights
        """
        self.config = config or self._default_config()
        logger.info("Coupling analyzer initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for coupling analysis."""
        return {
            "thresholds": {
                "high_afferent_coupling": 10,  # Components with >10 dependents
                "high_efferent_coupling": 15,  # Components with >15 dependencies
                "high_instability": 0.8,  # Instability > 0.8 is unstable
                "high_distance": 0.5,  # Distance > 0.5 is problematic
                "temporal_coupling_threshold": 100,  # >100 calls/sec is high
                "circular_dependency_severity": "high"
            },
            "weights": {
                "afferent_weight": 0.25,
                "efferent_weight": 0.25,
                "instability_weight": 0.20,
                "distance_weight": 0.15,
                "temporal_weight": 0.10,
                "circular_weight": 0.05
            },
            "hotspot_detection": {
                "min_coupling_for_hotspot": 5,
                "min_temporal_calls": 1000
            }
        }
    
    def analyze_coupling(
        self,
        application_name: str,
        static_results: Optional[Dict[str, Any]] = None,
        runtime_results: Optional[Any] = None,
        dependency_graph: Optional[Any] = None
    ) -> CouplingMetrics:
        """Perform comprehensive coupling analysis.
        
        Args:
            application_name: Name of the application
            static_results: Static analysis results with dependency info
            runtime_results: Runtime analysis results with call patterns
            dependency_graph: Dependency graph from static analysis
            
        Returns:
            CouplingMetrics with complete coupling analysis
        """
        logger.info(f"Analyzing coupling for: {application_name}")
        
        analysis_id = f"coupling_{application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract component coupling from static analysis
        component_coupling = self._calculate_component_coupling(
            static_results, dependency_graph
        )
        
        # Calculate package-level metrics
        package_metrics = self._calculate_package_metrics(
            static_results, dependency_graph
        )
        
        # Analyze temporal coupling from runtime
        temporal_couplings = self._analyze_temporal_coupling(runtime_results)
        
        # Identify circular dependencies
        circular_deps, circular_chains = self._identify_circular_dependencies(
            static_results, dependency_graph
        )
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(
            component_coupling, package_metrics
        )
        
        # Identify coupling hotspots
        hotspots = self._identify_coupling_hotspots(
            component_coupling,
            temporal_couplings,
            circular_chains
        )
        
        # Calculate migration complexity
        complexity_score = self._calculate_migration_complexity(
            component_coupling,
            temporal_couplings,
            circular_deps,
            overall_metrics
        )
        
        # Classify overall coupling strength
        coupling_strength = self._classify_coupling_strength(complexity_score)
        
        # Build complete metrics
        coupling_metrics = CouplingMetrics(
            analysis_id=analysis_id,
            application_name=application_name,
            analyzed_at=datetime.now(),
            component_coupling=component_coupling,
            package_instability=package_metrics.get("instability", {}),
            package_abstractness=package_metrics.get("abstractness", {}),
            package_distance=package_metrics.get("distance", {}),
            average_instability=overall_metrics.get("avg_instability", 0.5),
            average_abstractness=overall_metrics.get("avg_abstractness", 0.5),
            average_distance=overall_metrics.get("avg_distance", 0.5),
            coupling_density=overall_metrics.get("coupling_density", 0.0),
            max_afferent_coupling=overall_metrics.get("max_afferent", 0),
            max_efferent_coupling=overall_metrics.get("max_efferent", 0),
            temporal_couplings=temporal_couplings,
            coupling_hotspots=hotspots,
            circular_dependency_count=circular_deps,
            circular_dependency_chains=circular_chains,
            overall_coupling_strength=coupling_strength,
            migration_complexity_score=complexity_score,
            total_components=len(component_coupling),
            total_dependencies=overall_metrics.get("total_dependencies", 0),
            metrics_metadata={
                "static_analysis_available": static_results is not None,
                "runtime_analysis_available": runtime_results is not None,
                "dependency_graph_available": dependency_graph is not None,
                "config_used": self.config
            }
        )
        
        logger.info(f"Coupling analysis complete: {len(component_coupling)} components analyzed")
        return coupling_metrics
    
    def _calculate_component_coupling(
        self,
        static_results: Optional[Dict[str, Any]],
        dependency_graph: Optional[Any]
    ) -> Dict[str, ComponentCoupling]:
        """Calculate coupling metrics for each component."""
        component_coupling = {}
        
        # Try to extract from static results
        if static_results and static_results.get("dependency_analysis"):
            dep_analysis = static_results["dependency_analysis"]
            internal_deps = dep_analysis.get("internal_dependencies", {})
            
            # Calculate afferent and efferent for each component
            all_components = set(internal_deps.keys())
            for target in internal_deps.values():
                if isinstance(target, (list, set)):
                    all_components.update(target)
            
            for component in all_components:
                # Efferent: outgoing dependencies
                efferent = len(internal_deps.get(component, set()))
                efferent_list = list(internal_deps.get(component, set()))
                
                # Afferent: incoming dependencies
                afferent = sum(1 for deps in internal_deps.values() 
                             if component in deps)
                afferent_list = [c for c, deps in internal_deps.items() 
                               if component in deps]
                
                # Calculate instability
                total = afferent + efferent
                instability = efferent / total if total > 0 else 0.0
                
                # Abstractness (default to 0 if not available)
                abstractness = 0.0
                if static_results.get("code_metrics"):
                    component_metrics = static_results["code_metrics"].get(component, {})
                    if component_metrics.get("is_abstract") or component_metrics.get("is_interface"):
                        abstractness = 1.0
                
                # Distance from main sequence
                distance = abs(abstractness + instability - 1.0)
                
                # Risk score based on coupling
                risk_score = self._calculate_component_risk(
                    afferent, efferent, instability, distance
                )
                
                # Coupling strength classification
                strength = self._classify_component_coupling_strength(
                    afferent, efferent
                )
                
                # Check if hotspot
                is_hotspot = (
                    afferent > self.config["thresholds"]["high_afferent_coupling"] or
                    efferent > self.config["thresholds"]["high_efferent_coupling"] or
                    distance > self.config["thresholds"]["high_distance"]
                )
                
                component_coupling[component] = ComponentCoupling(
                    component_name=component,
                    afferent_coupling=afferent,
                    efferent_coupling=efferent,
                    instability=round(instability, 3),
                    abstractness=round(abstractness, 3),
                    distance_from_main_sequence=round(distance, 3),
                    incoming_dependencies=afferent_list,
                    outgoing_dependencies=efferent_list,
                    coupling_strength=strength,
                    is_hotspot=is_hotspot,
                    risk_score=round(risk_score, 2)
                )
        
        # Try to extract from dependency graph
        elif dependency_graph:
            if hasattr(dependency_graph, 'internal_dependencies'):
                internal_deps = dependency_graph.internal_dependencies
                
                all_components = set(internal_deps.keys())
                for deps in internal_deps.values():
                    all_components.update(deps)
                
                for component in all_components:
                    efferent = len(internal_deps.get(component, set()))
                    efferent_list = list(internal_deps.get(component, set()))
                    
                    afferent = sum(1 for deps in internal_deps.values() 
                                 if component in deps)
                    afferent_list = [c for c, deps in internal_deps.items() 
                                   if component in deps]
                    
                    total = afferent + efferent
                    instability = efferent / total if total > 0 else 0.0
                    abstractness = 0.0
                    distance = abs(abstractness + instability - 1.0)
                    
                    risk_score = self._calculate_component_risk(
                        afferent, efferent, instability, distance
                    )
                    
                    strength = self._classify_component_coupling_strength(
                        afferent, efferent
                    )
                    
                    is_hotspot = (
                        afferent > self.config["thresholds"]["high_afferent_coupling"] or
                        efferent > self.config["thresholds"]["high_efferent_coupling"]
                    )
                    
                    component_coupling[component] = ComponentCoupling(
                        component_name=component,
                        afferent_coupling=afferent,
                        efferent_coupling=efferent,
                        instability=round(instability, 3),
                        abstractness=round(abstractness, 3),
                        distance_from_main_sequence=round(distance, 3),
                        incoming_dependencies=afferent_list,
                        outgoing_dependencies=efferent_list,
                        coupling_strength=strength,
                        is_hotspot=is_hotspot,
                        risk_score=round(risk_score, 2)
                    )
        
        return component_coupling
    
    def _calculate_package_metrics(
        self,
        static_results: Optional[Dict[str, Any]],
        dependency_graph: Optional[Any]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate package-level coupling metrics."""
        metrics = {
            "instability": {},
            "abstractness": {},
            "distance": {}
        }
        
        # Try to use existing metrics from dependency analysis
        if static_results and static_results.get("dependency_metrics"):
            dep_metrics = static_results["dependency_metrics"]
            metrics["instability"] = dep_metrics.get("instability", {})
            metrics["abstractness"] = dep_metrics.get("abstractness", {})
            metrics["distance"] = dep_metrics.get("distance_from_main_sequence", {})
        
        # Or extract from dependency graph
        elif dependency_graph and hasattr(dependency_graph, 'package_dependencies'):
            package_deps = dependency_graph.package_dependencies
            
            # Calculate instability for each package
            for package in package_deps:
                efferent = len(package_deps.get(package, set()))
                afferent = sum(1 for deps in package_deps.values() 
                             if package in deps)
                total = afferent + efferent
                instability = efferent / total if total > 0 else 0.0
                metrics["instability"][package] = round(instability, 3)
                
                # Default abstractness and distance
                abstractness = 0.5  # Default middle value
                metrics["abstractness"][package] = abstractness
                metrics["distance"][package] = round(abs(abstractness + instability - 1.0), 3)
        
        return metrics
    
    def _analyze_temporal_coupling(
        self,
        runtime_results: Optional[Any]
    ) -> List[TemporalCoupling]:
        """Analyze temporal coupling from runtime call patterns."""
        temporal_couplings = []
        
        if not runtime_results:
            return temporal_couplings
        
        # Extract call patterns from runtime results
        if hasattr(runtime_results, 'baseline'):
            baseline = runtime_results.baseline
            
            # Look for trace data or span data
            if hasattr(runtime_results, 'trace_analysis'):
                traces = runtime_results.trace_analysis
                
                # Analyze call frequency between components
                call_patterns = self._extract_call_patterns(traces)
                
                for (source, target), metrics in call_patterns.items():
                    calls_per_sec = metrics.get("calls_per_second", 0.0)
                    
                    # Classify coupling strength based on call frequency
                    if calls_per_sec > 100:
                        strength = CouplingStrength.VERY_STRONG
                    elif calls_per_sec > 50:
                        strength = CouplingStrength.STRONG
                    elif calls_per_sec > 10:
                        strength = CouplingStrength.MODERATE
                    elif calls_per_sec > 1:
                        strength = CouplingStrength.WEAK
                    else:
                        strength = CouplingStrength.VERY_WEAK
                    
                    temporal_couplings.append(TemporalCoupling(
                        source_component=source,
                        target_component=target,
                        call_frequency=metrics.get("total_calls", 0),
                        calls_per_second=calls_per_sec,
                        temporal_correlation=metrics.get("correlation", 0.8),
                        latency_p95=metrics.get("p95_latency", 0.0),
                        error_rate=metrics.get("error_rate", 0.0),
                        coupling_strength=strength
                    ))
        
        return temporal_couplings
    
    def _extract_call_patterns(self, traces: Any) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Extract call patterns from trace data."""
        call_patterns = {}
        
        # This would analyze actual trace data
        # For now, return empty - will be populated when runtime tracing is available
        
        return call_patterns
    
    def _identify_circular_dependencies(
        self,
        static_results: Optional[Dict[str, Any]],
        dependency_graph: Optional[Any]
    ) -> Tuple[int, List[List[str]]]:
        """Identify circular dependencies."""
        circular_chains = []
        
        # Try static results first
        if static_results and static_results.get("dependency_analysis"):
            dep_analysis = static_results["dependency_analysis"]
            circular_chains = dep_analysis.get("circular_dependencies", [])
        
        # Or from dependency graph
        elif dependency_graph and hasattr(dependency_graph, 'circular_dependencies'):
            circular_chains = dependency_graph.circular_dependencies
        
        return len(circular_chains), circular_chains
    
    def _calculate_overall_metrics(
        self,
        component_coupling: Dict[str, ComponentCoupling],
        package_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Calculate overall coupling metrics."""
        if not component_coupling:
            return {
                "avg_instability": 0.5,
                "avg_abstractness": 0.5,
                "avg_distance": 0.5,
                "coupling_density": 0.0,
                "max_afferent": 0,
                "max_efferent": 0,
                "total_dependencies": 0
            }
        
        # Average metrics across components
        instabilities = [c.instability for c in component_coupling.values()]
        abstractnesses = [c.abstractness for c in component_coupling.values()]
        distances = [c.distance_from_main_sequence for c in component_coupling.values()]
        
        avg_instability = sum(instabilities) / len(instabilities) if instabilities else 0.5
        avg_abstractness = sum(abstractnesses) / len(abstractnesses) if abstractnesses else 0.5
        avg_distance = sum(distances) / len(distances) if distances else 0.5
        
        # Max coupling values
        max_afferent = max((c.afferent_coupling for c in component_coupling.values()), default=0)
        max_efferent = max((c.efferent_coupling for c in component_coupling.values()), default=0)
        
        # Total dependencies
        total_dependencies = sum(c.efferent_coupling for c in component_coupling.values())
        
        # Coupling density (percentage of possible couplings)
        n = len(component_coupling)
        max_possible = n * (n - 1)  # Directed graph
        coupling_density = total_dependencies / max_possible if max_possible > 0 else 0.0
        
        return {
            "avg_instability": round(avg_instability, 3),
            "avg_abstractness": round(avg_abstractness, 3),
            "avg_distance": round(avg_distance, 3),
            "coupling_density": round(coupling_density, 4),
            "max_afferent": max_afferent,
            "max_efferent": max_efferent,
            "total_dependencies": total_dependencies
        }
    
    def _identify_coupling_hotspots(
        self,
        component_coupling: Dict[str, ComponentCoupling],
        temporal_couplings: List[TemporalCoupling],
        circular_chains: List[List[str]]
    ) -> List[CouplingHotspot]:
        """Identify coupling hotspots that pose migration risks."""
        hotspots = []
        hotspot_id = 1
        
        # High afferent coupling hotspots (many dependents)
        high_afferent = [c for c in component_coupling.values() 
                        if c.afferent_coupling > self.config["thresholds"]["high_afferent_coupling"]]
        
        for component in high_afferent:
            hotspots.append(CouplingHotspot(
                hotspot_id=f"afferent_{hotspot_id}",
                components=[component.component_name] + component.incoming_dependencies[:5],
                coupling_type=CouplingType.STRUCTURAL,
                severity="high",
                description=f"{component.component_name} has {component.afferent_coupling} incoming dependencies",
                metrics={
                    "afferent_coupling": component.afferent_coupling,
                    "risk_score": component.risk_score
                },
                impact_on_migration="Many components depend on this - changes will have wide impact",
                remediation_suggestions=[
                    "Consider extracting interface to decouple dependents",
                    "Apply dependency inversion principle",
                    "Split into smaller, focused components"
                ],
                effort_estimate_days=int(component.afferent_coupling * 0.5)
            ))
            hotspot_id += 1
        
        # High efferent coupling hotspots (many dependencies)
        high_efferent = [c for c in component_coupling.values() 
                        if c.efferent_coupling > self.config["thresholds"]["high_efferent_coupling"]]
        
        for component in high_efferent:
            hotspots.append(CouplingHotspot(
                hotspot_id=f"efferent_{hotspot_id}",
                components=[component.component_name] + component.outgoing_dependencies[:5],
                coupling_type=CouplingType.STRUCTURAL,
                severity="medium",
                description=f"{component.component_name} depends on {component.efferent_coupling} components",
                metrics={
                    "efferent_coupling": component.efferent_coupling,
                    "instability": component.instability
                },
                impact_on_migration="Component is highly unstable - changes in dependencies will impact it",
                remediation_suggestions=[
                    "Reduce dependencies through refactoring",
                    "Apply facade pattern to group related dependencies",
                    "Consider moving to separate microservice"
                ],
                effort_estimate_days=int(component.efferent_coupling * 0.3)
            ))
            hotspot_id += 1
        
        # Circular dependency hotspots
        for chain in circular_chains:
            hotspots.append(CouplingHotspot(
                hotspot_id=f"circular_{hotspot_id}",
                components=chain,
                coupling_type=CouplingType.STRUCTURAL,
                severity="high",
                description=f"Circular dependency chain: {' → '.join(chain[:4])}...",
                metrics={
                    "chain_length": len(chain)
                },
                impact_on_migration="Circular dependencies prevent clean service boundaries",
                remediation_suggestions=[
                    "Break cycle by introducing abstraction layer",
                    "Apply dependency inversion at weakest link",
                    "Restructure to eliminate circular reference"
                ],
                effort_estimate_days=len(chain) * 2
            ))
            hotspot_id += 1
        
        # Temporal coupling hotspots
        high_temporal = [tc for tc in temporal_couplings 
                        if tc.calls_per_second > self.config["thresholds"]["temporal_coupling_threshold"]]
        
        for tc in high_temporal:
            hotspots.append(CouplingHotspot(
                hotspot_id=f"temporal_{hotspot_id}",
                components=[tc.source_component, tc.target_component],
                coupling_type=CouplingType.TEMPORAL,
                severity="medium",
                description=f"High frequency calls: {tc.source_component} → {tc.target_component}",
                metrics={
                    "calls_per_second": tc.calls_per_second,
                    "latency_p95": tc.latency_p95,
                    "error_rate": tc.error_rate
                },
                impact_on_migration="High call frequency may cause performance issues if separated",
                remediation_suggestions=[
                    "Consider keeping in same service for performance",
                    "Implement caching layer to reduce calls",
                    "Use event-driven architecture instead of synchronous calls"
                ],
                effort_estimate_days=5
            ))
            hotspot_id += 1
        
        return hotspots
    
    def _calculate_migration_complexity(
        self,
        component_coupling: Dict[str, ComponentCoupling],
        temporal_couplings: List[TemporalCoupling],
        circular_deps_count: int,
        overall_metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall migration complexity score (0-100)."""
        weights = self.config["weights"]
        
        # Afferent coupling score (normalized)
        max_afferent = overall_metrics.get("max_afferent", 0)
        afferent_score = min(max_afferent * 8, 100)  # 12+ afferent = max score
        
        # Efferent coupling score (normalized)
        max_efferent = overall_metrics.get("max_efferent", 0)
        efferent_score = min(max_efferent * 6, 100)  # 16+ efferent = max score
        
        # Instability score (higher instability = higher complexity)
        instability_score = overall_metrics.get("avg_instability", 0.5) * 100
        
        # Distance score (higher distance = higher complexity)
        distance_score = overall_metrics.get("avg_distance", 0.5) * 100
        
        # Temporal coupling score
        temporal_score = min(len(temporal_couplings) * 5, 100)
        
        # Circular dependency score
        circular_score = min(circular_deps_count * 20, 100)
        
        # Weighted average
        complexity = (
            afferent_score * weights["afferent_weight"] +
            efferent_score * weights["efferent_weight"] +
            instability_score * weights["instability_weight"] +
            distance_score * weights["distance_weight"] +
            temporal_score * weights["temporal_weight"] +
            circular_score * weights["circular_weight"]
        )
        
        return min(complexity, 100.0)
    
    def _classify_coupling_strength(self, complexity_score: float) -> CouplingStrength:
        """Classify overall coupling strength."""
        if complexity_score >= 80:
            return CouplingStrength.VERY_STRONG
        elif complexity_score >= 60:
            return CouplingStrength.STRONG
        elif complexity_score >= 40:
            return CouplingStrength.MODERATE
        elif complexity_score >= 20:
            return CouplingStrength.WEAK
        else:
            return CouplingStrength.VERY_WEAK
    
    def _calculate_component_risk(
        self,
        afferent: int,
        efferent: int,
        instability: float,
        distance: float
    ) -> float:
        """Calculate risk score for a component (0-100)."""
        # High afferent = high impact if changed
        afferent_risk = min(afferent * 5, 50)
        
        # High efferent = high fragility
        efferent_risk = min(efferent * 3, 30)
        
        # High distance = architectural violation
        distance_risk = distance * 20
        
        return afferent_risk + efferent_risk + distance_risk
    
    def _classify_component_coupling_strength(
        self,
        afferent: int,
        efferent: int
    ) -> CouplingStrength:
        """Classify coupling strength for a component."""
        total = afferent + efferent
        
        if total >= 40:
            return CouplingStrength.VERY_STRONG
        elif total >= 25:
            return CouplingStrength.STRONG
        elif total >= 15:
            return CouplingStrength.MODERATE
        elif total >= 5:
            return CouplingStrength.WEAK
        else:
            return CouplingStrength.VERY_WEAK
    
    def export_metrics(
        self,
        metrics: CouplingMetrics,
        output_path: Path
    ) -> None:
        """Export coupling metrics to JSON file.
        
        Args:
            metrics: Coupling metrics to export
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        export_data = {
            "analysis_id": metrics.analysis_id,
            "application_name": metrics.application_name,
            "analyzed_at": metrics.analyzed_at.isoformat(),
            "component_coupling": {
                name: {
                    "component_name": cc.component_name,
                    "afferent_coupling": cc.afferent_coupling,
                    "efferent_coupling": cc.efferent_coupling,
                    "instability": cc.instability,
                    "abstractness": cc.abstractness,
                    "distance_from_main_sequence": cc.distance_from_main_sequence,
                    "incoming_dependencies": cc.incoming_dependencies,
                    "outgoing_dependencies": cc.outgoing_dependencies,
                    "coupling_strength": cc.coupling_strength.value,
                    "is_hotspot": cc.is_hotspot,
                    "risk_score": cc.risk_score
                }
                for name, cc in metrics.component_coupling.items()
            },
            "package_metrics": {
                "instability": metrics.package_instability,
                "abstractness": metrics.package_abstractness,
                "distance": metrics.package_distance
            },
            "overall_metrics": {
                "average_instability": metrics.average_instability,
                "average_abstractness": metrics.average_abstractness,
                "average_distance": metrics.average_distance,
                "coupling_density": metrics.coupling_density,
                "max_afferent_coupling": metrics.max_afferent_coupling,
                "max_efferent_coupling": metrics.max_efferent_coupling
            },
            "temporal_couplings": [
                {
                    "source_component": tc.source_component,
                    "target_component": tc.target_component,
                    "call_frequency": tc.call_frequency,
                    "calls_per_second": tc.calls_per_second,
                    "temporal_correlation": tc.temporal_correlation,
                    "latency_p95": tc.latency_p95,
                    "error_rate": tc.error_rate,
                    "coupling_strength": tc.coupling_strength.value
                }
                for tc in metrics.temporal_couplings
            ],
            "coupling_hotspots": [
                {
                    "hotspot_id": h.hotspot_id,
                    "components": h.components,
                    "coupling_type": h.coupling_type.value,
                    "severity": h.severity,
                    "description": h.description,
                    "metrics": h.metrics,
                    "impact_on_migration": h.impact_on_migration,
                    "remediation_suggestions": h.remediation_suggestions,
                    "effort_estimate_days": h.effort_estimate_days
                }
                for h in metrics.coupling_hotspots
            ],
            "circular_dependencies": {
                "count": metrics.circular_dependency_count,
                "chains": metrics.circular_dependency_chains
            },
            "summary": {
                "total_components": metrics.total_components,
                "total_dependencies": metrics.total_dependencies,
                "overall_coupling_strength": metrics.overall_coupling_strength.value,
                "migration_complexity_score": metrics.migration_complexity_score
            },
            "metadata": metrics.metrics_metadata
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Coupling metrics exported to: {output_path}")


# CLI interface for standalone testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze coupling metrics')
    parser.add_argument('--application-name', required=True, help='Application name')
    parser.add_argument('--output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Run basic analysis
    analyzer = CouplingAnalyzer()
    metrics = analyzer.analyze_coupling(
        application_name=args.application_name
    )
    
    # Print summary
    print(f"\nCoupling Analysis: {metrics.application_name}")
    print(f"="*60)
    print(f"Total Components: {metrics.total_components}")
    print(f"Total Dependencies: {metrics.total_dependencies}")
    print(f"Coupling Density: {metrics.coupling_density:.2%}")
    print(f"Average Instability: {metrics.average_instability:.3f}")
    print(f"Average Distance: {metrics.average_distance:.3f}")
    print(f"Coupling Strength: {metrics.overall_coupling_strength.value}")
    print(f"Migration Complexity: {metrics.migration_complexity_score:.1f}/100")
    print(f"Coupling Hotspots: {len(metrics.coupling_hotspots)}")
    print(f"Circular Dependencies: {metrics.circular_dependency_count}")
    
    # Export if requested
    if args.output:
        analyzer.export_metrics(metrics, Path(args.output))
