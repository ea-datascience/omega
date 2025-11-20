"""
Spring Boot Project Analyzer

This module provides source code analysis for Spring Boot applications to identify
bounded contexts, modules, and dependencies without requiring compiled classes.

Unlike Context Mapper's reflection-based approach (which requires .class files),
this analyzer reads Java source code directly to extract architectural information.

Features:
- Spring Boot application detection
- Module/package structure analysis
- Service and entity classification
- Inter-module dependency detection
- CML (Context Mapping Language) generation
- JSON report generation

Dependencies:
- Python 3.12+
- pathlib (standard library)
- re (standard library)
- json (standard library)
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class SpringBootAnalyzerError(Exception):
    """Base exception for Spring Boot analyzer operations"""
    pass


@dataclass
class ModuleInfo:
    """Information about a Spring Boot module/package"""
    name: str
    package: str
    entities: List[str]
    services: List[str]
    events: List[str]
    repositories: List[str]
    controllers: List[str]
    all_classes: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ModuleDependency:
    """Dependency between two modules"""
    from_module: str
    to_module: str
    dependency_type: str = "imports"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "from": self.from_module,
            "to": self.to_module,
            "type": self.dependency_type
        }


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    application_class: str
    base_package: str
    modules: List[ModuleInfo]
    dependencies: List[ModuleDependency]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "application": self.application_class,
            "base_package": self.base_package,
            "modules": [m.to_dict() for m in self.modules],
            "dependencies": [d.to_dict() for d in self.dependencies]
        }


class SpringBootAnalyzer:
    """
    Analyzer for Spring Boot applications to extract architectural information.
    
    This analyzer reads Java source code to identify modules, services, entities,
    and dependencies without requiring compiled classes.
    """
    
    # Patterns for identifying different types of classes
    ANNOTATION_PATTERNS = {
        'entity': [r'@Entity\b', r'@Embeddable\b'],
        'service': [r'@Service\b', r'@Component\b'],
        'repository': [r'@Repository\b'],
        'controller': [r'@Controller\b', r'@RestController\b'],
        'event': [r'@DomainEvent\b'],
        'spring_boot_app': [r'@SpringBootApplication\b']
    }
    
    def __init__(self):
        """Initialize Spring Boot Analyzer"""
        pass
    
    def analyze_project(
        self,
        project_path: Path,
        base_package: str
    ) -> AnalysisResult:
        """
        Analyze a Spring Boot project.
        
        Args:
            project_path: Path to Spring Boot project root
            base_package: Base Java package (e.g., "com.example.app")
            
        Returns:
            AnalysisResult containing modules, dependencies, and metadata
            
        Raises:
            SpringBootAnalyzerError: If project structure is invalid
        """
        if not project_path.exists():
            raise SpringBootAnalyzerError(
                f"Project path does not exist: {project_path}"
            )
        
        # Find source directory
        src_dir = project_path / 'src' / 'main' / 'java'
        if not src_dir.exists():
            raise SpringBootAnalyzerError(
                f"Source directory not found: {src_dir}"
            )
        
        # Convert package to path
        package_path = src_dir / base_package.replace('.', '/')
        if not package_path.exists():
            raise SpringBootAnalyzerError(
                f"Package path not found: {package_path}. "
                f"Base package '{base_package}' may be incorrect."
            )
        
        logger.info(f"Analyzing Spring Boot project: {project_path.name}")
        logger.info(f"Base package: {base_package}")
        
        # Find Spring Boot Application class
        application_class = self._find_spring_boot_application(package_path)
        if not application_class:
            raise SpringBootAnalyzerError(
                f"No @SpringBootApplication class found in {package_path}"
            )
        
        logger.info(f"Found Spring Boot Application: {application_class}")
        
        # Analyze modules
        modules = self._analyze_modules(package_path, base_package)
        logger.info(f"Found {len(modules)} modules")
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies(modules, package_path)
        logger.info(f"Found {len(dependencies)} inter-module dependencies")
        
        return AnalysisResult(
            application_class=application_class,
            base_package=base_package,
            modules=modules,
            dependencies=dependencies
        )
    
    def _find_spring_boot_application(self, package_path: Path) -> Optional[str]:
        """Find the @SpringBootApplication class"""
        for java_file in package_path.glob('*.java'):
            content = java_file.read_text()
            if self._has_annotation(content, 'spring_boot_app'):
                return java_file.stem
        return None
    
    def _analyze_modules(
        self,
        package_path: Path,
        base_package: str
    ) -> List[ModuleInfo]:
        """Analyze all modules (subdirectories) in the package"""
        modules = []
        
        for subdir in package_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('_'):
                module_package = f"{base_package}.{subdir.name}"
                module_info = self._analyze_module(subdir, subdir.name, module_package)
                modules.append(module_info)
        
        return modules
    
    def _analyze_module(
        self,
        module_path: Path,
        module_name: str,
        package_name: str
    ) -> ModuleInfo:
        """Analyze a single module"""
        entities = []
        services = []
        events = []
        repositories = []
        controllers = []
        all_classes = []
        
        # Scan all Java files recursively
        for java_file in module_path.rglob('*.java'):
            if java_file.stem == 'package-info':
                continue
                
            content = java_file.read_text()
            class_name = java_file.stem
            
            all_classes.append(class_name)
            
            # Classify by annotations/keywords
            if self._has_annotation(content, 'entity'):
                entities.append(class_name)
            elif self._has_annotation(content, 'repository'):
                repositories.append(class_name)
            elif self._has_annotation(content, 'controller'):
                controllers.append(class_name)
            elif self._has_annotation(content, 'service'):
                services.append(class_name)
            elif self._has_annotation(content, 'event') or 'Event' in class_name:
                events.append(class_name)
        
        return ModuleInfo(
            name=module_name,
            package=package_name,
            entities=entities,
            services=services,
            events=events,
            repositories=repositories,
            controllers=controllers,
            all_classes=all_classes
        )
    
    def _has_annotation(self, content: str, annotation_type: str) -> bool:
        """Check if content has specific annotation type"""
        patterns = self.ANNOTATION_PATTERNS.get(annotation_type, [])
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def _analyze_dependencies(
        self,
        modules: List[ModuleInfo],
        base_path: Path
    ) -> List[ModuleDependency]:
        """Analyze dependencies between modules"""
        dependencies = []
        seen_deps = set()
        
        for module in modules:
            module_path = base_path / module.name
            
            # Scan all files in this module for imports
            for java_file in module_path.rglob('*.java'):
                content = java_file.read_text()
                
                # Find imports
                import_pattern = r'import\s+([a-zA-Z0-9_.]+);'
                imports = re.findall(import_pattern, content)
                
                for imp in imports:
                    # Check if this import references another module
                    for other_module in modules:
                        if other_module.name != module.name:
                            if other_module.package in imp:
                                dep_key = (module.name, other_module.name)
                                if dep_key not in seen_deps:
                                    dependencies.append(
                                        ModuleDependency(
                                            from_module=module.name,
                                            to_module=other_module.name,
                                            dependency_type="imports"
                                        )
                                    )
                                    seen_deps.add(dep_key)
        
        return dependencies
    
    def generate_cml(
        self,
        analysis: AnalysisResult,
        output_path: Path
    ) -> str:
        """
        Generate Context Mapper Language (CML) file from analysis.
        
        Args:
            analysis: AnalysisResult from analyze_project()
            output_path: Path to write CML file
            
        Returns:
            CML content as string
        """
        lines = []
        lines.append("/* Spring Boot Application Context Map */")
        lines.append(f"/* Application: {analysis.application_class} */")
        lines.append(f"/* Base Package: {analysis.base_package} */")
        lines.append(f"/* Modules: {len(analysis.modules)} */")
        lines.append(f"/* Generated: 2025-11-20 */")
        lines.append("")
        
        # Context Map
        module_names = [m.name for m in analysis.modules]
        lines.append("ContextMap ApplicationContextMap {")
        lines.append(f"  contains {', '.join(module_names)}")
        lines.append("")
        
        if analysis.dependencies:
            lines.append("  /* Inter-Module Dependencies */")
            for dep in analysis.dependencies:
                # D = Downstream, ACL = Anti-Corruption Layer
                # U = Upstream, OHS = Open Host Service
                lines.append(
                    f"  {dep.from_module} [D,ACL] -> [U,OHS] {dep.to_module}"
                )
            lines.append("")
        
        lines.append("}")
        lines.append("")
        
        # Bounded Contexts (one per module)
        for module in analysis.modules:
            lines.append(f"BoundedContext {module.name} {{")
            lines.append(f"  type = MODULE")
            lines.append(f"  domainVisionStatement = \"{module.package}\"")
            lines.append("")
            
            # Add aggregates if we have domain objects
            if module.entities or module.services or module.events:
                lines.append("  Aggregate {")
                
                for entity in module.entities:
                    lines.append(f"    Entity {entity}")
                
                for service in module.services:
                    lines.append(f"    Service {service}")
                
                for event in module.events:
                    lines.append(f"    DomainEvent {event}")
                
                lines.append("  }")
                lines.append("")
            
            lines.append("}")
            lines.append("")
        
        cml_content = "\n".join(lines)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cml_content)
        
        logger.info(f"CML file written to: {output_path}")
        
        return cml_content
    
    def generate_json_report(
        self,
        analysis: AnalysisResult,
        output_path: Path
    ) -> None:
        """
        Generate JSON report from analysis.
        
        Args:
            analysis: AnalysisResult from analyze_project()
            output_path: Path to write JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)
        
        logger.info(f"JSON report written to: {output_path}")
    
    def print_summary(self, analysis: AnalysisResult) -> None:
        """Print analysis summary to console"""
        print(f"\nSpring Boot Application: {analysis.application_class}")
        print(f"Base Package: {analysis.base_package}")
        print(f"\nModules ({len(analysis.modules)}):")
        
        for module in analysis.modules:
            print(f"  • {module.name}")
            print(f"    - Entities: {len(module.entities)}")
            print(f"    - Services: {len(module.services)}")
            print(f"    - Repositories: {len(module.repositories)}")
            print(f"    - Controllers: {len(module.controllers)}")
            print(f"    - Events: {len(module.events)}")
            print(f"    - Total Classes: {len(module.all_classes)}")
        
        if analysis.dependencies:
            print(f"\nInter-Module Dependencies ({len(analysis.dependencies)}):")
            for dep in analysis.dependencies:
                print(f"  {dep.from_module} -> {dep.to_module}")
        else:
            print("\nNo inter-module dependencies found")


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m src.utils.spring_boot_analyzer <project_path> <base_package>")
        print("Example: python -m src.utils.spring_boot_analyzer /path/to/project com.example.app")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    base_package = sys.argv[2]
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path.cwd()
    
    analyzer = SpringBootAnalyzer()
    
    try:
        # Analyze project
        result = analyzer.analyze_project(project_path, base_package)
        analyzer.print_summary(result)
        
        # Generate outputs
        project_name = project_path.name
        cml_file = output_dir / f"{project_name}_context_map.cml"
        json_file = output_dir / f"{project_name}_analysis.json"
        
        analyzer.generate_cml(result, cml_file)
        analyzer.generate_json_report(result, json_file)
        
        print(f"\n✓ CML file: {cml_file}")
        print(f"✓ JSON report: {json_file}")
        
    except SpringBootAnalyzerError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
