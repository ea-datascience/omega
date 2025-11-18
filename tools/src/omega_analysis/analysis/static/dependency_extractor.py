"""Dependency analysis and extraction for Java applications."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
import re
import xml.etree.ElementTree as ET

from .java_parser import JavaSourceAnalyzer, JavaClass

logger = logging.getLogger(__name__)


@dataclass
@dataclass(frozen=True)
class Dependency:
    """Represents a single dependency."""
    group_id: str
    artifact_id: str
    version: str
    scope: str
    type: str
    classifier: Optional[str] = None


@dataclass(frozen=True)
class DependencyGraph:
    """Represents the dependency graph of the application."""
    internal_dependencies: Dict[str, Set[str]]  # class -> set of classes it depends on
    external_dependencies: Dict[str, Set[Dependency]]  # class -> set of external deps
    package_dependencies: Dict[str, Set[str]]  # package -> set of packages it depends on
    maven_dependencies: List[Dependency]
    gradle_dependencies: List[Dependency]
    transitive_dependencies: Dict[str, Set[str]]
    circular_dependencies: List[List[str]]


@dataclass
class DependencyMetrics:
    """Metrics about dependencies."""
    total_classes: int
    total_dependencies: int
    average_dependencies_per_class: float
    max_dependencies: int
    min_dependencies: int
    coupling_factor: float
    instability: Dict[str, float]  # package -> instability metric
    abstractness: Dict[str, float]  # package -> abstractness metric
    distance_from_main_sequence: Dict[str, float]  # package -> distance metric


class DependencyExtractor:
    """Extracts and analyzes dependencies from Java applications."""
    
    def __init__(self):
        self.java_analyzer = JavaSourceAnalyzer()
    
    def analyze_dependencies(self, source_path: Path) -> DependencyGraph:
        """Analyze all dependencies in a Java project."""
        logger.info(f"Analyzing dependencies for: {source_path}")
        
        # Analyze Java source code
        java_analysis = self.java_analyzer.analyze_directory(source_path)
        classes = java_analysis["classes"]
        
        # Extract internal dependencies (class-to-class)
        internal_deps = self._extract_internal_dependencies(classes)
        
        # Extract external dependencies
        external_deps = self._extract_external_dependencies(classes)
        
        # Build package-level dependencies
        package_deps = self._build_package_dependencies(internal_deps, classes)
        
        # Parse build files for Maven/Gradle dependencies
        maven_deps = self._parse_maven_dependencies(source_path)
        gradle_deps = self._parse_gradle_dependencies(source_path)
        
        # Calculate transitive dependencies
        transitive_deps = self._calculate_transitive_dependencies(internal_deps)
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(internal_deps)
        
        dependency_graph = DependencyGraph(
            internal_dependencies=internal_deps,
            external_dependencies=external_deps,
            package_dependencies=package_deps,
            maven_dependencies=maven_deps,
            gradle_dependencies=gradle_deps,
            transitive_dependencies=transitive_deps,
            circular_dependencies=circular_deps
        )
        
        logger.info(f"Dependency analysis complete: {len(internal_deps)} classes analyzed")
        return dependency_graph
    
    def _extract_internal_dependencies(self, classes: Dict[str, JavaClass]) -> Dict[str, Set[str]]:
        """Extract dependencies between classes within the project."""
        internal_deps = {}
        
        # Build a set of all internal class names for faster lookup
        internal_classes = set(classes.keys())
        
        for class_name, java_class in classes.items():
            class_deps = set()
            
            # Check imports for internal dependencies
            for import_stmt in java_class.imports:
                if import_stmt in internal_classes:
                    class_deps.add(import_stmt)
            
            # Check field types for internal dependencies
            for field in java_class.fields:
                field_type = self._resolve_type(field.type, java_class.imports, internal_classes)
                if field_type and field_type in internal_classes:
                    class_deps.add(field_type)
            
            # Check method parameters and return types
            for method in java_class.methods:
                # Return type
                return_type = self._resolve_type(method.return_type, java_class.imports, internal_classes)
                if return_type and return_type in internal_classes:
                    class_deps.add(return_type)
                
                # Parameter types
                for param in method.parameters:
                    param_type = self._resolve_type(param["type"], java_class.imports, internal_classes)
                    if param_type and param_type in internal_classes:
                        class_deps.add(param_type)
            
            # Check inheritance
            if java_class.extends:
                extends_type = self._resolve_type(java_class.extends, java_class.imports, internal_classes)
                if extends_type and extends_type in internal_classes:
                    class_deps.add(extends_type)
            
            # Check interfaces
            for interface in java_class.implements:
                interface_type = self._resolve_type(interface, java_class.imports, internal_classes)
                if interface_type and interface_type in internal_classes:
                    class_deps.add(interface_type)
            
            internal_deps[class_name] = class_deps
        
        return internal_deps
    
    def _resolve_type(self, type_name: str, imports: List[str], internal_classes: Set[str]) -> Optional[str]:
        """Resolve a type name to a fully qualified class name."""
        if not type_name:
            return None
        
        # Handle generic types (e.g., List<String> -> List)
        base_type = type_name.split('<')[0].split('[')[0]
        
        # Check if it's already fully qualified
        if base_type in internal_classes:
            return base_type
        
        # Check imports for matching type
        for import_stmt in imports:
            if import_stmt.endswith('.' + base_type):
                return import_stmt
        
        return None
    
    def _extract_external_dependencies(self, classes: Dict[str, JavaClass]) -> Dict[str, Set[Dependency]]:
        """Extract external library dependencies for each class."""
        external_deps = {}
        
        # Common framework mappings
        framework_mappings = {
            'org.springframework': {'group_id': 'org.springframework', 'artifact_id': 'spring-core', 'version': 'unknown', 'scope': 'compile', 'type': 'jar'},
            'javax.persistence': {'group_id': 'javax.persistence', 'artifact_id': 'javax.persistence-api', 'version': 'unknown', 'scope': 'compile', 'type': 'jar'},
            'org.hibernate': {'group_id': 'org.hibernate', 'artifact_id': 'hibernate-core', 'version': 'unknown', 'scope': 'compile', 'type': 'jar'},
            'com.fasterxml.jackson': {'group_id': 'com.fasterxml.jackson.core', 'artifact_id': 'jackson-core', 'version': 'unknown', 'scope': 'compile', 'type': 'jar'}
        }
        
        for class_name, java_class in classes.items():
            class_external_deps = set()
            
            # Analyze imports for external dependencies
            for import_stmt in java_class.imports:
                for framework_prefix, dep_info in framework_mappings.items():
                    if import_stmt.startswith(framework_prefix):
                        dependency = Dependency(**dep_info)
                        class_external_deps.add(dependency)
                        break
            
            # Analyze annotations for framework dependencies
            for annotation in java_class.annotations:
                if annotation in ['Entity', 'Table', 'Column', 'Id', 'GeneratedValue']:
                    # JPA dependency
                    dependency = Dependency(
                        group_id='javax.persistence',
                        artifact_id='javax.persistence-api',
                        version='unknown',
                        scope='compile',
                        type='jar'
                    )
                    class_external_deps.add(dependency)
                elif annotation in ['Service', 'Repository', 'Controller', 'Component', 'Autowired']:
                    # Spring dependency
                    dependency = Dependency(
                        group_id='org.springframework',
                        artifact_id='spring-context',
                        version='unknown',
                        scope='compile',
                        type='jar'
                    )
                    class_external_deps.add(dependency)
            
            external_deps[class_name] = class_external_deps
        
        return external_deps
    
    def _build_package_dependencies(self, internal_deps: Dict[str, Set[str]], 
                                   classes: Dict[str, JavaClass]) -> Dict[str, Set[str]]:
        """Build package-level dependency graph."""
        package_deps = {}
        
        # Create mapping from class to package
        class_to_package = {class_name: java_class.package 
                           for class_name, java_class in classes.items()}
        
        # Build package dependencies
        for class_name, class_deps in internal_deps.items():
            if class_name not in class_to_package:
                continue
                
            source_package = class_to_package[class_name]
            
            if source_package not in package_deps:
                package_deps[source_package] = set()
            
            for dep_class in class_deps:
                if dep_class in class_to_package:
                    target_package = class_to_package[dep_class]
                    if target_package != source_package:  # Don't include self-dependencies
                        package_deps[source_package].add(target_package)
        
        return package_deps
    
    def _parse_maven_dependencies(self, source_path: Path) -> List[Dependency]:
        """Parse Maven pom.xml files for dependencies."""
        dependencies = []
        pom_files = list(source_path.rglob("pom.xml"))
        
        for pom_file in pom_files:
            try:
                tree = ET.parse(pom_file)
                root = tree.getroot()
                
                # Handle namespace
                namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                if root.tag.startswith('{'):
                    ns = root.tag.split('}')[0] + '}'
                    namespace = {'maven': ns.strip('{')}
                
                # Find dependencies
                deps_element = root.find('.//maven:dependencies', namespace)
                if deps_element is not None:
                    for dep_element in deps_element.findall('.//maven:dependency', namespace):
                        group_id = self._get_element_text(dep_element, './/maven:groupId', namespace)
                        artifact_id = self._get_element_text(dep_element, './/maven:artifactId', namespace)
                        version = self._get_element_text(dep_element, './/maven:version', namespace) or 'unknown'
                        scope = self._get_element_text(dep_element, './/maven:scope', namespace) or 'compile'
                        dep_type = self._get_element_text(dep_element, './/maven:type', namespace) or 'jar'
                        classifier = self._get_element_text(dep_element, './/maven:classifier', namespace)
                        
                        if group_id and artifact_id:
                            dependency = Dependency(
                                group_id=group_id,
                                artifact_id=artifact_id,
                                version=version,
                                scope=scope,
                                type=dep_type,
                                classifier=classifier
                            )
                            dependencies.append(dependency)
                
            except ET.ParseError as e:
                logger.warning(f"Failed to parse {pom_file}: {e}")
            except Exception as e:
                logger.error(f"Error processing {pom_file}: {e}")
        
        logger.info(f"Found {len(dependencies)} Maven dependencies")
        return dependencies
    
    def _get_element_text(self, parent, xpath: str, namespace: dict) -> Optional[str]:
        """Safely get text from XML element."""
        element = parent.find(xpath, namespace)
        return element.text if element is not None else None
    
    def _parse_gradle_dependencies(self, source_path: Path) -> List[Dependency]:
        """Parse Gradle build.gradle files for dependencies."""
        dependencies = []
        gradle_files = list(source_path.rglob("build.gradle")) + list(source_path.rglob("build.gradle.kts"))
        
        dependency_patterns = [
            r"implementation\s+['\"]([^'\"]+)['\"]",
            r"compile\s+['\"]([^'\"]+)['\"]",
            r"api\s+['\"]([^'\"]+)['\"]",
            r"testImplementation\s+['\"]([^'\"]+)['\"]"
        ]
        
        for gradle_file in gradle_files:
            try:
                with open(gradle_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in dependency_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        parts = match.split(':')
                        if len(parts) >= 2:
                            group_id = parts[0]
                            artifact_id = parts[1]
                            version = parts[2] if len(parts) > 2 else 'unknown'
                            
                            dependency = Dependency(
                                group_id=group_id,
                                artifact_id=artifact_id,
                                version=version,
                                scope='compile',
                                type='jar'
                            )
                            dependencies.append(dependency)
                
            except Exception as e:
                logger.error(f"Error processing {gradle_file}: {e}")
        
        logger.info(f"Found {len(dependencies)} Gradle dependencies")
        return dependencies
    
    def _calculate_transitive_dependencies(self, internal_deps: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """Calculate transitive dependencies using graph traversal."""
        transitive_deps = {}
        
        def get_all_dependencies(class_name: str, visited: Set[str]) -> Set[str]:
            if class_name in visited:
                return set()  # Avoid cycles
            
            visited.add(class_name)
            all_deps = set()
            
            # Direct dependencies
            direct_deps = internal_deps.get(class_name, set())
            all_deps.update(direct_deps)
            
            # Transitive dependencies
            for dep in direct_deps:
                transitive = get_all_dependencies(dep, visited.copy())
                all_deps.update(transitive)
            
            return all_deps
        
        for class_name in internal_deps:
            transitive_deps[class_name] = get_all_dependencies(class_name, set())
        
        return transitive_deps
    
    def _detect_circular_dependencies(self, internal_deps: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found a cycle, extract it
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                circular_deps.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visit all dependencies
            for dep in internal_deps.get(node, set()):
                if dfs(dep, path.copy()):
                    break  # Stop after finding first cycle from this node
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes
        for class_name in internal_deps:
            if class_name not in visited:
                dfs(class_name, [])
        
        return circular_deps
    
    def calculate_metrics(self, dependency_graph: DependencyGraph, 
                         classes: Dict[str, JavaClass]) -> DependencyMetrics:
        """Calculate various dependency metrics."""
        
        internal_deps = dependency_graph.internal_dependencies
        package_deps = dependency_graph.package_dependencies
        
        # Basic metrics
        total_classes = len(internal_deps)
        total_dependencies = sum(len(deps) for deps in internal_deps.values())
        avg_deps = total_dependencies / total_classes if total_classes > 0 else 0
        
        dep_counts = [len(deps) for deps in internal_deps.values()]
        max_deps = max(dep_counts) if dep_counts else 0
        min_deps = min(dep_counts) if dep_counts else 0
        
        # Coupling factor (percentage of possible dependencies that exist)
        max_possible_deps = total_classes * (total_classes - 1)  # n*(n-1)
        coupling_factor = total_dependencies / max_possible_deps if max_possible_deps > 0 else 0
        
        # Package-level metrics
        instability = self._calculate_instability(package_deps, classes)
        abstractness = self._calculate_abstractness(classes)
        distance = self._calculate_distance_from_main_sequence(instability, abstractness)
        
        return DependencyMetrics(
            total_classes=total_classes,
            total_dependencies=total_dependencies,
            average_dependencies_per_class=round(avg_deps, 2),
            max_dependencies=max_deps,
            min_dependencies=min_deps,
            coupling_factor=round(coupling_factor, 4),
            instability=instability,
            abstractness=abstractness,
            distance_from_main_sequence=distance
        )
    
    def _calculate_instability(self, package_deps: Dict[str, Set[str]], 
                              classes: Dict[str, JavaClass]) -> Dict[str, float]:
        """Calculate instability metric for each package (I = Ce / (Ca + Ce))."""
        instability = {}
        
        # Calculate efferent (Ce) and afferent (Ca) coupling for each package
        efferent = {}  # outgoing dependencies
        afferent = {}  # incoming dependencies
        
        # Initialize
        all_packages = set()
        for class_name, java_class in classes.items():
            all_packages.add(java_class.package)
        
        for package in all_packages:
            efferent[package] = len(package_deps.get(package, set()))
            afferent[package] = 0
        
        # Count afferent dependencies
        for source_package, target_packages in package_deps.items():
            for target_package in target_packages:
                if target_package in afferent:
                    afferent[target_package] += 1
        
        # Calculate instability
        for package in all_packages:
            ca = afferent[package]
            ce = efferent[package]
            total = ca + ce
            
            if total == 0:
                instability[package] = 0.0
            else:
                instability[package] = round(ce / total, 3)
        
        return instability
    
    def _calculate_abstractness(self, classes: Dict[str, JavaClass]) -> Dict[str, float]:
        """Calculate abstractness metric for each package (A = abstract_classes / total_classes)."""
        abstractness = {}
        
        # Group classes by package
        package_classes = {}
        for class_name, java_class in classes.items():
            package = java_class.package
            if package not in package_classes:
                package_classes[package] = []
            package_classes[package].append(java_class)
        
        # Calculate abstractness for each package
        for package, pkg_classes in package_classes.items():
            total_classes = len(pkg_classes)
            abstract_classes = sum(1 for cls in pkg_classes 
                                 if cls.is_abstract or cls.is_interface)
            
            if total_classes == 0:
                abstractness[package] = 0.0
            else:
                abstractness[package] = round(abstract_classes / total_classes, 3)
        
        return abstractness
    
    def _calculate_distance_from_main_sequence(self, instability: Dict[str, float], 
                                             abstractness: Dict[str, float]) -> Dict[str, float]:
        """Calculate distance from main sequence (D = |A + I - 1|)."""
        distance = {}
        
        for package in instability:
            if package in abstractness:
                a = abstractness[package]
                i = instability[package]
                d = abs(a + i - 1)
                distance[package] = round(d, 3)
        
        return distance