"""Java source code analyzer using tree-sitter for AST parsing and analysis.

This module uses tree-sitter-java for robust Java 17+ syntax support including:
- Records (Java 14+)
- Pattern matching (Java 16+)
- Sealed classes (Java 17+)
- Text blocks and modern Java features

Replaces javalang which lacks support for modern Java syntax.
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
import re

from tree_sitter import Language, Parser, Node
import tree_sitter_java

logger = logging.getLogger(__name__)


@dataclass
class JavaClass:
    """Represents a Java class with its metadata."""
    name: str
    package: str
    full_name: str
    source_file: str
    is_interface: bool
    is_abstract: bool
    extends: Optional[str]
    implements: List[str]
    annotations: List[str]
    methods: List['JavaMethod']
    fields: List['JavaField']
    imports: List[str]
    dependencies: Set[str]


@dataclass 
class JavaMethod:
    """Represents a Java method with its metadata."""
    name: str
    return_type: str
    parameters: List[Dict[str, str]]
    annotations: List[str]
    is_public: bool
    is_private: bool
    is_protected: bool
    is_static: bool
    is_abstract: bool
    line_number: int


@dataclass
class JavaField:
    """Represents a Java field with its metadata."""
    name: str
    type: str
    annotations: List[str]
    is_public: bool
    is_private: bool
    is_protected: bool
    is_static: bool
    is_final: bool
    line_number: int


@dataclass
class JavaPackage:
    """Represents a Java package with its classes."""
    name: str
    classes: List[JavaClass]
    sub_packages: List['JavaPackage']


class JavaSourceAnalyzer:
    """Analyzes Java source code to extract structural information using tree-sitter."""
    
    def __init__(self):
        self.classes: Dict[str, JavaClass] = {}
        self.packages: Dict[str, JavaPackage] = {}
        self.errors: List[str] = []
        
        # Initialize tree-sitter parser
        self.parser = Parser()
        java_language = Language(tree_sitter_java.language())
        self.parser.language = java_language
    
    def analyze_directory(self, source_path: Path) -> Dict[str, Any]:
        """Analyze all Java files in a directory."""
        logger.info(f"Analyzing Java source directory: {source_path}")
        
        if not source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")
        
        java_files = list(source_path.rglob("*.java"))
        logger.info(f"Found {len(java_files)} Java files")
        
        results = {
            "classes": {},
            "packages": {},
            "metrics": {
                "total_files": len(java_files),
                "total_classes": 0,
                "total_methods": 0,
                "total_fields": 0,
                "errors": []
            }
        }
        
        for java_file in java_files:
            try:
                java_class = self.analyze_file(java_file)
                if java_class:
                    results["classes"][java_class.full_name] = java_class
                    results["metrics"]["total_classes"] += 1
                    results["metrics"]["total_methods"] += len(java_class.methods)
                    results["metrics"]["total_fields"] += len(java_class.fields)
                    
            except Exception as e:
                error_msg = f"Error analyzing {java_file}: {str(e)}"
                logger.error(error_msg)
                results["metrics"]["errors"].append(error_msg)
        
        # Organize classes into packages
        results["packages"] = self._organize_packages(results["classes"])
        
        logger.info(f"Analysis complete: {results['metrics']['total_classes']} classes in {len(results['packages'])} packages")
        return results
    
    def analyze_file(self, file_path: Path) -> Optional[JavaClass]:
        """Analyze a single Java file using tree-sitter."""
        logger.debug(f"Analyzing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the Java source code with tree-sitter
            tree = self.parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            # Extract package name
            package_name = self._extract_package_name(root_node, source_code)
            
            # Extract imports
            imports = self._extract_imports(root_node, source_code)
            
            # Find the main class/interface/record in the file
            main_type_node = self._find_main_type(root_node)
            
            if not main_type_node:
                logger.warning(f"No class or interface found in {file_path}")
                return None
            
            # Extract class information
            java_class = self._extract_class_info_from_node(
                main_type_node, package_name, str(file_path), imports, source_code
            )
            
            return java_class
            
        except Exception as e:
            logger.error(f"Unexpected error analyzing {file_path}: {e}")
            return None
    
    def _extract_package_name(self, root_node: Node, source_code: str) -> str:
        """Extract package name from tree-sitter AST."""
        for child in root_node.children:
            if child.type == 'package_declaration':
                # Get the scoped_identifier node
                for node in child.children:
                    if node.type == 'scoped_identifier' or node.type == 'identifier':
                        return self._get_node_text(node, source_code)
        return ""
    
    def _extract_imports(self, root_node: Node, source_code: str) -> List[str]:
        """Extract import statements from tree-sitter AST."""
        imports = []
        for child in root_node.children:
            if child.type == 'import_declaration':
                # Get the imported path
                for node in child.children:
                    if node.type in ('scoped_identifier', 'identifier'):
                        imports.append(self._get_node_text(node, source_code))
        return imports
    
    def _find_main_type(self, root_node: Node) -> Optional[Node]:
        """Find the main class/interface/record/enum declaration."""
        for child in root_node.children:
            if child.type in ('class_declaration', 'interface_declaration', 
                            'record_declaration', 'enum_declaration'):
                return child
        return None
    
    def _get_node_text(self, node: Node, source_code: str) -> str:
        """Extract text content from a tree-sitter node."""
        return source_code[node.start_byte:node.end_byte]
    
    def _extract_class_info_from_node(self, type_node: Node, package_name: str, 
                                     source_file: str, imports: List[str], 
                                     source_code: str) -> JavaClass:
        """Extract detailed information from a class/interface/record node."""
        
        is_interface = type_node.type == 'interface_declaration'
        is_record = type_node.type == 'record_declaration'
        is_enum = type_node.type == 'enum_declaration'
        
        # Extract class name
        class_name = ""
        for child in type_node.children:
            if child.type == 'identifier':
                class_name = self._get_node_text(child, source_code)
                break
        
        # Extract annotations
        annotations = self._extract_annotations(type_node, source_code)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(type_node, source_code)
        is_abstract = 'abstract' in modifiers
        
        # Extract inheritance information
        extends, implements = self._extract_inheritance(type_node, source_code)
        
        # Extract methods and fields from class body
        methods, fields = self._extract_members(type_node, source_code, is_record)
        
        # Extract dependencies from source code
        dependencies = self._extract_dependencies(source_code, imports)
        
        full_name = f"{package_name}.{class_name}" if package_name else class_name
        
        return JavaClass(
            name=class_name,
            package=package_name,
            full_name=full_name,
            source_file=source_file,
            is_interface=is_interface,
            is_abstract=is_abstract,
            extends=extends,
            implements=implements,
            annotations=annotations,
            methods=methods,
            fields=fields,
            imports=imports,
            dependencies=dependencies
        )
    
    def _extract_annotations(self, node: Node, source_code: str) -> List[str]:
        """Extract annotations from a node."""
        annotations = []
        for child in node.children:
            if child.type == 'modifiers':
                for modifier_child in child.children:
                    if modifier_child.type == 'marker_annotation':
                        # Get annotation name (e.g., @Service)
                        for ann_child in modifier_child.children:
                            if ann_child.type == 'identifier' or ann_child.type == 'scoped_identifier':
                                ann_text = self._get_node_text(ann_child, source_code)
                                annotations.append(ann_text)
                    elif modifier_child.type == 'annotation':
                        # Normal annotation with parameters
                        for ann_child in modifier_child.children:
                            if ann_child.type == 'identifier' or ann_child.type == 'scoped_identifier':
                                ann_text = self._get_node_text(ann_child, source_code)
                                annotations.append(ann_text)
        return annotations
    
    def _extract_modifiers(self, node: Node, source_code: str) -> List[str]:
        """Extract modifiers (public, private, static, etc.) from a node."""
        modifiers = []
        for child in node.children:
            if child.type == 'modifiers':
                for modifier_child in child.children:
                    if modifier_child.type in ('public', 'private', 'protected', 'static', 
                                               'final', 'abstract', 'synchronized', 'native', 
                                               'strictfp', 'transient', 'volatile'):
                        modifiers.append(modifier_child.type)
        return modifiers
    
    def _extract_inheritance(self, node: Node, source_code: str) -> Tuple[Optional[str], List[str]]:
        """Extract extends and implements information."""
        extends = None
        implements = []
        
        for child in node.children:
            if child.type == 'superclass':
                # Get the extended class name
                for superclass_child in child.children:
                    if superclass_child.type in ('type_identifier', 'identifier', 'generic_type'):
                        extends = self._get_node_text(superclass_child, source_code)
            elif child.type == 'super_interfaces':
                # Get implemented interfaces
                for interface_child in child.children:
                    if interface_child.type == 'type_list':
                        for type_node in interface_child.children:
                            if type_node.type in ('type_identifier', 'generic_type'):
                                implements.append(self._get_node_text(type_node, source_code))
        
        return extends, implements
    
    def _extract_members(self, type_node: Node, source_code: str, 
                        is_record: bool = False) -> Tuple[List[JavaMethod], List[JavaField]]:
        """Extract methods and fields from class/interface body."""
        methods = []
        fields = []
        
        # Find the class/interface body
        body_node = None
        for child in type_node.children:
            if child.type in ('class_body', 'interface_body', 'enum_body'):
                body_node = child
                break
        
        if not body_node:
            return methods, fields
        
        # If it's a record, also extract record components as fields
        if is_record:
            for child in type_node.children:
                if child.type == 'formal_parameters':
                    record_fields = self._extract_record_components(child, source_code)
                    fields.extend(record_fields)
        
        # Extract members from body
        for member in body_node.children:
            if member.type == 'method_declaration' or member.type == 'constructor_declaration':
                method = self._extract_method_from_node(member, source_code)
                if method:
                    methods.append(method)
            elif member.type == 'field_declaration':
                field_list = self._extract_fields_from_node(member, source_code)
                fields.extend(field_list)
        
        return methods, fields
    
    def _extract_record_components(self, params_node: Node, source_code: str) -> List[JavaField]:
        """Extract fields from record components."""
        fields = []
        for child in params_node.children:
            if child.type == 'formal_parameter':
                field = self._extract_field_from_formal_parameter(child, source_code)
                if field:
                    fields.append(field)
        return fields
    
    def _extract_field_from_formal_parameter(self, param_node: Node, source_code: str) -> Optional[JavaField]:
        """Extract field information from a formal parameter (for records)."""
        field_type = ""
        field_name = ""
        annotations = []
        
        for child in param_node.children:
            if child.type in ('type_identifier', 'integral_type', 'floating_point_type', 
                            'boolean_type', 'generic_type', 'array_type'):
                field_type = self._get_node_text(child, source_code)
            elif child.type == 'identifier':
                field_name = self._get_node_text(child, source_code)
            elif child.type == 'modifiers':
                # Extract annotations from modifiers
                for modifier in child.children:
                    if modifier.type in ('marker_annotation', 'annotation'):
                        for ann_child in modifier.children:
                            if ann_child.type in ('identifier', 'scoped_identifier'):
                                annotations.append(self._get_node_text(ann_child, source_code))
        
        if not field_name:
            return None
        
        return JavaField(
            name=field_name,
            type=field_type,
            annotations=annotations,
            is_public=True,  # Record components are implicitly public
            is_private=False,
            is_protected=False,
            is_static=False,
            is_final=True,  # Record components are implicitly final
            line_number=param_node.start_point[0] + 1
        )
    
    def _extract_method_from_node(self, method_node: Node, source_code: str) -> Optional[JavaMethod]:
        """Extract method information from tree-sitter node."""
        method_name = ""
        return_type = "void"
        parameters = []
        annotations = []
        modifiers = []
        
        for child in method_node.children:
            if child.type == 'identifier':
                method_name = self._get_node_text(child, source_code)
            elif child.type in ('type_identifier', 'integral_type', 'floating_point_type', 
                              'boolean_type', 'void_type', 'generic_type', 'array_type'):
                return_type = self._get_node_text(child, source_code)
            elif child.type == 'formal_parameters':
                parameters = self._extract_parameters(child, source_code)
            elif child.type == 'modifiers':
                annotations = self._extract_annotations(method_node, source_code)
                modifiers = self._extract_modifiers(method_node, source_code)
        
        if not method_name and method_node.type == 'constructor_declaration':
            # Constructor name is the class name
            method_name = "<init>"
        
        if not method_name:
            return None
        
        return JavaMethod(
            name=method_name,
            return_type=return_type,
            parameters=parameters,
            annotations=annotations,
            is_public='public' in modifiers,
            is_private='private' in modifiers,
            is_protected='protected' in modifiers,
            is_static='static' in modifiers,
            is_abstract='abstract' in modifiers,
            line_number=method_node.start_point[0] + 1
        )
    
    def _extract_parameters(self, params_node: Node, source_code: str) -> List[Dict[str, str]]:
        """Extract method parameters."""
        parameters = []
        for child in params_node.children:
            if child.type == 'formal_parameter':
                param_type = ""
                param_name = ""
                for param_child in child.children:
                    if param_child.type in ('type_identifier', 'integral_type', 'floating_point_type',
                                           'boolean_type', 'generic_type', 'array_type'):
                        param_type = self._get_node_text(param_child, source_code)
                    elif param_child.type == 'identifier':
                        param_name = self._get_node_text(param_child, source_code)
                
                if param_name:
                    parameters.append({"name": param_name, "type": param_type})
        
        return parameters
    
    def _extract_fields_from_node(self, field_node: Node, source_code: str) -> List[JavaField]:
        """Extract field information from tree-sitter node."""
        fields = []
        field_type = ""
        annotations = []
        modifiers = []
        
        # Extract type, annotations, and modifiers
        for child in field_node.children:
            if child.type in ('type_identifier', 'integral_type', 'floating_point_type',
                            'boolean_type', 'generic_type', 'array_type'):
                field_type = self._get_node_text(child, source_code)
            elif child.type == 'modifiers':
                annotations = self._extract_annotations(field_node, source_code)
                modifiers = self._extract_modifiers(field_node, source_code)
            elif child.type == 'variable_declarator':
                # Extract field name from declarator
                for declarator_child in child.children:
                    if declarator_child.type == 'identifier':
                        field_name = self._get_node_text(declarator_child, source_code)
                        fields.append(JavaField(
                            name=field_name,
                            type=field_type,
                            annotations=annotations,
                            is_public='public' in modifiers,
                            is_private='private' in modifiers,
                            is_protected='protected' in modifiers,
                            is_static='static' in modifiers,
                            is_final='final' in modifiers,
                            line_number=child.start_point[0] + 1
                        ))
        
        return fields
    
    def _extract_dependencies(self, source_code: str, imports: List[str]) -> Set[str]:
        """Extract dependencies from source code and imports."""
        dependencies = set()
        
        # Add explicit imports
        for import_stmt in imports:
            dependencies.add(import_stmt)
        
        # Look for common Spring annotations and patterns
        spring_patterns = [
            r'@(Component|Service|Repository|Controller|RestController|Configuration)',
            r'@(Autowired|Inject|Resource)',
            r'@(Entity|Table|Column|Id|GeneratedValue)',
            r'@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping)',
            r'@(Transactional|Cacheable|Async)',
        ]
        
        for pattern in spring_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                dependencies.add(f"org.springframework.*.{match}")
        
        return dependencies
    
    def _organize_packages(self, classes: Dict[str, JavaClass]) -> Dict[str, JavaPackage]:
        """Organize classes into package structure."""
        packages = {}
        
        for class_name, java_class in classes.items():
            package_name = java_class.package
            
            if package_name not in packages:
                packages[package_name] = JavaPackage(
                    name=package_name,
                    classes=[],
                    sub_packages=[]
                )
            
            packages[package_name].classes.append(java_class)
        
        return packages
    
    def get_class_dependencies(self, class_name: str) -> Set[str]:
        """Get all dependencies for a specific class."""
        if class_name not in self.classes:
            return set()
        
        return self.classes[class_name].dependencies
    
    def get_package_dependencies(self, package_name: str) -> Set[str]:
        """Get all dependencies for a package."""
        dependencies = set()
        
        for class_name, java_class in self.classes.items():
            if java_class.package == package_name:
                dependencies.update(java_class.dependencies)
        
        return dependencies
    
    def find_spring_components(self) -> List[JavaClass]:
        """Find all Spring components (services, controllers, etc.)."""
        spring_components = []
        spring_annotations = {
            'Component', 'Service', 'Repository', 'Controller', 
            'RestController', 'Configuration', 'EnableAutoConfiguration'
        }
        
        for java_class in self.classes.values():
            class_annotations = set(java_class.annotations)
            if class_annotations.intersection(spring_annotations):
                spring_components.append(java_class)
        
        return spring_components
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate various code metrics."""
        total_classes = len(self.classes)
        total_methods = sum(len(cls.methods) for cls in self.classes.values())
        total_fields = sum(len(cls.fields) for cls in self.classes.values())
        
        # Calculate complexity metrics
        avg_methods_per_class = total_methods / total_classes if total_classes > 0 else 0
        avg_fields_per_class = total_fields / total_classes if total_classes > 0 else 0
        
        # Count Spring components
        spring_components = self.find_spring_components()
        
        return {
            "total_classes": total_classes,
            "total_methods": total_methods,
            "total_fields": total_fields,
            "total_packages": len(self.packages),
            "avg_methods_per_class": round(avg_methods_per_class, 2),
            "avg_fields_per_class": round(avg_fields_per_class, 2),
            "spring_components": len(spring_components),
            "interfaces": sum(1 for cls in self.classes.values() if cls.is_interface),
            "abstract_classes": sum(1 for cls in self.classes.values() if cls.is_abstract)
        }