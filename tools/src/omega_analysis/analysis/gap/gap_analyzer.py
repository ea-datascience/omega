"""Gap analysis comparison engine for migration readiness assessment.

This module compares static and runtime analysis results to identify discrepancies,
calculate migration complexity, and assess readiness for microservices migration.

Per Epic 1.1 Milestone 2.1: Automated comparison between static and runtime analysis
findings with discrepancy identification, coupling quantification, and complexity scoring.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from ..static.appcat import AppCATResults, CloudReadinessAssessment
from ...services.orchestration.runtime_analyzer import (
    RuntimeAnalysisResults, PerformanceBaseline
)

logger = logging.getLogger(__name__)


class GapCategory(Enum):
    """Categories of gaps identified in analysis."""
    ARCHITECTURAL = "architectural"
    PERFORMANCE = "performance"
    DEPENDENCY = "dependency"
    TECHNOLOGY = "technology"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DATA_ACCESS = "data_access"


class DiscrepancySeverity(Enum):
    """Severity levels for discrepancies."""
    CRITICAL = "critical"  # Blocks migration
    HIGH = "high"          # Requires significant refactoring
    MEDIUM = "medium"      # Needs attention but manageable
    LOW = "low"            # Minor issue, can be addressed during migration
    INFO = "info"          # Informational, no action needed


@dataclass
class DiscrepancyFinding:
    """Represents a discrepancy between static and runtime analysis."""
    finding_id: str
    category: GapCategory
    severity: DiscrepancySeverity
    title: str
    description: str
    
    # Evidence from analyses
    static_evidence: Dict[str, Any]
    runtime_evidence: Dict[str, Any]
    
    # Impact assessment
    migration_impact: str
    remediation_effort: str  # Low, Medium, High, Critical
    recommended_action: str
    
    # Metadata
    confidence_score: float  # 0.0-1.0
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplexityScore:
    """Migration complexity scoring."""
    overall_score: float  # 0.0-100.0 (higher = more complex)
    
    # Component scores
    architectural_complexity: float
    coupling_complexity: float
    performance_complexity: float
    technology_complexity: float
    data_complexity: float
    
    # Breakdown
    complexity_factors: List[str]
    simplification_opportunities: List[str]
    
    # Risk categorization
    complexity_level: str  # Low, Medium, High, Very High
    estimated_effort_weeks: int


@dataclass
class MigrationReadinessAssessment:
    """Overall migration readiness assessment."""
    readiness_score: float  # 0.0-100.0 (higher = more ready)
    readiness_category: str  # Ready, Nearly Ready, Needs Work, Not Ready
    
    # Sub-scores
    technical_readiness: float
    architectural_readiness: float
    performance_readiness: float
    organizational_readiness: float
    
    # Go/No-Go decision support
    go_no_go_recommendation: str  # GO, CONDITIONAL GO, NO GO
    go_no_go_rationale: str
    
    # Blockers and prerequisites
    critical_blockers: List[str]
    prerequisites: List[str]
    
    # Roadmap
    recommended_approach: str  # Big Bang, Strangler Fig, Parallel Run
    estimated_timeline_months: int
    confidence_level: float  # 0.0-1.0


@dataclass
class GapAnalysisResult:
    """Complete gap analysis results."""
    analysis_id: str
    application_name: str
    analysis_timestamp: datetime
    
    # Input analysis results
    static_analysis_id: Optional[str]
    runtime_analysis_id: Optional[str]
    
    # Findings
    discrepancies: List[DiscrepancyFinding]
    discrepancy_summary: Dict[str, int]  # By category and severity
    
    # Complexity and readiness
    complexity_score: ComplexityScore
    readiness_assessment: MigrationReadinessAssessment
    
    # Gap metrics
    gap_metrics: Dict[str, Any]
    
    # Metadata
    comparison_config: Dict[str, Any]
    validation_status: str  # passed, failed, warnings


class GapAnalyzer:
    """Analyzes gaps between static and runtime analysis results."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize gap analyzer.
        
        Args:
            config: Optional configuration for gap analysis thresholds and weights
        """
        self.config = config or self._default_config()
        logger.info("Gap analyzer initialized with configuration")
        
    def analyze_gaps(
        self,
        application_name: str,
        static_results: Optional[Dict[str, Any]] = None,
        runtime_results: Optional[RuntimeAnalysisResults] = None,
        appcat_results: Optional[AppCATResults] = None,
        analysis_id: Optional[str] = None
    ) -> GapAnalysisResult:
        """Perform comprehensive gap analysis.
        
        Args:
            application_name: Name of application being analyzed
            static_results: Static analysis results (from StaticAnalysisOrchestrator)
            runtime_results: Runtime analysis results (from RuntimeAnalysisOrchestrator)
            appcat_results: AppCAT assessment results
            analysis_id: Optional analysis identifier
            
        Returns:
            GapAnalysisResult with complete gap analysis
        """
        logger.info(f"Starting gap analysis for: {application_name}")
        
        if analysis_id is None:
            analysis_id = f"gap_{application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        # Identify discrepancies
        logger.info("Identifying discrepancies between static and runtime analysis...")
        discrepancies = self._identify_discrepancies(
            static_results, runtime_results, appcat_results
        )
        
        # Calculate complexity score
        logger.info("Calculating migration complexity score...")
        complexity_score = self._calculate_complexity_score(
            static_results, runtime_results, appcat_results, discrepancies
        )
        
        # Assess migration readiness
        logger.info("Assessing migration readiness...")
        readiness_assessment = self._assess_migration_readiness(
            static_results, runtime_results, appcat_results, 
            complexity_score, discrepancies
        )
        
        # Calculate gap metrics
        logger.info("Calculating gap metrics...")
        gap_metrics = self._calculate_gap_metrics(
            discrepancies, complexity_score, readiness_assessment
        )
        
        # Generate summary
        discrepancy_summary = self._summarize_discrepancies(discrepancies)
        
        # Determine validation status
        validation_status = self._validate_results(
            readiness_assessment, complexity_score, discrepancies
        )
        
        result = GapAnalysisResult(
            analysis_id=analysis_id,
            application_name=application_name,
            analysis_timestamp=datetime.now(),
            static_analysis_id=static_results.get("analysis_id") if static_results else None,
            runtime_analysis_id=runtime_results.analysis_id if runtime_results else None,
            discrepancies=discrepancies,
            discrepancy_summary=discrepancy_summary,
            complexity_score=complexity_score,
            readiness_assessment=readiness_assessment,
            gap_metrics=gap_metrics,
            comparison_config=self.config,
            validation_status=validation_status
        )
        
        logger.info(f"Gap analysis completed: {analysis_id}")
        logger.info(f"  Discrepancies found: {len(discrepancies)}")
        logger.info(f"  Complexity score: {complexity_score.overall_score:.1f}/100")
        logger.info(f"  Readiness score: {readiness_assessment.readiness_score:.1f}/100")
        logger.info(f"  Recommendation: {readiness_assessment.go_no_go_recommendation}")
        
        return result
        
    def _identify_discrepancies(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults],
        appcat_results: Optional[AppCATResults]
    ) -> List[DiscrepancyFinding]:
        """Identify discrepancies between static and runtime analysis."""
        discrepancies = []
        
        # Architectural discrepancies
        discrepancies.extend(
            self._compare_architecture(static_results, runtime_results, appcat_results)
        )
        
        # Performance discrepancies
        if runtime_results and runtime_results.baseline:
            discrepancies.extend(
                self._analyze_performance_gaps(runtime_results.baseline)
            )
            
        # Dependency discrepancies
        discrepancies.extend(
            self._compare_dependencies(static_results, runtime_results)
        )
        
        # Technology stack discrepancies
        if appcat_results:
            discrepancies.extend(
                self._analyze_technology_gaps(appcat_results)
            )
            
        # Security discrepancies
        if static_results and static_results.get("codeql_analysis"):
            discrepancies.extend(
                self._analyze_security_gaps(static_results["codeql_analysis"])
            )
            
        return discrepancies
        
    def _compare_architecture(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults],
        appcat_results: Optional[AppCATResults]
    ) -> List[DiscrepancyFinding]:
        """Compare architectural findings."""
        findings = []
        
        if appcat_results:
            # Check architectural patterns
            for pattern in appcat_results.architectural_patterns:
                if pattern.migration_readiness in ["Needs Refactoring", "Complex"]:
                    finding = DiscrepancyFinding(
                        finding_id=f"arch_{pattern.pattern_name.lower().replace(' ', '_')}",
                        category=GapCategory.ARCHITECTURAL,
                        severity=DiscrepancySeverity.HIGH if pattern.complexity_score > 7 else DiscrepancySeverity.MEDIUM,
                        title=f"{pattern.pattern_name} Requires Refactoring",
                        description=f"Pattern '{pattern.pattern_name}' (complexity {pattern.complexity_score}/10) needs significant refactoring for microservices migration.",
                        static_evidence={
                            "pattern_type": pattern.pattern_type,
                            "components": pattern.components,
                            "complexity_score": pattern.complexity_score,
                            "migration_readiness": pattern.migration_readiness
                        },
                        runtime_evidence={},
                        migration_impact=f"High coupling in {pattern.pattern_name} may require substantial decomposition effort",
                        remediation_effort="High" if pattern.complexity_score > 7 else "Medium",
                        recommended_action="; ".join(pattern.recommendations[:3]),
                        confidence_score=0.85
                    )
                    findings.append(finding)
                    
        return findings
        
    def _analyze_performance_gaps(
        self,
        baseline: PerformanceBaseline
    ) -> List[DiscrepancyFinding]:
        """Analyze performance baseline for potential issues."""
        findings = []
        
        # Check P95 response time
        p95_threshold = self.config["performance_thresholds"]["p95_response_time_ms"]
        if baseline.response_time_p95 > p95_threshold:
            severity = DiscrepancySeverity.HIGH if baseline.response_time_p95 > p95_threshold * 2 else DiscrepancySeverity.MEDIUM
            finding = DiscrepancyFinding(
                finding_id="perf_p95_high",
                category=GapCategory.PERFORMANCE,
                severity=severity,
                title="High P95 Response Time",
                description=f"P95 response time of {baseline.response_time_p95:.1f}ms exceeds threshold of {p95_threshold}ms",
                static_evidence={},
                runtime_evidence={
                    "p95_response_time": baseline.response_time_p95,
                    "p99_response_time": baseline.response_time_p99,
                    "mean_response_time": baseline.response_time_mean,
                    "throughput": baseline.requests_per_second
                },
                migration_impact="Performance issues may be magnified in distributed microservices architecture",
                remediation_effort="Medium",
                recommended_action="Optimize critical paths, add caching, review database queries",
                confidence_score=baseline.data_quality_score
            )
            findings.append(finding)
            
        # Check error rate
        error_threshold = self.config["performance_thresholds"]["error_rate"]
        if baseline.error_rate > error_threshold:
            finding = DiscrepancyFinding(
                finding_id="perf_error_rate_high",
                category=GapCategory.PERFORMANCE,
                severity=DiscrepancySeverity.HIGH,
                title="High Error Rate",
                description=f"Error rate of {baseline.error_rate:.1%} exceeds threshold of {error_threshold:.1%}",
                static_evidence={},
                runtime_evidence={
                    "error_rate": baseline.error_rate,
                    "errors_by_type": baseline.errors_by_type,
                    "total_requests": baseline.total_requests
                },
                migration_impact="High error rates indicate reliability issues that will affect migration",
                remediation_effort="High",
                recommended_action="Identify root causes, improve error handling, add circuit breakers",
                confidence_score=baseline.data_quality_score
            )
            findings.append(finding)
            
        return findings
        
    def _compare_dependencies(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults]
    ) -> List[DiscrepancyFinding]:
        """Compare dependency findings."""
        findings = []
        
        if static_results and static_results.get("dependency_analysis"):
            dep_analysis = static_results["dependency_analysis"]
            
            # Check for circular dependencies
            if dep_analysis.get("circular_dependencies"):
                finding = DiscrepancyFinding(
                    finding_id="dep_circular",
                    category=GapCategory.DEPENDENCY,
                    severity=DiscrepancySeverity.HIGH,
                    title="Circular Dependencies Detected",
                    description=f"Found {len(dep_analysis['circular_dependencies'])} circular dependency chains",
                    static_evidence=dep_analysis.get("circular_dependencies", {}),
                    runtime_evidence={},
                    migration_impact="Circular dependencies prevent clean service boundaries",
                    remediation_effort="High",
                    recommended_action="Break circular dependencies through dependency inversion or event-driven patterns",
                    confidence_score=0.90
                )
                findings.append(finding)
                
        return findings
        
    def _analyze_technology_gaps(
        self,
        appcat_results: AppCATResults
    ) -> List[DiscrepancyFinding]:
        """Analyze technology assessment for migration gaps."""
        findings = []
        
        for tech in appcat_results.technology_assessments:
            if tech.migration_effort in ["High", "Critical"]:
                finding = DiscrepancyFinding(
                    finding_id=f"tech_{tech.name.lower().replace(' ', '_')}",
                    category=GapCategory.TECHNOLOGY,
                    severity=DiscrepancySeverity.HIGH if tech.migration_effort == "Critical" else DiscrepancySeverity.MEDIUM,
                    title=f"{tech.name} Migration Challenge",
                    description=f"{tech.name} ({tech.version or 'unknown version'}) requires {tech.migration_effort.lower()} migration effort",
                    static_evidence={
                        "technology": tech.name,
                        "version": tech.version,
                        "assessment_status": tech.assessment_status,
                        "migration_effort": tech.migration_effort,
                        "notes": tech.notes
                    },
                    runtime_evidence={},
                    migration_impact=f"Technology {tech.name} may need replacement or significant updates",
                    remediation_effort=tech.migration_effort,
                    recommended_action=tech.recommended_alternative or "Review migration options",
                    confidence_score=tech.confidence_level
                )
                findings.append(finding)
                
        return findings
        
    def _analyze_security_gaps(
        self,
        codeql_results: Dict[str, Any]
    ) -> List[DiscrepancyFinding]:
        """Analyze security findings."""
        findings = []
        
        # Check for high-severity security issues
        security_issues = codeql_results.get("findings", [])
        high_severity_count = sum(1 for issue in security_issues if issue.get("severity") == "high")
        
        if high_severity_count > 0:
            finding = DiscrepancyFinding(
                finding_id="sec_high_severity",
                category=GapCategory.SECURITY,
                severity=DiscrepancySeverity.CRITICAL,
                title="High-Severity Security Issues",
                description=f"Found {high_severity_count} high-severity security issues requiring immediate attention",
                static_evidence={
                    "total_issues": len(security_issues),
                    "high_severity": high_severity_count,
                    "findings_summary": codeql_results.get("summary", {})
                },
                runtime_evidence={},
                migration_impact="Security issues must be resolved before migration to prevent vulnerabilities in new architecture",
                remediation_effort="High",
                recommended_action="Address all high-severity security findings before proceeding with migration",
                confidence_score=0.95
            )
            findings.append(finding)
            
        return findings
        
    def _calculate_complexity_score(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults],
        appcat_results: Optional[AppCATResults],
        discrepancies: List[DiscrepancyFinding]
    ) -> ComplexityScore:
        """Calculate overall migration complexity score."""
        
        # Calculate component scores
        arch_score = self._calculate_architectural_complexity(static_results, appcat_results)
        coupling_score = self._calculate_coupling_complexity(static_results, discrepancies)
        perf_score = self._calculate_performance_complexity(runtime_results)
        tech_score = self._calculate_technology_complexity(appcat_results)
        data_score = self._calculate_data_complexity(appcat_results)
        
        # Weighted average for overall score
        weights = self.config["complexity_weights"]
        overall_score = (
            arch_score * weights["architectural"] +
            coupling_score * weights["coupling"] +
            perf_score * weights["performance"] +
            tech_score * weights["technology"] +
            data_score * weights["data"]
        )
        
        # Identify complexity factors
        complexity_factors = self._identify_complexity_factors(
            arch_score, coupling_score, perf_score, tech_score, data_score, discrepancies
        )
        
        # Identify simplification opportunities
        simplification_opportunities = self._identify_simplifications(
            static_results, runtime_results, appcat_results
        )
        
        # Categorize complexity level
        if overall_score < 30:
            complexity_level = "Low"
            estimated_effort_weeks = 8
        elif overall_score < 50:
            complexity_level = "Medium"
            estimated_effort_weeks = 16
        elif overall_score < 70:
            complexity_level = "High"
            estimated_effort_weeks = 24
        else:
            complexity_level = "Very High"
            estimated_effort_weeks = 36
            
        return ComplexityScore(
            overall_score=round(overall_score, 1),
            architectural_complexity=round(arch_score, 1),
            coupling_complexity=round(coupling_score, 1),
            performance_complexity=round(perf_score, 1),
            technology_complexity=round(tech_score, 1),
            data_complexity=round(data_score, 1),
            complexity_factors=complexity_factors,
            simplification_opportunities=simplification_opportunities,
            complexity_level=complexity_level,
            estimated_effort_weeks=estimated_effort_weeks
        )
        
    def _calculate_architectural_complexity(
        self,
        static_results: Optional[Dict[str, Any]],
        appcat_results: Optional[AppCATResults]
    ) -> float:
        """Calculate architectural complexity (0-100)."""
        if not appcat_results:
            return 50.0  # Default moderate complexity
            
        # Average pattern complexity scores
        pattern_scores = [p.complexity_score * 10 for p in appcat_results.architectural_patterns]
        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 50.0
        
    def _calculate_coupling_complexity(
        self,
        static_results: Optional[Dict[str, Any]],
        discrepancies: List[DiscrepancyFinding]
    ) -> float:
        """Calculate coupling complexity (0-100)."""
        coupling_score = 50.0  # Base score
        
        # Increase for circular dependencies
        circular_deps = [d for d in discrepancies if d.finding_id == "dep_circular"]
        if circular_deps:
            coupling_score += 30.0
            
        return min(coupling_score, 100.0)
        
    def _calculate_performance_complexity(
        self,
        runtime_results: Optional[RuntimeAnalysisResults]
    ) -> float:
        """Calculate performance complexity (0-100)."""
        if not runtime_results or not runtime_results.baseline:
            return 50.0
            
        baseline = runtime_results.baseline
        perf_score = 0.0
        
        # Factor in P95 response time
        if baseline.response_time_p95 > 1000:  # >1s
            perf_score += 40.0
        elif baseline.response_time_p95 > 500:  # >500ms
            perf_score += 25.0
        elif baseline.response_time_p95 > 200:  # >200ms
            perf_score += 10.0
            
        # Factor in error rate
        if baseline.error_rate > 0.05:  # >5%
            perf_score += 30.0
        elif baseline.error_rate > 0.01:  # >1%
            perf_score += 15.0
            
        # Factor in data quality
        if baseline.data_quality_score < 0.7:
            perf_score += 10.0
            
        return min(perf_score, 100.0)
        
    def _calculate_technology_complexity(
        self,
        appcat_results: Optional[AppCATResults]
    ) -> float:
        """Calculate technology complexity (0-100)."""
        if not appcat_results:
            return 50.0
            
        tech_score = 0.0
        total_techs = len(appcat_results.technology_assessments)
        
        if total_techs == 0:
            return 50.0
            
        # Count technologies by migration effort
        effort_scores = {
            "Critical": 100,
            "High": 70,
            "Medium": 40,
            "Low": 10
        }
        
        for tech in appcat_results.technology_assessments:
            tech_score += effort_scores.get(tech.migration_effort, 50)
            
        return min(tech_score / total_techs, 100.0)
        
    def _calculate_data_complexity(
        self,
        appcat_results: Optional[AppCATResults]
    ) -> float:
        """Calculate data access complexity (0-100)."""
        if not appcat_results:
            return 50.0
            
        # Simplified data complexity based on number of patterns
        pattern_count = len(appcat_results.data_access_patterns)
        
        if pattern_count == 0:
            return 30.0  # Simple or unknown
        elif pattern_count == 1:
            return 40.0  # Single pattern
        elif pattern_count == 2:
            return 60.0  # Multiple patterns
        else:
            return 75.0  # Complex data access
            
    def _identify_complexity_factors(
        self,
        arch_score: float,
        coupling_score: float,
        perf_score: float,
        tech_score: float,
        data_score: float,
        discrepancies: List[DiscrepancyFinding]
    ) -> List[str]:
        """Identify key complexity factors."""
        factors = []
        
        if arch_score > 60:
            factors.append(f"High architectural complexity ({arch_score:.0f}/100)")
        if coupling_score > 60:
            factors.append(f"Strong coupling between components ({coupling_score:.0f}/100)")
        if perf_score > 50:
            factors.append(f"Performance optimization needed ({perf_score:.0f}/100)")
        if tech_score > 60:
            factors.append(f"Technology stack modernization required ({tech_score:.0f}/100)")
        if data_score > 60:
            factors.append(f"Complex data access patterns ({data_score:.0f}/100)")
            
        # Add specific discrepancy factors
        critical_discrepancies = [d for d in discrepancies if d.severity == DiscrepancySeverity.CRITICAL]
        if critical_discrepancies:
            factors.append(f"{len(critical_discrepancies)} critical issues blocking migration")
            
        return factors
        
    def _identify_simplifications(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults],
        appcat_results: Optional[AppCATResults]
    ) -> List[str]:
        """Identify opportunities to simplify migration."""
        opportunities = []
        
        if appcat_results:
            # Check cloud readiness
            if appcat_results.cloud_readiness.overall_readiness_score > 70:
                opportunities.append("High cloud readiness enables smoother migration path")
                
            # Check for modern technologies
            modern_techs = [t for t in appcat_results.technology_assessments 
                          if t.migration_effort == "Low"]
            if len(modern_techs) > len(appcat_results.technology_assessments) / 2:
                opportunities.append("Modern technology stack reduces migration complexity")
                
        if runtime_results and runtime_results.baseline:
            # Check performance
            if runtime_results.baseline.response_time_p95 < 200:
                opportunities.append("Good performance baseline simplifies capacity planning")
                
            # Check error rate
            if runtime_results.baseline.error_rate < 0.01:
                opportunities.append("Low error rate indicates stable foundation for migration")
                
        return opportunities
        
    def _assess_migration_readiness(
        self,
        static_results: Optional[Dict[str, Any]],
        runtime_results: Optional[RuntimeAnalysisResults],
        appcat_results: Optional[AppCATResults],
        complexity_score: ComplexityScore,
        discrepancies: List[DiscrepancyFinding]
    ) -> MigrationReadinessAssessment:
        """Assess overall migration readiness."""
        
        # Calculate sub-scores
        technical_readiness = self._calculate_technical_readiness(
            complexity_score, discrepancies
        )
        
        architectural_readiness = self._calculate_architectural_readiness(
            appcat_results, complexity_score
        )
        
        performance_readiness = self._calculate_performance_readiness(
            runtime_results
        )
        
        organizational_readiness = self._calculate_organizational_readiness(
            complexity_score
        )
        
        # Calculate overall readiness score (inverse of complexity)
        readiness_score = 100.0 - (
            (complexity_score.overall_score * 0.4) +
            (100.0 - technical_readiness) * 0.3 +
            (100.0 - architectural_readiness) * 0.2 +
            (100.0 - performance_readiness) * 0.1
        )
        readiness_score = max(0.0, min(100.0, readiness_score))
        
        # Categorize readiness
        if readiness_score >= 75:
            readiness_category = "Ready"
        elif readiness_score >= 60:
            readiness_category = "Nearly Ready"
        elif readiness_score >= 40:
            readiness_category = "Needs Work"
        else:
            readiness_category = "Not Ready"
            
        # Identify blockers
        critical_blockers = [
            d.title for d in discrepancies 
            if d.severity == DiscrepancySeverity.CRITICAL
        ]
        
        high_severity_issues = [
            d for d in discrepancies 
            if d.severity == DiscrepancySeverity.HIGH
        ]
        
        # Prerequisites
        prerequisites = []
        if critical_blockers:
            prerequisites.append("Resolve all critical blockers")
        if high_severity_issues:
            prerequisites.append(f"Address {len(high_severity_issues)} high-severity issues")
        if complexity_score.overall_score > 70:
            prerequisites.append("Reduce architectural complexity through refactoring")
            
        # Go/No-Go decision
        if critical_blockers:
            go_no_go = "NO GO"
            rationale = f"Cannot proceed with {len(critical_blockers)} critical blockers"
        elif readiness_score >= 70:
            go_no_go = "GO"
            rationale = "System meets readiness criteria for migration"
        elif readiness_score >= 50:
            go_no_go = "CONDITIONAL GO"
            rationale = f"Proceed with caution; address {len(prerequisites)} prerequisites"
        else:
            go_no_go = "NO GO"
            rationale = "System not ready; significant preparation required"
            
        # Recommended approach
        if complexity_score.overall_score < 40:
            recommended_approach = "Big Bang"
            timeline_months = 6
        elif complexity_score.overall_score < 65:
            recommended_approach = "Strangler Fig"
            timeline_months = 12
        else:
            recommended_approach = "Parallel Run"
            timeline_months = 18
            
        # Confidence based on data quality
        if runtime_results and runtime_results.baseline:
            confidence = runtime_results.baseline.data_quality_score
        else:
            confidence = 0.75  # Default moderate confidence
            
        return MigrationReadinessAssessment(
            readiness_score=round(readiness_score, 1),
            readiness_category=readiness_category,
            technical_readiness=round(technical_readiness, 1),
            architectural_readiness=round(architectural_readiness, 1),
            performance_readiness=round(performance_readiness, 1),
            organizational_readiness=round(organizational_readiness, 1),
            go_no_go_recommendation=go_no_go,
            go_no_go_rationale=rationale,
            critical_blockers=critical_blockers,
            prerequisites=prerequisites,
            recommended_approach=recommended_approach,
            estimated_timeline_months=timeline_months,
            confidence_level=confidence
        )
        
    def _calculate_technical_readiness(
        self,
        complexity_score: ComplexityScore,
        discrepancies: List[DiscrepancyFinding]
    ) -> float:
        """Calculate technical readiness score."""
        readiness = 100.0
        
        # Deduct for complexity
        readiness -= (complexity_score.technology_complexity * 0.5)
        
        # Deduct for high-severity issues
        high_severity = sum(1 for d in discrepancies if d.severity in [
            DiscrepancySeverity.CRITICAL, DiscrepancySeverity.HIGH
        ])
        readiness -= (high_severity * 5)
        
        return max(0.0, min(100.0, readiness))
        
    def _calculate_architectural_readiness(
        self,
        appcat_results: Optional[AppCATResults],
        complexity_score: ComplexityScore
    ) -> float:
        """Calculate architectural readiness score."""
        if appcat_results:
            # Use cloud readiness as base
            readiness = appcat_results.cloud_readiness.overall_readiness_score
        else:
            readiness = 60.0  # Default moderate readiness
            
        # Adjust for architectural complexity
        readiness -= (complexity_score.architectural_complexity * 0.3)
        
        return max(0.0, min(100.0, readiness))
        
    def _calculate_performance_readiness(
        self,
        runtime_results: Optional[RuntimeAnalysisResults]
    ) -> float:
        """Calculate performance readiness score."""
        if not runtime_results or not runtime_results.baseline:
            return 60.0  # Default moderate readiness
            
        baseline = runtime_results.baseline
        readiness = 100.0
        
        # Deduct for poor performance
        if baseline.response_time_p95 > 1000:
            readiness -= 40
        elif baseline.response_time_p95 > 500:
            readiness -= 20
        elif baseline.response_time_p95 > 200:
            readiness -= 10
            
        # Deduct for high error rate
        if baseline.error_rate > 0.05:
            readiness -= 30
        elif baseline.error_rate > 0.01:
            readiness -= 15
            
        return max(0.0, min(100.0, readiness))
        
    def _calculate_organizational_readiness(
        self,
        complexity_score: ComplexityScore
    ) -> float:
        """Calculate organizational readiness score."""
        # Simplified - based on estimated effort
        if complexity_score.estimated_effort_weeks <= 12:
            return 80.0
        elif complexity_score.estimated_effort_weeks <= 24:
            return 60.0
        else:
            return 40.0
            
    def _calculate_gap_metrics(
        self,
        discrepancies: List[DiscrepancyFinding],
        complexity_score: ComplexityScore,
        readiness_assessment: MigrationReadinessAssessment
    ) -> Dict[str, Any]:
        """Calculate gap analysis metrics."""
        return {
            "total_discrepancies": len(discrepancies),
            "by_severity": {
                "critical": sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.CRITICAL),
                "high": sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.HIGH),
                "medium": sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.MEDIUM),
                "low": sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.LOW),
                "info": sum(1 for d in discrepancies if d.severity == DiscrepancySeverity.INFO)
            },
            "by_category": {
                cat.value: sum(1 for d in discrepancies if d.category == cat)
                for cat in GapCategory
            },
            "complexity_summary": {
                "overall_score": complexity_score.overall_score,
                "level": complexity_score.complexity_level,
                "estimated_effort_weeks": complexity_score.estimated_effort_weeks
            },
            "readiness_summary": {
                "overall_score": readiness_assessment.readiness_score,
                "category": readiness_assessment.readiness_category,
                "recommendation": readiness_assessment.go_no_go_recommendation,
                "approach": readiness_assessment.recommended_approach,
                "timeline_months": readiness_assessment.estimated_timeline_months
            },
            "average_confidence": sum(d.confidence_score for d in discrepancies) / len(discrepancies) if discrepancies else 0.0
        }
        
    def _summarize_discrepancies(
        self,
        discrepancies: List[DiscrepancyFinding]
    ) -> Dict[str, int]:
        """Summarize discrepancies by category and severity."""
        summary = {}
        
        for severity in DiscrepancySeverity:
            summary[f"severity_{severity.value}"] = sum(
                1 for d in discrepancies if d.severity == severity
            )
            
        for category in GapCategory:
            summary[f"category_{category.value}"] = sum(
                1 for d in discrepancies if d.category == category
            )
            
        return summary
        
    def _validate_results(
        self,
        readiness_assessment: MigrationReadinessAssessment,
        complexity_score: ComplexityScore,
        discrepancies: List[DiscrepancyFinding]
    ) -> str:
        """Validate gap analysis results."""
        warnings = []
        
        # Check for critical blockers
        if readiness_assessment.critical_blockers:
            warnings.append("critical_blockers_present")
            
        # Check complexity vs readiness alignment
        if complexity_score.overall_score > 70 and readiness_assessment.readiness_score > 60:
            warnings.append("readiness_complexity_mismatch")
            
        # Check for insufficient data
        if not discrepancies:
            warnings.append("no_discrepancies_found")
            
        if warnings:
            return "warnings" if len(warnings) < 3 else "failed"
        return "passed"
        
    def export_results(
        self,
        results: GapAnalysisResult,
        output_path: Path
    ) -> None:
        """Export gap analysis results to JSON."""
        output_data = {
            "analysis_id": results.analysis_id,
            "application_name": results.application_name,
            "analysis_timestamp": results.analysis_timestamp.isoformat(),
            "static_analysis_id": results.static_analysis_id,
            "runtime_analysis_id": results.runtime_analysis_id,
            "discrepancies": [
                {
                    "finding_id": d.finding_id,
                    "category": d.category.value,
                    "severity": d.severity.value,
                    "title": d.title,
                    "description": d.description,
                    "migration_impact": d.migration_impact,
                    "remediation_effort": d.remediation_effort,
                    "recommended_action": d.recommended_action,
                    "confidence_score": d.confidence_score
                }
                for d in results.discrepancies
            ],
            "complexity_score": {
                "overall_score": results.complexity_score.overall_score,
                "architectural_complexity": results.complexity_score.architectural_complexity,
                "coupling_complexity": results.complexity_score.coupling_complexity,
                "performance_complexity": results.complexity_score.performance_complexity,
                "technology_complexity": results.complexity_score.technology_complexity,
                "data_complexity": results.complexity_score.data_complexity,
                "complexity_level": results.complexity_score.complexity_level,
                "estimated_effort_weeks": results.complexity_score.estimated_effort_weeks,
                "complexity_factors": results.complexity_score.complexity_factors,
                "simplification_opportunities": results.complexity_score.simplification_opportunities
            },
            "readiness_assessment": {
                "readiness_score": results.readiness_assessment.readiness_score,
                "readiness_category": results.readiness_assessment.readiness_category,
                "technical_readiness": results.readiness_assessment.technical_readiness,
                "architectural_readiness": results.readiness_assessment.architectural_readiness,
                "performance_readiness": results.readiness_assessment.performance_readiness,
                "organizational_readiness": results.readiness_assessment.organizational_readiness,
                "go_no_go_recommendation": results.readiness_assessment.go_no_go_recommendation,
                "go_no_go_rationale": results.readiness_assessment.go_no_go_rationale,
                "critical_blockers": results.readiness_assessment.critical_blockers,
                "prerequisites": results.readiness_assessment.prerequisites,
                "recommended_approach": results.readiness_assessment.recommended_approach,
                "estimated_timeline_months": results.readiness_assessment.estimated_timeline_months,
                "confidence_level": results.readiness_assessment.confidence_level
            },
            "gap_metrics": results.gap_metrics,
            "discrepancy_summary": results.discrepancy_summary,
            "validation_status": results.validation_status
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Gap analysis results exported to: {output_path}")
        
    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration for gap analysis."""
        return {
            "performance_thresholds": {
                "p95_response_time_ms": 500,
                "error_rate": 0.05,
                "min_throughput_rps": 10
            },
            "complexity_weights": {
                "architectural": 0.25,
                "coupling": 0.25,
                "performance": 0.20,
                "technology": 0.20,
                "data": 0.10
            },
            "severity_thresholds": {
                "critical_blocker_threshold": 1,
                "high_severity_threshold": 3
            }
        }


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gap analysis comparison engine')
    parser.add_argument('--app-name', default='spring-modulith', help='Application name')
    parser.add_argument('--output', default='/tmp/gap-analysis.json', help='Output file')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"\n=== Gap Analysis Engine ===")
    print(f"Application: {args.app_name}")
    print(f"Output: {args.output}")
    print()
    
    analyzer = GapAnalyzer()
    
    # Example usage with mock data
    results = analyzer.analyze_gaps(
        application_name=args.app_name
    )
    
    analyzer.export_results(results, Path(args.output))
    
    print(f"\n=== Analysis Complete ===")
    print(f"Analysis ID: {results.analysis_id}")
    print(f"Discrepancies Found: {len(results.discrepancies)}")
    print(f"Complexity Score: {results.complexity_score.overall_score}/100 ({results.complexity_score.complexity_level})")
    print(f"Readiness Score: {results.readiness_assessment.readiness_score}/100 ({results.readiness_assessment.readiness_category})")
    print(f"Recommendation: {results.readiness_assessment.go_no_go_recommendation}")
    print(f"\nResults exported to: {args.output}")
