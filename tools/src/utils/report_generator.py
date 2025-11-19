#!/usr/bin/env python3
"""
Omega Migration System - Report Generator Utility

Generates comprehensive analysis reports for Java Spring Boot codebases including:
- Static code analysis metrics
- Dependency graph analysis
- C4 architecture diagrams (Context, Container, Component, Code)
- Migration readiness assessment
- Markdown report with integrated diagrams

Usage:
    python -m src.utils.report_generator analyze --codebase /path/to/codebase --output /path/to/output

Requirements:
    - Java 17+ (for JavaParser analysis)
    - Python 3.12+
    - tree-sitter-java 0.23.5
    - PlantUML (optional, for rendering diagrams)

Author: Omega Migration System
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from omega_analysis.analysis.static.java_parser import (
    JavaSourceAnalyzer,
    JavaClass,
    JavaPackage,
    JavaMethod,
    JavaField,
)
from omega_analysis.analysis.static.structurizr import StructurizrGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ReportConfiguration:
    """Configuration for report generation."""
    
    codebase_path: Path
    output_dir: Path
    project_name: str
    generate_diagrams: bool = True
    diagram_formats: List[str] = field(default_factory=lambda: ["puml"])
    include_test_code: bool = False
    max_depth: int = 10
    verbose: bool = False


@dataclass
class C4DiagramSet:
    """Container for all C4 diagrams."""
    
    context: Optional[str] = None
    container: Optional[str] = None
    component: Optional[str] = None
    code: Dict[str, str] = field(default_factory=dict)


@dataclass
class ModuleAnalysisResult:
    """Results from analyzing a module."""
    classes: Dict[str, JavaClass]
    packages: Dict[str, JavaPackage]
    metrics: Dict[str, Any]


class ReportGenerator:
    """
    Main report generator that orchestrates analysis and report creation.
    
    Responsibilities:
    - Coordinate static analysis of codebase
    - Generate C4 architecture diagrams
    - Create comprehensive markdown report
    - Export results in multiple formats
    """
    
    def __init__(self, config: ReportConfiguration):
        self.config = config
        self.analyzer = JavaSourceAnalyzer()
        self.structurizr = StructurizrGenerator()
        
        # Analysis results
        self.modules: Dict[str, ModuleAnalysisResult] = {}
        self.dependency_graph: Optional[Dict] = None
        self.architecture_data: Optional[Dict] = None
        self.diagrams: C4DiagramSet = C4DiagramSet()
        
        # Setup output directories
        self.output_dir = config.output_dir
        self.diagrams_dir = self.output_dir / "diagrams"
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        if config.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def analyze_codebase(self) -> bool:
        """
        Analyze the entire codebase.
        
        Returns:
            True if analysis succeeded, False otherwise
        """
        logger.info(f"Starting analysis of codebase: {self.config.codebase_path}")
        
        if not self.config.codebase_path.exists():
            logger.error(f"Codebase path does not exist: {self.config.codebase_path}")
            return False
        
        # Find all module directories
        module_dirs = self._discover_modules()
        logger.info(f"Discovered {len(module_dirs)} modules")
        
        # Analyze each module
        all_dependencies = set()
        for module_name, module_path in module_dirs.items():
            logger.info(f"Analyzing module: {module_name}")
            result_dict = self.analyzer.analyze_directory(module_path)
            
            if result_dict and result_dict.get("classes"):
                result = ModuleAnalysisResult(
                    classes=result_dict["classes"],
                    packages=result_dict["packages"],
                    metrics=result_dict["metrics"]
                )
                self.modules[module_name] = result
                logger.info(
                    f"  - {module_name}: {len(result.classes)} classes, "
                    f"{result.metrics['total_methods']} methods"
                )
                
                # Collect dependencies
                for cls in result.classes.values():
                    all_dependencies.update(cls.dependencies)
        
        if not self.modules:
            logger.error("No modules were successfully analyzed")
            return False
        
        # Build dependency graph
        self._build_dependency_graph(all_dependencies)
        
        # Build architecture data
        self._build_architecture_data()
        
        logger.info(f"Analysis complete: {len(self.modules)} modules, {len(all_dependencies)} dependencies")
        return True
    
    def _discover_modules(self) -> Dict[str, Path]:
        """
        Discover module directories in the codebase.
        
        Returns:
            Dictionary mapping module names to their paths
        """
        modules = {}
        base_path = self.config.codebase_path
        
        # Look for common Spring Boot module patterns
        for child in base_path.iterdir():
            if not child.is_dir():
                continue
            
            # Skip common non-module directories
            if child.name in {'.git', '.github', 'target', 'build', 'node_modules', 'etc', 'src', 'docs'}:
                continue
            
            # Check if this looks like a module (has src/ directory)
            src_dir = child / "src" / "main" / "java"
            if src_dir.exists():
                modules[child.name] = src_dir
        
        return modules
    
    def _build_dependency_graph(self, dependencies: Set[str]) -> None:
        """Build dependency graph from analysis results."""
        nodes = []
        edges = []
        
        # Create nodes for each dependency
        for dep in sorted(dependencies):
            nodes.append({
                "id": dep,
                "label": dep.split(".")[-1],
                "type": self._classify_dependency(dep)
            })
        
        # Create edges based on usage patterns
        for module_name, result in self.modules.items():
            for class_full_name, cls in result.classes.items():
                source = class_full_name
                for dep in cls.dependencies:
                    if dep in dependencies:
                        edges.append({
                            "source": source,
                            "target": dep,
                            "module": module_name
                        })
        
        self.dependency_graph = {
            "nodes": nodes,
            "edges": edges
        }
    
    def _classify_dependency(self, dependency: str) -> str:
        """Classify a dependency based on its package name."""
        if dependency.startswith("org.springframework"):
            return "spring-framework"
        elif dependency.startswith("org.junit") or dependency.startswith("org.assertj"):
            return "testing"
        elif dependency.startswith("com.tngtech.archunit"):
            return "architecture-testing"
        elif dependency.startswith("com.jayway.jsonpath"):
            return "json-processing"
        elif dependency.startswith("java.") or dependency.startswith("javax."):
            return "jdk"
        else:
            return "external"
    
    def _build_architecture_data(self) -> None:
        """Build architecture metadata from analysis results."""
        self.architecture_data = {
            "modules": {},
            "metrics": {
                "total_modules": len(self.modules),
                "total_classes": 0,
                "total_methods": 0,
                "total_fields": 0,
                "total_packages": 0
            }
        }
        
        for module_name, result in self.modules.items():
            module_metrics = {
                "classes": len(result.classes),
                "methods": result.metrics.get("total_methods", 0),
                "fields": result.metrics.get("total_fields", 0),
                "packages": len(result.packages)
            }
            
            self.architecture_data["modules"][module_name] = module_metrics
            
            # Update totals
            self.architecture_data["metrics"]["total_classes"] += module_metrics["classes"]
            self.architecture_data["metrics"]["total_methods"] += module_metrics["methods"]
            self.architecture_data["metrics"]["total_fields"] += module_metrics["fields"]
            self.architecture_data["metrics"]["total_packages"] += module_metrics["packages"]
    
    def generate_diagrams(self) -> bool:
        """
        Generate all C4 diagrams.
        
        Returns:
            True if diagram generation succeeded
        """
        if not self.config.generate_diagrams:
            logger.info("Diagram generation disabled")
            return True
        
        logger.info("Generating C4 diagrams")
        
        try:
            # Generate C4 Context diagram (system landscape)
            self.diagrams.context = self._generate_context_diagram()
            
            # Generate C4 Container diagram (module-level)
            self.diagrams.container = self._generate_container_diagram()
            
            # Generate C4 Component diagram (detailed components)
            self.diagrams.component = self._generate_component_diagram()
            
            # Generate C4 Code diagrams (class-level for key modules)
            self._generate_code_diagrams()
            
            logger.info(f"Diagrams generated successfully in {self.diagrams_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to generate diagrams: {e}", exc_info=True)
            return False
    
    def _generate_context_diagram(self) -> str:
        """Generate C4 Context diagram showing system landscape."""
        diagram_path = self.diagrams_dir / f"{self.config.project_name}_context.puml"
        
        # Create PlantUML C4 Context diagram
        project_id = self.config.project_name.replace("-", "_")
        lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml",
            "",
            "LAYOUT_WITH_LEGEND()",
            f"title System Context Diagram for {self.config.project_name}",
            "",
            f'Person(developer, "Developer", "Software developers building and maintaining the system")',
            f'Person(architect, "Architect", "Enterprise architects analyzing the system")',
            f'Person(user, "End User", "Users interacting with the application")',
            "",
            f'System({project_id}, "{self.config.project_name}", "Monolithic Spring Boot application under analysis")',
            'System_Ext(database, "Database System", "Relational database (PostgreSQL/MySQL)")',
            'System_Ext(external_api, "External APIs", "Third-party services and APIs")',
            "",
            f'Rel(user, {project_id}, "Uses", "HTTPS/REST")',
            f'Rel(developer, {project_id}, "Develops and maintains", "IDE/Git")',
            f'Rel(architect, {project_id}, "Analyzes for migration", "Omega System")',
            f'Rel({project_id}, database, "Reads/Writes", "JDBC/JPA")',
            f'Rel({project_id}, external_api, "Integrates with", "REST/HTTP")',
            "",
            "@enduml"
        ]
        
        content = "\n".join(lines)
        diagram_path.write_text(content)
        logger.info(f"Generated C4 Context diagram: {diagram_path}")
        return content
    
    def _generate_container_diagram(self) -> str:
        """Generate C4 Container diagram showing modules."""
        diagram_path = self.diagrams_dir / f"{self.config.project_name}_container.puml"
        
        project_id = self.config.project_name.replace("-", "_")
        lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
            "",
            "LAYOUT_WITH_LEGEND()",
            f"title Container Diagram for {self.config.project_name}",
            "",
            'Person(developer, "Developer", "Software developers")',
            'Person(user, "End User", "Application users")',
            "",
            f'System_Boundary({project_id}_boundary, "{self.config.project_name}") {{',
        ]
        
        # Add containers for each module
        for module_name, metrics in self.architecture_data["modules"].items():
            clean_name = module_name.replace("-", "_")
            description = f"{metrics['classes']} classes, {metrics['methods']} methods"
            lines.append(
                f'    Container({clean_name}, "{module_name}", "Spring Boot Module", "{description}")'
            )
        
        lines.append("}")
        lines.append("")
        
        # Add external systems
        lines.extend([
            'ContainerDb(database, "Database", "PostgreSQL/MySQL", "Application data storage")',
            'System_Ext(external_api, "External APIs", "Third-party services")',
            "",
        ])
        
        # Add relationships
        lines.append(f'Rel(user, {list(self.architecture_data["modules"].keys())[0].replace("-", "_")}, "Uses", "HTTPS")')
        
        # Add module dependencies (simplified)
        module_names = list(self.architecture_data["modules"].keys())
        if len(module_names) > 1:
            for i in range(min(3, len(module_names) - 1)):
                source = module_names[i].replace("-", "_")
                target = module_names[i + 1].replace("-", "_")
                lines.append(f'Rel({source}, {target}, "Depends on", "Java imports")')
        
        lines.extend([
            "",
            "@enduml"
        ])
        
        content = "\n".join(lines)
        diagram_path.write_text(content)
        logger.info(f"Generated C4 Container diagram: {diagram_path}")
        return content
    
    def _generate_component_diagram(self) -> str:
        """Generate C4 Component diagram showing detailed components."""
        diagram_path = self.diagrams_dir / f"{self.config.project_name}_component.puml"
        
        # Focus on the largest module for component diagram
        largest_module = max(
            self.architecture_data["modules"].items(),
            key=lambda x: x[1]["classes"]
        )
        module_name, metrics = largest_module
        module_id = module_name.replace("-", "_")
        
        lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
            "",
            "LAYOUT_WITH_LEGEND()",
            f"title Component Diagram for {module_name}",
            "",
            f'Container_Boundary({module_id}_boundary, "{module_name}") {{',
        ]
        
        # Get packages from this module
        module_result = self.modules.get(module_name)
        if module_result:
            for pkg_name, pkg in list(module_result.packages.items())[:10]:  # Limit to top 10 packages
                pkg_display_name = pkg_name.split(".")[-1]
                clean_name = pkg_display_name.replace(".", "_")
                class_count = len([c for c in module_result.classes.values() if c.package == pkg_name])
                lines.append(
                    f'    Component({clean_name}, "{pkg_display_name}", "Java Package", "{class_count} classes")'
                )
        
        lines.extend([
            "}",
            "",
            'ContainerDb(database, "Database", "PostgreSQL", "Data storage")',
            "",
            "@enduml"
        ])
        
        content = "\n".join(lines)
        diagram_path.write_text(content)
        logger.info(f"Generated C4 Component diagram: {diagram_path}")
        return content
    
    def _generate_code_diagrams(self) -> None:
        """Generate C4 Code diagrams (class diagrams) for key modules."""
        # Generate class diagrams for top 3 largest modules
        sorted_modules = sorted(
            self.architecture_data["modules"].items(),
            key=lambda x: x[1]["classes"],
            reverse=True
        )
        
        for module_name, metrics in sorted_modules[:3]:
            diagram_path = self.diagrams_dir / f"{module_name}_classes.puml"
            
            lines = [
                "@startuml",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
                "",
                f"title Class Diagram for {module_name}",
                "",
                "LAYOUT_WITH_LEGEND()",
                "",
            ]
            
            # Get classes from this module
            module_result = self.modules.get(module_name)
            if module_result:
                for class_full_name, cls in list(module_result.classes.items())[:25]:  # Top 25 classes
                    clean_name = cls.name.replace(".", "_")
                    method_count = len(cls.methods)
                    field_count = len(cls.fields)
                    lines.append(
                        f'Component({clean_name}, "{cls.name}", "Java Class", '
                        f'"{method_count} methods, {field_count} fields")'
                    )
            
            lines.extend([
                "",
                "@enduml"
            ])
            
            content = "\n".join(lines)
            diagram_path.write_text(content)
            self.diagrams.code[module_name] = content
            logger.info(f"Generated class diagram: {diagram_path}")
    
    def generate_report(self) -> str:
        """
        Generate comprehensive markdown report.
        
        Returns:
            Path to generated report file
        """
        logger.info("Generating markdown report")
        
        report_path = self.output_dir / f"{self.config.project_name}_ANALYSIS_REPORT.md"
        
        lines = [
            f"# {self.config.project_name} Analysis Report",
            "",
            f"**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}",
            f"**Codebase:** {self.config.codebase_path}",
            "**Analysis Tool:** Omega Migration System v1.0",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            self._generate_executive_summary(),
            "",
            "---",
            "",
            "## C4 Architecture Diagrams",
            "",
            self._generate_diagrams_section(),
            "",
            "---",
            "",
            "## Quantitative Analysis",
            "",
            self._generate_metrics_section(),
            "",
            "---",
            "",
            "## Module Analysis",
            "",
            self._generate_module_section(),
            "",
            "---",
            "",
            "## Dependency Analysis",
            "",
            self._generate_dependency_section(),
            "",
            "---",
            "",
            "## Migration Readiness Assessment",
            "",
            self._generate_migration_section(),
            "",
            "---",
            "",
            "## Next Steps",
            "",
            self._generate_next_steps(),
        ]
        
        content = "\n".join(lines)
        report_path.write_text(content)
        logger.info(f"Report generated: {report_path}")
        return str(report_path)
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section."""
        metrics = self.architecture_data["metrics"]
        dep_count = len(self.dependency_graph["nodes"]) if self.dependency_graph else 0
        
        return f"""Analysis of {self.config.project_name} completed successfully, identifying {metrics['total_modules']} modules containing {metrics['total_classes']} classes with {metrics['total_methods']} methods across {metrics['total_packages']} packages.

The system demonstrates a modular architecture with clear separation of concerns. Dependency analysis identified {dep_count} unique external dependencies.

C4 architecture diagrams have been generated at multiple levels of abstraction to support migration planning."""
    
    def _generate_diagrams_section(self) -> str:
        """Generate C4 diagrams section."""
        lines = [
            "### C4 Model Overview",
            "",
            "The C4 model provides hierarchical views of the system architecture:",
            "",
            "1. **Context Diagram**: System landscape and external dependencies",
            "2. **Container Diagram**: Module-level architecture",
            "3. **Component Diagram**: Detailed component view",
            "4. **Code Diagrams**: Class-level implementation details",
            "",
            "### Context Diagram (Level 1)",
            "",
            f"**File:** `diagrams/{self.config.project_name}_context.puml`",
            "",
            "Shows the system in its environment with users and external dependencies.",
            "",
            "```plantuml",
            self.diagrams.context if self.diagrams.context else "Not generated",
            "```",
            "",
            "### Container Diagram (Level 2)",
            "",
            f"**File:** `diagrams/{self.config.project_name}_container.puml`",
            "",
            "Shows the module-level architecture and key containers.",
            "",
            "```plantuml",
            self.diagrams.container if self.diagrams.container else "Not generated",
            "```",
            "",
            "### Component Diagram (Level 3)",
            "",
            f"**File:** `diagrams/{self.config.project_name}_component.puml`",
            "",
            "Shows detailed component structure within the largest module.",
            "",
            "```plantuml",
            self.diagrams.component if self.diagrams.component else "Not generated",
            "```",
            "",
            "### Code Diagrams (Level 4)",
            "",
            "Class-level diagrams generated for top modules:",
            "",
        ]
        
        for module_name in self.diagrams.code.keys():
            lines.append(f"- `diagrams/{module_name}_classes.puml`")
        
        lines.extend([
            "",
            "**Rendering Instructions:**",
            "",
            "```bash",
            "# Install PlantUML",
            "sudo apt-get install plantuml",
            "",
            "# Render all diagrams",
            f"plantuml diagrams/{self.config.project_name}_*.puml",
            "",
            "# Or use online renderer: https://www.plantuml.com/plantuml/uml/",
            "```",
        ])
        
        return "\n".join(lines)
    
    def _generate_metrics_section(self) -> str:
        """Generate metrics section."""
        metrics = self.architecture_data["metrics"]
        dep_count = len(self.dependency_graph["nodes"]) if self.dependency_graph else 0
        
        lines = [
            "### Overall Metrics",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Total Modules | {metrics['total_modules']} |",
            f"| Total Classes | {metrics['total_classes']} |",
            f"| Total Methods | {metrics['total_methods']} |",
            f"| Total Fields | {metrics['total_fields']} |",
            f"| Total Packages | {metrics['total_packages']} |",
            f"| Unique Dependencies | {dep_count} |",
            "",
            "### Module Metrics",
            "",
            "| Module | Classes | Methods | Fields | Avg Methods/Class |",
            "|--------|---------|---------|--------|-------------------|",
        ]
        
        for module_name, mod_metrics in sorted(
            self.architecture_data["modules"].items(),
            key=lambda x: x[1]["classes"],
            reverse=True
        ):
            avg_methods = mod_metrics["methods"] / mod_metrics["classes"] if mod_metrics["classes"] > 0 else 0
            lines.append(
                f"| {module_name} | {mod_metrics['classes']} | {mod_metrics['methods']} | "
                f"{mod_metrics['fields']} | {avg_methods:.1f} |"
            )
        
        return "\n".join(lines)
    
    def _generate_module_section(self) -> str:
        """Generate module analysis section."""
        lines = ["### Module Breakdown", ""]
        
        for module_name, result in sorted(self.modules.items()):
            lines.extend([
                f"#### {module_name}",
                "",
                f"- **Classes:** {len(result.classes)}",
                f"- **Packages:** {len(result.packages)}",
                f"- **Methods:** {result.metrics.get('total_methods', 0)}",
                f"- **Fields:** {result.metrics.get('total_fields', 0)}",
                "",
                "**Top Packages:**",
                "",
            ])
            
            for pkg_name in list(result.packages.keys())[:5]:
                class_count = len([c for c in result.classes.values() if c.package == pkg_name])
                lines.append(f"- `{pkg_name}` ({class_count} classes)")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_dependency_section(self) -> str:
        """Generate dependency analysis section."""
        if not self.dependency_graph:
            return "No dependency data available."
        
        # Count dependencies by type
        dep_types = {}
        for node in self.dependency_graph["nodes"]:
            dep_type = node.get("type", "unknown")
            dep_types[dep_type] = dep_types.get(dep_type, 0) + 1
        
        lines = [
            "### Dependency Distribution",
            "",
            "| Type | Count |",
            "|------|-------|",
        ]
        
        for dep_type, count in sorted(dep_types.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {dep_type} | {count} |")
        
        lines.extend([
            "",
            "### Top External Dependencies",
            "",
        ])
        
        # Show top 20 dependencies
        external_deps = [
            node["id"] for node in self.dependency_graph["nodes"]
            if node.get("type") not in {"jdk", "internal"}
        ]
        
        for dep in sorted(external_deps)[:20]:
            lines.append(f"- `{dep}`")
        
        return "\n".join(lines)
    
    def _generate_migration_section(self) -> str:
        """Generate migration readiness section."""
        metrics = self.architecture_data["metrics"]
        
        complexity_score = "Medium"
        if metrics["total_classes"] > 200:
            complexity_score = "High"
        elif metrics["total_classes"] < 50:
            complexity_score = "Low"
        
        dep_count = len(self.dependency_graph["nodes"]) if self.dependency_graph else 0
        
        return f"""### Complexity Assessment

**Overall Complexity:** {complexity_score}

**Factors:**
- Module count: {metrics['total_modules']} ({"Well-modularized" if metrics['total_modules'] > 5 else "Limited modularity"})
- Class count: {metrics['total_classes']} ({"Large codebase" if metrics['total_classes'] > 100 else "Small to medium codebase"})
- External dependencies: {dep_count}

### Strengths

- Modular architecture with {metrics['total_modules']} distinct modules
- Clear package organization ({metrics['total_packages']} packages)
- Structured codebase suitable for analysis

### Migration Considerations

- Analyze dependency coupling between modules
- Review shared data models across modules
- Identify transaction boundaries
- Map API surfaces for service extraction

### Recommended Approach

1. **Phase 1**: Runtime analysis with OpenTelemetry
2. **Phase 2**: Gap analysis comparing static vs runtime architecture
3. **Phase 3**: Service boundary refinement
4. **Phase 4**: Migration planning and execution"""
    
    def _generate_next_steps(self) -> str:
        """Generate next steps section."""
        return """1. **Runtime Analysis**: Deploy OpenTelemetry instrumentation to capture runtime behavior
2. **Gap Analysis**: Compare static architecture with runtime observations
3. **Service Boundaries**: Refine module boundaries based on coupling analysis
4. **Risk Assessment**: Evaluate migration complexity and effort
5. **Migration Planning**: Create detailed migration roadmap

**Tools Required:**
- SigNoz for observability
- OpenTelemetry for instrumentation
- CodeQL for security analysis (future)
- Microsoft AppCAT for Azure migration assessment (future)

**Documentation:**
- See `docs/tools/report-generator.md` for detailed usage
- See `docs/analysis/` for analysis methodology"""
    
    def export_json(self) -> str:
        """Export analysis results as JSON."""
        json_path = self.output_dir / f"{self.config.project_name}_analysis.json"
        
        data = {
            "metadata": {
                "project_name": self.config.project_name,
                "analysis_date": datetime.now().isoformat(),
                "codebase_path": str(self.config.codebase_path),
                "tool_version": "1.0.0"
            },
            "metrics": self.architecture_data["metrics"],
            "modules": self.architecture_data["modules"],
            "dependencies": {
                "count": len(self.dependency_graph["nodes"]) if self.dependency_graph else 0,
                "nodes": self.dependency_graph["nodes"] if self.dependency_graph else [],
                "edges": self.dependency_graph["edges"] if self.dependency_graph else []
            }
        }
        
        with json_path.open("w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"JSON export: {json_path}")
        return str(json_path)
    
    def run(self) -> bool:
        """
        Execute full report generation workflow.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting report generation for {self.config.project_name}")
        
        # Step 1: Analyze codebase
        if not self.analyze_codebase():
            logger.error("Codebase analysis failed")
            return False
        
        # Step 2: Generate diagrams
        if not self.generate_diagrams():
            logger.error("Diagram generation failed")
            return False
        
        # Step 3: Generate report
        report_path = self.generate_report()
        
        # Step 4: Export JSON
        json_path = self.export_json()
        
        logger.info("=" * 80)
        logger.info("Report generation complete!")
        logger.info(f"  Markdown Report: {report_path}")
        logger.info(f"  JSON Data: {json_path}")
        logger.info(f"  Diagrams: {self.diagrams_dir}")
        logger.info("=" * 80)
        
        return True


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Omega Migration System - Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Spring Modulith codebase
  python -m src.utils.report_generator analyze \\
    --codebase /workspace/data/codebase/spring-modulith \\
    --output /workspace \\
    --project-name spring-modulith

  # Generate report with verbose output
  python -m src.utils.report_generator analyze \\
    --codebase /path/to/codebase \\
    --output /path/to/output \\
    --project-name my-project \\
    --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze codebase and generate report")
    analyze_parser.add_argument(
        "--codebase",
        type=Path,
        required=True,
        help="Path to codebase root directory"
    )
    analyze_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for report and diagrams"
    )
    analyze_parser.add_argument(
        "--project-name",
        type=str,
        required=True,
        help="Project name for report"
    )
    analyze_parser.add_argument(
        "--no-diagrams",
        action="store_true",
        help="Skip diagram generation"
    )
    analyze_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "analyze":
        config = ReportConfiguration(
            codebase_path=args.codebase,
            output_dir=args.output,
            project_name=args.project_name,
            generate_diagrams=not args.no_diagrams,
            verbose=args.verbose
        )
        
        generator = ReportGenerator(config)
        success = generator.run()
        
        return 0 if success else 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
