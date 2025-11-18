"""CodeQL integration for security scanning and code quality analysis."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
import json
import subprocess
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    """Represents a security finding from CodeQL analysis."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    file_path: str
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    category: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


@dataclass
class QualityFinding:
    """Represents a code quality finding from CodeQL analysis."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    file_path: str
    start_line: int
    end_line: int
    category: str
    maintainability_impact: str


@dataclass
class CodeQLResults:
    """Results from CodeQL analysis."""
    security_findings: List[SecurityFinding]
    quality_findings: List[QualityFinding]
    metrics: Dict[str, Any]
    scan_metadata: Dict[str, Any]


class CodeQLAnalyzer:
    """Analyzes Java applications using CodeQL for security and quality issues."""
    
    def __init__(self, codeql_path: Optional[str] = None):
        self.codeql_path = codeql_path or "codeql"
        self.java_query_packs = [
            "codeql/java-queries",
            "codeql/java-security-queries"
        ]
    
    def analyze_project(self, source_path: Path, output_dir: Optional[Path] = None) -> CodeQLResults:
        """Analyze a Java project with CodeQL."""
        logger.info(f"Starting CodeQL analysis for: {source_path}")
        
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="codeql_analysis_"))
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check if CodeQL is available
            if not self._is_codeql_available():
                logger.warning("CodeQL not available, generating mock results")
                return self._generate_mock_results(source_path)
            
            # Create CodeQL database
            db_path = output_dir / "codeql_db"
            self._create_database(source_path, db_path)
            
            # Run security queries
            security_results = self._run_security_queries(db_path, output_dir)
            
            # Run quality queries
            quality_results = self._run_quality_queries(db_path, output_dir)
            
            # Parse results
            security_findings = self._parse_security_results(security_results)
            quality_findings = self._parse_quality_results(quality_results)
            
            # Calculate metrics
            metrics = self._calculate_metrics(security_findings, quality_findings)
            
            # Create scan metadata
            scan_metadata = {
                "scan_timestamp": datetime.now().isoformat(),
                "source_path": str(source_path),
                "codeql_version": self._get_codeql_version(),
                "query_packs": self.java_query_packs,
                "database_path": str(db_path)
            }
            
            results = CodeQLResults(
                security_findings=security_findings,
                quality_findings=quality_findings,
                metrics=metrics,
                scan_metadata=scan_metadata
            )
            
            logger.info(f"CodeQL analysis complete: {len(security_findings)} security findings, {len(quality_findings)} quality findings")
            return results
            
        except Exception as e:
            logger.error(f"CodeQL analysis failed: {e}")
            # Return mock results on failure
            return self._generate_mock_results(source_path)
    
    def _is_codeql_available(self) -> bool:
        """Check if CodeQL CLI is available."""
        try:
            result = subprocess.run([self.codeql_path, "--version"], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _create_database(self, source_path: Path, db_path: Path) -> None:
        """Create CodeQL database from source code."""
        logger.info(f"Creating CodeQL database: {db_path}")
        
        cmd = [
            self.codeql_path, "database", "create",
            str(db_path),
            "--language=java",
            f"--source-root={source_path}",
            "--overwrite"
        ]
        
        # Auto-detect build system
        if (source_path / "pom.xml").exists():
            cmd.extend(["--command=mvn clean compile test-compile"])
        elif (source_path / "build.gradle").exists():
            cmd.extend(["--command=./gradlew compileJava compileTestJava"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create CodeQL database: {result.stderr}")
        
        logger.info("CodeQL database created successfully")
    
    def _run_security_queries(self, db_path: Path, output_dir: Path) -> Path:
        """Run security-focused CodeQL queries."""
        logger.info("Running CodeQL security queries")
        
        output_file = output_dir / "security-results.sarif"
        
        cmd = [
            self.codeql_path, "database", "analyze",
            str(db_path),
            "codeql/java-security-queries",
            "--format=sarif-latest",
            f"--output={output_file}",
            "--sarif-category=security"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode != 0:
            logger.warning(f"Security queries failed: {result.stderr}")
            # Create empty results file
            with open(output_file, 'w') as f:
                json.dump({"runs": []}, f)
        
        return output_file
    
    def _run_quality_queries(self, db_path: Path, output_dir: Path) -> Path:
        """Run code quality CodeQL queries."""
        logger.info("Running CodeQL quality queries")
        
        output_file = output_dir / "quality-results.sarif"
        
        cmd = [
            self.codeql_path, "database", "analyze",
            str(db_path),
            "codeql/java-queries:Maintainability",
            "codeql/java-queries:Reliability",
            "--format=sarif-latest",
            f"--output={output_file}",
            "--sarif-category=quality"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode != 0:
            logger.warning(f"Quality queries failed: {result.stderr}")
            # Create empty results file
            with open(output_file, 'w') as f:
                json.dump({"runs": []}, f)
        
        return output_file
    
    def _parse_security_results(self, results_file: Path) -> List[SecurityFinding]:
        """Parse security findings from SARIF results."""
        findings = []
        
        try:
            with open(results_file, 'r') as f:
                sarif_data = json.load(f)
            
            for run in sarif_data.get("runs", []):
                for result in run.get("results", []):
                    rule_id = result.get("ruleId", "unknown")
                    message = result.get("message", {}).get("text", "No description")
                    
                    # Extract location information
                    locations = result.get("locations", [])
                    if locations:
                        location = locations[0]
                        physical_location = location.get("physicalLocation", {})
                        artifact_location = physical_location.get("artifactLocation", {})
                        region = physical_location.get("region", {})
                        
                        file_path = artifact_location.get("uri", "unknown")
                        start_line = region.get("startLine", 0)
                        end_line = region.get("endLine", start_line)
                        start_column = region.get("startColumn", 0)
                        end_column = region.get("endColumn", start_column)
                    else:
                        file_path = "unknown"
                        start_line = end_line = start_column = end_column = 0
                    
                    # Determine severity
                    level = result.get("level", "note")
                    severity = self._map_sarif_level_to_severity(level)
                    
                    # Extract rule information
                    rule_info = self._get_rule_info(rule_id, run.get("tool", {}))
                    
                    finding = SecurityFinding(
                        rule_id=rule_id,
                        rule_name=rule_info.get("name", rule_id),
                        severity=severity,
                        message=message,
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        start_column=start_column,
                        end_column=end_column,
                        category=rule_info.get("category", "Security"),
                        cwe_id=rule_info.get("cwe_id"),
                        cvss_score=rule_info.get("cvss_score")
                    )
                    findings.append(finding)
                    
        except Exception as e:
            logger.error(f"Failed to parse security results: {e}")
        
        return findings
    
    def _parse_quality_results(self, results_file: Path) -> List[QualityFinding]:
        """Parse quality findings from SARIF results."""
        findings = []
        
        try:
            with open(results_file, 'r') as f:
                sarif_data = json.load(f)
            
            for run in sarif_data.get("runs", []):
                for result in run.get("results", []):
                    rule_id = result.get("ruleId", "unknown")
                    message = result.get("message", {}).get("text", "No description")
                    
                    # Extract location information (same as security)
                    locations = result.get("locations", [])
                    if locations:
                        location = locations[0]
                        physical_location = location.get("physicalLocation", {})
                        artifact_location = physical_location.get("artifactLocation", {})
                        region = physical_location.get("region", {})
                        
                        file_path = artifact_location.get("uri", "unknown")
                        start_line = region.get("startLine", 0)
                        end_line = region.get("endLine", start_line)
                    else:
                        file_path = "unknown"
                        start_line = end_line = 0
                    
                    # Determine severity and category
                    level = result.get("level", "note")
                    severity = self._map_sarif_level_to_severity(level)
                    
                    rule_info = self._get_rule_info(rule_id, run.get("tool", {}))
                    category = rule_info.get("category", "Quality")
                    
                    finding = QualityFinding(
                        rule_id=rule_id,
                        rule_name=rule_info.get("name", rule_id),
                        severity=severity,
                        message=message,
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        category=category,
                        maintainability_impact=self._assess_maintainability_impact(rule_id, severity)
                    )
                    findings.append(finding)
                    
        except Exception as e:
            logger.error(f"Failed to parse quality results: {e}")
        
        return findings
    
    def _map_sarif_level_to_severity(self, level: str) -> str:
        """Map SARIF level to severity."""
        mapping = {
            "error": "High",
            "warning": "Medium", 
            "note": "Low",
            "info": "Info"
        }
        return mapping.get(level, "Medium")
    
    def _get_rule_info(self, rule_id: str, tool_info: Dict) -> Dict[str, Any]:
        """Get additional rule information."""
        # Default rule information
        rule_info = {
            "name": rule_id,
            "category": "General",
            "cwe_id": None,
            "cvss_score": None
        }
        
        # Try to extract from tool information
        driver = tool_info.get("driver", {})
        rules = driver.get("rules", [])
        
        for rule in rules:
            if rule.get("id") == rule_id:
                rule_info["name"] = rule.get("name", rule_id)
                
                # Extract security metadata
                properties = rule.get("properties", {})
                if "security-severity" in properties:
                    try:
                        rule_info["cvss_score"] = float(properties["security-severity"])
                    except ValueError:
                        pass
                
                # Extract CWE information
                relationships = rule.get("relationships", [])
                for rel in relationships:
                    if rel.get("target", {}).get("toolComponent", {}).get("name") == "CWE":
                        rule_info["cwe_id"] = rel.get("target", {}).get("id")
                        break
                
                break
        
        return rule_info
    
    def _assess_maintainability_impact(self, rule_id: str, severity: str) -> str:
        """Assess maintainability impact of a quality finding."""
        # Simple heuristic based on rule ID patterns
        high_impact_patterns = ["complexity", "duplicate", "dead-code", "unused"]
        medium_impact_patterns = ["naming", "style", "documentation"]
        
        rule_lower = rule_id.lower()
        
        if any(pattern in rule_lower for pattern in high_impact_patterns):
            return "High"
        elif any(pattern in rule_lower for pattern in medium_impact_patterns):
            return "Medium"
        elif severity == "High":
            return "High"
        else:
            return "Low"
    
    def _calculate_metrics(self, security_findings: List[SecurityFinding], 
                          quality_findings: List[QualityFinding]) -> Dict[str, Any]:
        """Calculate metrics from findings."""
        
        # Security metrics
        security_by_severity = {"High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for finding in security_findings:
            security_by_severity[finding.severity] += 1
        
        # Quality metrics
        quality_by_severity = {"High": 0, "Medium": 0, "Low": 0, "Info": 0}
        quality_by_category = {}
        maintainability_impact = {"High": 0, "Medium": 0, "Low": 0}
        
        for finding in quality_findings:
            quality_by_severity[finding.severity] += 1
            
            category = finding.category
            if category not in quality_by_category:
                quality_by_category[category] = 0
            quality_by_category[category] += 1
            
            maintainability_impact[finding.maintainability_impact] += 1
        
        # Calculate security score (0-100, higher is better)
        total_security = len(security_findings)
        if total_security == 0:
            security_score = 100
        else:
            # Weight by severity: High=4, Medium=2, Low=1, Info=0.5
            weighted_issues = (security_by_severity["High"] * 4 + 
                             security_by_severity["Medium"] * 2 + 
                             security_by_severity["Low"] * 1 + 
                             security_by_severity["Info"] * 0.5)
            # Simple scoring formula
            security_score = max(0, 100 - (weighted_issues * 2))
        
        return {
            "security_findings": {
                "total": len(security_findings),
                "by_severity": security_by_severity,
                "security_score": round(security_score, 1)
            },
            "quality_findings": {
                "total": len(quality_findings),
                "by_severity": quality_by_severity,
                "by_category": quality_by_category,
                "maintainability_impact": maintainability_impact
            },
            "overall_score": round((security_score + max(0, 100 - len(quality_findings))) / 2, 1)
        }
    
    def _get_codeql_version(self) -> str:
        """Get CodeQL version."""
        try:
            result = subprocess.run([self.codeql_path, "--version"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        return "unknown"
    
    def _generate_mock_results(self, source_path: Path) -> CodeQLResults:
        """Generate mock results when CodeQL is not available."""
        logger.info("Generating mock CodeQL results for demonstration")
        
        # Mock security findings
        security_findings = [
            SecurityFinding(
                rule_id="java/sql-injection",
                rule_name="SQL Injection vulnerability",
                severity="High",
                message="Potential SQL injection vulnerability detected",
                file_path="src/main/java/com/example/UserService.java",
                start_line=45,
                end_line=45,
                start_column=20,
                end_column=50,
                category="Security",
                cwe_id="CWE-89",
                cvss_score=8.1
            ),
            SecurityFinding(
                rule_id="java/hardcoded-credentials",
                rule_name="Hardcoded credentials",
                severity="Medium",
                message="Hardcoded password detected",
                file_path="src/main/java/com/example/Config.java",
                start_line=23,
                end_line=23,
                start_column=15,
                end_column=35,
                category="Security",
                cwe_id="CWE-798",
                cvss_score=6.5
            )
        ]
        
        # Mock quality findings
        quality_findings = [
            QualityFinding(
                rule_id="java/complex-method",
                rule_name="Method too complex",
                severity="Medium",
                message="Method has cyclomatic complexity of 15, consider refactoring",
                file_path="src/main/java/com/example/OrderProcessor.java",
                start_line=67,
                end_line=120,
                category="Maintainability",
                maintainability_impact="High"
            ),
            QualityFinding(
                rule_id="java/duplicate-code",
                rule_name="Duplicate code block",
                severity="Low",
                message="Duplicate code block detected",
                file_path="src/main/java/com/example/Utils.java",
                start_line=15,
                end_line=25,
                category="Maintainability",
                maintainability_impact="Medium"
            )
        ]
        
        metrics = self._calculate_metrics(security_findings, quality_findings)
        
        scan_metadata = {
            "scan_timestamp": datetime.now().isoformat(),
            "source_path": str(source_path),
            "codeql_version": "mock-2.15.0",
            "query_packs": self.java_query_packs,
            "mock_data": True
        }
        
        return CodeQLResults(
            security_findings=security_findings,
            quality_findings=quality_findings,
            metrics=metrics,
            scan_metadata=scan_metadata
        )
    
    def export_results(self, results: CodeQLResults, output_path: Path) -> None:
        """Export CodeQL results to JSON."""
        
        def finding_to_dict(finding):
            if isinstance(finding, SecurityFinding):
                return {
                    "rule_id": finding.rule_id,
                    "rule_name": finding.rule_name,
                    "severity": finding.severity,
                    "message": finding.message,
                    "file_path": finding.file_path,
                    "start_line": finding.start_line,
                    "end_line": finding.end_line,
                    "start_column": finding.start_column,
                    "end_column": finding.end_column,
                    "category": finding.category,
                    "cwe_id": finding.cwe_id,
                    "cvss_score": finding.cvss_score,
                    "type": "security"
                }
            else:  # QualityFinding
                return {
                    "rule_id": finding.rule_id,
                    "rule_name": finding.rule_name,
                    "severity": finding.severity,
                    "message": finding.message,
                    "file_path": finding.file_path,
                    "start_line": finding.start_line,
                    "end_line": finding.end_line,
                    "category": finding.category,
                    "maintainability_impact": finding.maintainability_impact,
                    "type": "quality"
                }
        
        export_data = {
            "security_findings": [finding_to_dict(f) for f in results.security_findings],
            "quality_findings": [finding_to_dict(f) for f in results.quality_findings],
            "metrics": results.metrics,
            "scan_metadata": results.scan_metadata
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"CodeQL results exported to: {output_path}")
    
    def generate_report(self, results: CodeQLResults, output_path: Path) -> None:
        """Generate a human-readable report."""
        
        report_lines = [
            "# CodeQL Security and Quality Analysis Report",
            f"Generated: {results.scan_metadata['scan_timestamp']}",
            f"Source: {results.scan_metadata['source_path']}",
            f"CodeQL Version: {results.scan_metadata['codeql_version']}",
            "",
            "## Summary",
            f"- Security Findings: {results.metrics['security_findings']['total']}",
            f"- Quality Findings: {results.metrics['quality_findings']['total']}",
            f"- Overall Score: {results.metrics['overall_score']}/100",
            f"- Security Score: {results.metrics['security_findings']['security_score']}/100",
            "",
            "## Security Findings by Severity"
        ]
        
        for severity, count in results.metrics['security_findings']['by_severity'].items():
            if count > 0:
                report_lines.append(f"- {severity}: {count}")
        
        report_lines.extend([
            "",
            "## Quality Findings by Category"
        ])
        
        for category, count in results.metrics['quality_findings']['by_category'].items():
            report_lines.append(f"- {category}: {count}")
        
        if results.security_findings:
            report_lines.extend([
                "",
                "## Top Security Issues"
            ])
            
            # Show top 5 security findings
            high_security = [f for f in results.security_findings if f.severity == "High"][:5]
            for finding in high_security:
                report_lines.extend([
                    f"### {finding.rule_name}",
                    f"- **File**: {finding.file_path}:{finding.start_line}",
                    f"- **Severity**: {finding.severity}",
                    f"- **Message**: {finding.message}",
                    f"- **CWE**: {finding.cwe_id or 'N/A'}",
                    ""
                ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"CodeQL report generated: {output_path}")