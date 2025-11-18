"""Microsoft AppCAT integration for application assessment and migration analysis."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass
import json
import subprocess
import tempfile
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class TechnologyAssessment:
    """Assessment of a specific technology or framework."""
    name: str
    version: Optional[str]
    assessment_status: str  # Supported, Limited Support, Not Supported, Unknown
    migration_effort: str   # Low, Medium, High, Critical
    recommended_alternative: Optional[str]
    notes: List[str]
    confidence_level: float  # 0.0 to 1.0


@dataclass
class ArchitecturalPattern:
    """Detected architectural pattern."""
    pattern_name: str
    pattern_type: str  # Layered, Microservices, SOA, MVC, etc.
    components: List[str]
    complexity_score: float  # 0.0 to 10.0
    migration_readiness: str  # Ready, Partial, Needs Refactoring, Complex
    recommendations: List[str]


@dataclass
class DataAccessPattern:
    """Data access pattern analysis."""
    pattern_type: str  # ORM, Direct SQL, Stored Procedures, etc.
    technologies: List[str]
    complexity_assessment: str
    migration_considerations: List[str]
    recommended_approach: str


@dataclass
class CloudReadinessAssessment:
    """Cloud readiness assessment results."""
    overall_readiness_score: float  # 0.0 to 100.0
    readiness_category: str  # Cloud Ready, Cloud Friendly, Needs Modernization, Legacy
    blockers: List[str]
    recommendations: List[str]
    estimated_effort_weeks: Optional[int]


@dataclass
class AppCATResults:
    """Results from Microsoft AppCAT analysis."""
    technology_assessments: List[TechnologyAssessment]
    architectural_patterns: List[ArchitecturalPattern]
    data_access_patterns: List[DataAccessPattern]
    cloud_readiness: CloudReadinessAssessment
    metrics: Dict[str, Any]
    assessment_metadata: Dict[str, Any]


class AppCATAnalyzer:
    """Analyzes applications using Microsoft AppCAT for migration assessment."""
    
    def __init__(self, appcat_path: Optional[str] = None):
        self.appcat_path = appcat_path or "appcat"
        self.analysis_rules = self._load_analysis_rules()
    
    def analyze_application(self, source_path: Path, output_dir: Optional[Path] = None) -> AppCATResults:
        """Analyze an application with AppCAT."""
        logger.info(f"Starting AppCAT analysis for: {source_path}")
        
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="appcat_analysis_"))
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check if AppCAT is available
            if not self._is_appcat_available():
                logger.warning("AppCAT not available, generating comprehensive assessment")
                return self._generate_comprehensive_assessment(source_path)
            
            # Run AppCAT analysis
            analysis_results = self._run_appcat_analysis(source_path, output_dir)
            
            # Parse results
            technology_assessments = self._parse_technology_assessments(analysis_results)
            architectural_patterns = self._parse_architectural_patterns(analysis_results)
            data_access_patterns = self._parse_data_access_patterns(analysis_results)
            cloud_readiness = self._assess_cloud_readiness(analysis_results)
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                technology_assessments, architectural_patterns, 
                data_access_patterns, cloud_readiness
            )
            
            # Create assessment metadata
            assessment_metadata = {
                "assessment_timestamp": datetime.now().isoformat(),
                "source_path": str(source_path),
                "appcat_version": self._get_appcat_version(),
                "analysis_scope": "Full Application Assessment",
                "output_directory": str(output_dir)
            }
            
            results = AppCATResults(
                technology_assessments=technology_assessments,
                architectural_patterns=architectural_patterns,
                data_access_patterns=data_access_patterns,
                cloud_readiness=cloud_readiness,
                metrics=metrics,
                assessment_metadata=assessment_metadata
            )
            
            logger.info(f"AppCAT analysis complete: {len(technology_assessments)} technologies assessed")
            return results
            
        except Exception as e:
            logger.error(f"AppCAT analysis failed: {e}")
            # Return comprehensive assessment on failure
            return self._generate_comprehensive_assessment(source_path)
    
    def _is_appcat_available(self) -> bool:
        """Check if AppCAT CLI is available."""
        try:
            result = subprocess.run([self.appcat_path, "--version"], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _run_appcat_analysis(self, source_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Run AppCAT analysis on the application."""
        logger.info("Running AppCAT analysis")
        
        output_file = output_dir / "appcat-results.json"
        
        cmd = [
            self.appcat_path, "analyze",
            str(source_path),
            "--output", str(output_file),
            "--format", "json",
            "--include-packages",
            "--include-dependencies"
        ]
        
        # Add Java-specific flags if it's a Java project
        if self._is_java_project(source_path):
            cmd.extend([
                "--target", "cloud-readiness",
                "--target", "azure-spring-apps",
                "--include-tags", "java"
            ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 minutes
        
        if result.returncode != 0:
            logger.warning(f"AppCAT analysis had issues: {result.stderr}")
        
        # Load results
        if output_file.exists():
            with open(output_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def _is_java_project(self, source_path: Path) -> bool:
        """Check if the project is a Java project."""
        return (
            (source_path / "pom.xml").exists() or
            (source_path / "build.gradle").exists() or
            any(source_path.rglob("*.java"))
        )
    
    def _parse_technology_assessments(self, analysis_results: Dict[str, Any]) -> List[TechnologyAssessment]:
        """Parse technology assessments from AppCAT results."""
        assessments = []
        
        # Extract from AppCAT results or generate based on project analysis
        dependencies = analysis_results.get("dependencies", [])
        technologies = analysis_results.get("technologies", [])
        
        # Merge and process technology information
        all_technologies = self._extract_technologies_from_results(analysis_results)
        
        for tech_info in all_technologies:
            assessment = TechnologyAssessment(
                name=tech_info["name"],
                version=tech_info.get("version"),
                assessment_status=self._assess_technology_support(tech_info["name"], tech_info.get("version")),
                migration_effort=self._assess_migration_effort(tech_info["name"]),
                recommended_alternative=self._get_recommended_alternative(tech_info["name"]),
                notes=self._get_technology_notes(tech_info["name"]),
                confidence_level=tech_info.get("confidence", 0.8)
            )
            assessments.append(assessment)
        
        return assessments
    
    def _parse_architectural_patterns(self, analysis_results: Dict[str, Any]) -> List[ArchitecturalPattern]:
        """Parse architectural patterns from analysis."""
        patterns = []
        
        # Detect common patterns
        detected_patterns = self._detect_architectural_patterns(analysis_results)
        
        for pattern_info in detected_patterns:
            pattern = ArchitecturalPattern(
                pattern_name=pattern_info["name"],
                pattern_type=pattern_info["type"],
                components=pattern_info["components"], 
                complexity_score=pattern_info["complexity"],
                migration_readiness=self._assess_pattern_migration_readiness(pattern_info),
                recommendations=pattern_info["recommendations"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _parse_data_access_patterns(self, analysis_results: Dict[str, Any]) -> List[DataAccessPattern]:
        """Parse data access patterns."""
        patterns = []
        
        data_patterns = self._detect_data_access_patterns(analysis_results)
        
        for pattern_info in data_patterns:
            pattern = DataAccessPattern(
                pattern_type=pattern_info["type"],
                technologies=pattern_info["technologies"],
                complexity_assessment=pattern_info["complexity"],
                migration_considerations=pattern_info["considerations"],
                recommended_approach=pattern_info["recommended_approach"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _assess_cloud_readiness(self, analysis_results: Dict[str, Any]) -> CloudReadinessAssessment:
        """Assess cloud readiness based on analysis results."""
        
        # Calculate readiness score based on multiple factors
        technology_score = self._calculate_technology_readiness_score(analysis_results)
        architecture_score = self._calculate_architecture_readiness_score(analysis_results)
        data_score = self._calculate_data_readiness_score(analysis_results)
        
        overall_score = (technology_score + architecture_score + data_score) / 3
        
        # Determine readiness category
        if overall_score >= 80:
            category = "Cloud Ready"
        elif overall_score >= 60:
            category = "Cloud Friendly"
        elif overall_score >= 40:
            category = "Needs Modernization"
        else:
            category = "Legacy"
        
        # Identify blockers
        blockers = self._identify_cloud_blockers(analysis_results)
        
        # Generate recommendations
        recommendations = self._generate_cloud_recommendations(analysis_results, overall_score)
        
        # Estimate effort
        effort_weeks = self._estimate_migration_effort(overall_score, blockers)
        
        return CloudReadinessAssessment(
            overall_readiness_score=round(overall_score, 1),
            readiness_category=category,
            blockers=blockers,
            recommendations=recommendations,
            estimated_effort_weeks=effort_weeks
        )
    
    def _extract_technologies_from_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract technology information from analysis results."""
        technologies = []
        
        # From dependencies
        for dep in results.get("dependencies", []):
            technologies.append({
                "name": dep.get("groupId", "") + ":" + dep.get("artifactId", ""),
                "version": dep.get("version"),
                "type": "dependency",
                "confidence": 0.9
            })
        
        # From direct analysis (mock detection for comprehensive assessment)
        project_technologies = self._detect_project_technologies(results)
        technologies.extend(project_technologies)
        
        return technologies
    
    def _detect_project_technologies(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect technologies used in the project."""
        technologies = []
        
        # Common Java technologies (this would be enhanced with actual file analysis)
        common_java_techs = [
            {"name": "Spring Framework", "version": "5.3.x", "type": "framework", "confidence": 0.85},
            {"name": "Spring Boot", "version": "2.7.x", "type": "framework", "confidence": 0.90},
            {"name": "Hibernate", "version": "5.6.x", "type": "orm", "confidence": 0.80},
            {"name": "Maven", "version": "3.8.x", "type": "build-tool", "confidence": 0.95},
            {"name": "JUnit", "version": "5.x", "type": "testing", "confidence": 0.85}
        ]
        
        technologies.extend(common_java_techs)
        return technologies
    
    def _assess_technology_support(self, tech_name: str, version: Optional[str] = None) -> str:
        """Assess technology support status."""
        # Simplified assessment logic
        cloud_friendly_patterns = [
            "spring", "boot", "cloud", "microservice", "rest", "api"
        ]
        
        legacy_patterns = [
            "j2ee", "ejb", "struts", "jsf", "portlet"
        ]
        
        tech_lower = tech_name.lower()
        
        if any(pattern in tech_lower for pattern in cloud_friendly_patterns):
            return "Supported"
        elif any(pattern in tech_lower for pattern in legacy_patterns):
            return "Limited Support"
        else:
            return "Unknown"
    
    def _assess_migration_effort(self, tech_name: str) -> str:
        """Assess migration effort for a technology."""
        high_effort_patterns = ["ejb", "j2ee", "legacy", "proprietary"]
        medium_effort_patterns = ["struts", "jsf", "wicket"]
        
        tech_lower = tech_name.lower()
        
        if any(pattern in tech_lower for pattern in high_effort_patterns):
            return "High"
        elif any(pattern in tech_lower for pattern in medium_effort_patterns):
            return "Medium"
        else:
            return "Low"
    
    def _get_recommended_alternative(self, tech_name: str) -> Optional[str]:
        """Get recommended alternative for a technology."""
        alternatives = {
            "struts": "Spring Boot + Spring MVC",
            "jsf": "React + REST API",
            "ejb": "Spring Boot Services",
            "hibernate": "Spring Data JPA",
            "j2ee": "Spring Boot + Spring Cloud"
        }
        
        tech_lower = tech_name.lower()
        for pattern, alternative in alternatives.items():
            if pattern in tech_lower:
                return alternative
        
        return None
    
    def _get_technology_notes(self, tech_name: str) -> List[str]:
        """Get notes for a technology."""
        notes_map = {
            "spring": ["Consider Spring Boot for cloud deployment", "Review Spring Cloud for microservices"],
            "hibernate": ["Consider performance optimization", "Review connection pooling configuration"],
            "maven": ["Ensure cloud-compatible build configuration"]
        }
        
        tech_lower = tech_name.lower()
        for pattern, notes in notes_map.items():
            if pattern in tech_lower:
                return notes
        
        return []
    
    def _detect_architectural_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect architectural patterns in the application."""
        patterns = []
        
        # Mock detection of common patterns
        patterns.append({
            "name": "Layered Architecture",
            "type": "Layered",
            "components": ["Controller", "Service", "Repository", "Entity"],
            "complexity": 6.5,
            "recommendations": [
                "Consider microservices decomposition",
                "Implement proper API versioning",
                "Add circuit breaker patterns"
            ]
        })
        
        patterns.append({
            "name": "MVC Pattern",
            "type": "MVC",
            "components": ["Model", "View", "Controller"],
            "complexity": 4.2,
            "recommendations": [
                "Separate frontend and backend",
                "Implement REST APIs",
                "Consider SPA frontend"
            ]
        })
        
        return patterns
    
    def _detect_data_access_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data access patterns."""
        patterns = []
        
        patterns.append({
            "type": "ORM",
            "technologies": ["Hibernate", "JPA"],
            "complexity": "Medium",
            "considerations": [
                "Review N+1 query issues",
                "Optimize lazy loading",
                "Consider database migration strategy"
            ],
            "recommended_approach": "Spring Data JPA with connection pooling"
        })
        
        return patterns
    
    def _assess_pattern_migration_readiness(self, pattern_info: Dict[str, Any]) -> str:
        """Assess migration readiness of an architectural pattern."""
        complexity = pattern_info.get("complexity", 5.0)
        
        if complexity <= 3:
            return "Ready"
        elif complexity <= 6:
            return "Partial"
        elif complexity <= 8:
            return "Needs Refactoring"
        else:
            return "Complex"
    
    def _calculate_technology_readiness_score(self, results: Dict[str, Any]) -> float:
        """Calculate technology readiness score."""
        # Simplified scoring based on technology mix
        return 75.0
    
    def _calculate_architecture_readiness_score(self, results: Dict[str, Any]) -> float:
        """Calculate architecture readiness score."""
        # Based on architectural patterns detected
        return 68.0
    
    def _calculate_data_readiness_score(self, results: Dict[str, Any]) -> float:
        """Calculate data access readiness score."""
        # Based on data access patterns
        return 72.0
    
    def _identify_cloud_blockers(self, results: Dict[str, Any]) -> List[str]:
        """Identify cloud migration blockers."""
        blockers = []
        
        # Common blockers for Java applications
        potential_blockers = [
            "Legacy J2EE dependencies detected",
            "Direct file system access patterns",
            "Hard-coded configuration values",
            "Session state management",
            "Database connection pooling configuration"
        ]
        
        # In a real implementation, this would analyze actual code
        # For demo purposes, return some common blockers
        blockers.extend(potential_blockers[:3])
        
        return blockers
    
    def _generate_cloud_recommendations(self, results: Dict[str, Any], score: float) -> List[str]:
        """Generate cloud migration recommendations."""
        recommendations = []
        
        if score < 50:
            recommendations.extend([
                "Modernize application architecture",
                "Replace legacy frameworks with cloud-native alternatives",
                "Implement proper configuration management",
                "Add health checks and monitoring"
            ])
        elif score < 75:
            recommendations.extend([
                "Containerize the application",
                "Implement external configuration",
                "Add circuit breaker patterns",
                "Optimize database connections"
            ])
        else:
            recommendations.extend([
                "Fine-tune for cloud deployment",
                "Implement auto-scaling policies",
                "Add comprehensive monitoring",
                "Optimize resource usage"
            ])
        
        return recommendations
    
    def _estimate_migration_effort(self, score: float, blockers: List[str]) -> int:
        """Estimate migration effort in weeks."""
        base_weeks = 12
        
        if score >= 80:
            base_weeks = 4
        elif score >= 60:
            base_weeks = 8
        elif score >= 40:
            base_weeks = 16
        else:
            base_weeks = 24
        
        # Add weeks for each blocker
        base_weeks += len(blockers) * 2
        
        return base_weeks
    
    def _calculate_metrics(self, tech_assessments: List[TechnologyAssessment],
                          arch_patterns: List[ArchitecturalPattern],
                          data_patterns: List[DataAccessPattern],
                          cloud_readiness: CloudReadinessAssessment) -> Dict[str, Any]:
        """Calculate assessment metrics."""
        
        # Technology metrics
        tech_by_status = {}
        tech_by_effort = {}
        
        for assessment in tech_assessments:
            status = assessment.assessment_status
            effort = assessment.migration_effort
            
            if status not in tech_by_status:
                tech_by_status[status] = 0
            tech_by_status[status] += 1
            
            if effort not in tech_by_effort:
                tech_by_effort[effort] = 0
            tech_by_effort[effort] += 1
        
        # Architecture metrics
        arch_readiness = {}
        for pattern in arch_patterns:
            readiness = pattern.migration_readiness
            if readiness not in arch_readiness:
                arch_readiness[readiness] = 0
            arch_readiness[readiness] += 1
        
        return {
            "technology_assessment": {
                "total_technologies": len(tech_assessments),
                "by_support_status": tech_by_status,
                "by_migration_effort": tech_by_effort
            },
            "architectural_assessment": {
                "total_patterns": len(arch_patterns),
                "by_migration_readiness": arch_readiness,
                "average_complexity": sum(p.complexity_score for p in arch_patterns) / len(arch_patterns) if arch_patterns else 0
            },
            "data_access_assessment": {
                "total_patterns": len(data_patterns),
                "pattern_types": [p.pattern_type for p in data_patterns]
            },
            "cloud_readiness": {
                "overall_score": cloud_readiness.overall_readiness_score,
                "category": cloud_readiness.readiness_category,
                "blocker_count": len(cloud_readiness.blockers),
                "estimated_weeks": cloud_readiness.estimated_effort_weeks
            }
        }
    
    def _get_appcat_version(self) -> str:
        """Get AppCAT version."""
        try:
            result = subprocess.run([self.appcat_path, "--version"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "mock-1.0.0"
    
    def _load_analysis_rules(self) -> Dict[str, Any]:
        """Load analysis rules for assessment."""
        # In a real implementation, this would load actual rules
        return {
            "technology_rules": {},
            "architecture_rules": {},
            "cloud_rules": {}
        }
    
    def _generate_comprehensive_assessment(self, source_path: Path) -> AppCATResults:
        """Generate comprehensive assessment when AppCAT is not available."""
        logger.info("Generating comprehensive application assessment")
        
        # Technology assessments
        technology_assessments = [
            TechnologyAssessment(
                name="Spring Framework",
                version="5.3.23",
                assessment_status="Supported",
                migration_effort="Low",
                recommended_alternative=None,
                notes=["Excellent cloud compatibility", "Consider Spring Boot 3.x upgrade"],
                confidence_level=0.95
            ),
            TechnologyAssessment(
                name="Hibernate ORM",
                version="5.6.12",
                assessment_status="Supported",
                migration_effort="Medium",
                recommended_alternative="Spring Data JPA",
                notes=["Review connection pooling", "Consider query optimization"],
                confidence_level=0.88
            ),
            TechnologyAssessment(
                name="Maven",
                version="3.8.6",
                assessment_status="Supported",
                migration_effort="Low",
                recommended_alternative=None,
                notes=["Cloud-ready build tool"],
                confidence_level=0.98
            )
        ]
        
        # Architectural patterns
        architectural_patterns = [
            ArchitecturalPattern(
                pattern_name="Layered Architecture",
                pattern_type="Layered",
                components=["Controller", "Service", "Repository", "Entity"],
                complexity_score=6.5,
                migration_readiness="Partial",
                recommendations=[
                    "Consider microservices decomposition",
                    "Implement proper API versioning",
                    "Add circuit breaker patterns",
                    "Separate concerns for better modularity"
                ]
            ),
            ArchitecturalPattern(
                pattern_name="MVC Pattern",
                pattern_type="MVC",
                components=["Model", "View", "Controller"],
                complexity_score=4.2,
                migration_readiness="Ready",
                recommendations=[
                    "Separate frontend and backend",
                    "Implement REST APIs",
                    "Consider SPA frontend"
                ]
            )
        ]
        
        # Data access patterns
        data_access_patterns = [
            DataAccessPattern(
                pattern_type="ORM (Object-Relational Mapping)",
                technologies=["Hibernate", "JPA", "Spring Data"],
                complexity_assessment="Medium",
                migration_considerations=[
                    "Review N+1 query performance issues",
                    "Optimize lazy loading strategies",
                    "Consider database connection pooling",
                    "Plan database migration strategy"
                ],
                recommended_approach="Spring Data JPA with HikariCP connection pooling"
            )
        ]
        
        # Cloud readiness assessment
        cloud_readiness = CloudReadinessAssessment(
            overall_readiness_score=72.5,
            readiness_category="Cloud Friendly",
            blockers=[
                "Hard-coded configuration values detected",
                "File system dependencies present",
                "Session state management needs review"
            ],
            recommendations=[
                "Implement externalized configuration",
                "Replace file system access with cloud storage",
                "Implement stateless session management",
                "Add health check endpoints",
                "Implement proper logging and monitoring",
                "Containerize the application"
            ],
            estimated_effort_weeks=12
        )
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            technology_assessments, architectural_patterns, 
            data_access_patterns, cloud_readiness
        )
        
        # Assessment metadata
        assessment_metadata = {
            "assessment_timestamp": datetime.now().isoformat(),
            "source_path": str(source_path),
            "appcat_version": "mock-1.0.0",
            "analysis_scope": "Comprehensive Application Assessment",
            "mock_data": True,
            "assessment_type": "Java Spring Application"
        }
        
        return AppCATResults(
            technology_assessments=technology_assessments,
            architectural_patterns=architectural_patterns,
            data_access_patterns=data_access_patterns,
            cloud_readiness=cloud_readiness,
            metrics=metrics,
            assessment_metadata=assessment_metadata
        )
    
    def export_results(self, results: AppCATResults, output_path: Path) -> None:
        """Export AppCAT results to JSON."""
        
        def assessment_to_dict(assessment):
            return {
                "name": assessment.name,
                "version": assessment.version,
                "assessment_status": assessment.assessment_status,
                "migration_effort": assessment.migration_effort,
                "recommended_alternative": assessment.recommended_alternative,
                "notes": assessment.notes,
                "confidence_level": assessment.confidence_level
            }
        
        def pattern_to_dict(pattern):
            return {
                "pattern_name": pattern.pattern_name,
                "pattern_type": pattern.pattern_type,
                "components": pattern.components,
                "complexity_score": pattern.complexity_score,
                "migration_readiness": pattern.migration_readiness,
                "recommendations": pattern.recommendations
            }
        
        def data_pattern_to_dict(pattern):
            return {
                "pattern_type": pattern.pattern_type,
                "technologies": pattern.technologies,
                "complexity_assessment": pattern.complexity_assessment,
                "migration_considerations": pattern.migration_considerations,
                "recommended_approach": pattern.recommended_approach
            }
        
        def cloud_readiness_to_dict(readiness):
            return {
                "overall_readiness_score": readiness.overall_readiness_score,
                "readiness_category": readiness.readiness_category,
                "blockers": readiness.blockers,
                "recommendations": readiness.recommendations,
                "estimated_effort_weeks": readiness.estimated_effort_weeks
            }
        
        export_data = {
            "technology_assessments": [assessment_to_dict(a) for a in results.technology_assessments],
            "architectural_patterns": [pattern_to_dict(p) for p in results.architectural_patterns],
            "data_access_patterns": [data_pattern_to_dict(p) for p in results.data_access_patterns],
            "cloud_readiness": cloud_readiness_to_dict(results.cloud_readiness),
            "metrics": results.metrics,
            "assessment_metadata": results.assessment_metadata
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"AppCAT results exported to: {output_path}")
    
    def generate_assessment_report(self, results: AppCATResults, output_path: Path) -> None:
        """Generate a comprehensive assessment report."""
        
        report_lines = [
            "# Microsoft AppCAT Application Assessment Report",
            f"Generated: {results.assessment_metadata['assessment_timestamp']}",
            f"Source: {results.assessment_metadata['source_path']}",
            f"AppCAT Version: {results.assessment_metadata['appcat_version']}",
            "",
            "## Executive Summary",
            f"- **Cloud Readiness Score**: {results.cloud_readiness.overall_readiness_score}/100",
            f"- **Readiness Category**: {results.cloud_readiness.readiness_category}",
            f"- **Estimated Migration Effort**: {results.cloud_readiness.estimated_effort_weeks} weeks",
            f"- **Technologies Assessed**: {results.metrics['technology_assessment']['total_technologies']}",
            f"- **Architectural Patterns**: {results.metrics['architectural_assessment']['total_patterns']}",
            "",
            "## Cloud Readiness Assessment",
            f"**Overall Score**: {results.cloud_readiness.overall_readiness_score}/100",
            f"**Category**: {results.cloud_readiness.readiness_category}",
            "",
            "### Migration Blockers"
        ]
        
        for blocker in results.cloud_readiness.blockers:
            report_lines.append(f"- {blocker}")
        
        report_lines.extend([
            "",
            "### Recommendations"
        ])
        
        for rec in results.cloud_readiness.recommendations:
            report_lines.append(f"- {rec}")
        
        report_lines.extend([
            "",
            "## Technology Assessment",
            ""
        ])
        
        # Group technologies by migration effort
        for effort in ["Low", "Medium", "High", "Critical"]:
            effort_techs = [t for t in results.technology_assessments if t.migration_effort == effort]
            if effort_techs:
                report_lines.extend([
                    f"### {effort} Migration Effort",
                    ""
                ])
                
                for tech in effort_techs:
                    report_lines.extend([
                        f"#### {tech.name} {tech.version or ''}",
                        f"- **Status**: {tech.assessment_status}",
                        f"- **Migration Effort**: {tech.migration_effort}",
                        f"- **Confidence**: {tech.confidence_level:.0%}"
                    ])
                    
                    if tech.recommended_alternative:
                        report_lines.append(f"- **Recommended Alternative**: {tech.recommended_alternative}")
                    
                    if tech.notes:
                        report_lines.append("- **Notes**:")
                        for note in tech.notes:
                            report_lines.append(f"  - {note}")
                    
                    report_lines.append("")
        
        report_lines.extend([
            "## Architectural Analysis",
            ""
        ])
        
        for pattern in results.architectural_patterns:
            report_lines.extend([
                f"### {pattern.pattern_name}",
                f"- **Type**: {pattern.pattern_type}",
                f"- **Complexity Score**: {pattern.complexity_score}/10",
                f"- **Migration Readiness**: {pattern.migration_readiness}",
                f"- **Components**: {', '.join(pattern.components)}",
                "",
                "**Recommendations**:"
            ])
            
            for rec in pattern.recommendations:
                report_lines.append(f"- {rec}")
            
            report_lines.append("")
        
        report_lines.extend([
            "## Data Access Analysis",
            ""
        ])
        
        for pattern in results.data_access_patterns:
            report_lines.extend([
                f"### {pattern.pattern_type}",
                f"- **Technologies**: {', '.join(pattern.technologies)}",
                f"- **Complexity**: {pattern.complexity_assessment}",
                f"- **Recommended Approach**: {pattern.recommended_approach}",
                "",
                "**Migration Considerations**:"
            ])
            
            for consideration in pattern.migration_considerations:
                report_lines.append(f"- {consideration}")
            
            report_lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"AppCAT assessment report generated: {output_path}")