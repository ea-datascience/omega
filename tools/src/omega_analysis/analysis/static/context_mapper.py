"""Context Mapper integration for domain modeling and bounded context detection."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
import json
import re
import tempfile
import subprocess

from .java_parser import JavaSourceAnalyzer, JavaClass

logger = logging.getLogger(__name__)


@dataclass
class BoundedContext:
    """Represents a bounded context in the domain model."""
    name: str
    description: str
    classes: List[str]
    services: List[str]
    repositories: List[str]
    controllers: List[str]
    aggregates: List[str]
    domain_events: List[str]
    dependencies: Set[str]
    package_prefix: str


@dataclass
class DomainModel:
    """Represents the overall domain model."""
    bounded_contexts: List[BoundedContext]
    context_relationships: List[Dict[str, Any]]
    aggregates: List[Dict[str, Any]]
    domain_services: List[str]
    shared_kernel: List[str]


@dataclass
class ContextMapperResult:
    """Result of Context Mapper analysis."""
    domain_model: DomainModel
    context_map_dsl: str
    c4_model: Optional[str]
    plant_uml: Optional[str]
    metrics: Dict[str, Any]


class ContextMapperAnalyzer:
    """Analyzes Java applications to detect bounded contexts using Domain-Driven Design principles."""
    
    def __init__(self):
        self.java_analyzer = JavaSourceAnalyzer()
        self.spring_stereotypes = {
            'Service': 'domain_service',
            'Repository': 'repository', 
            'Controller': 'api_layer',
            'RestController': 'api_layer',
            'Component': 'infrastructure',
            'Configuration': 'infrastructure'
        }
        self.domain_indicators = [
            'Entity', 'ValueObject', 'DomainService', 'Repository',
            'Aggregate', 'AggregateRoot', 'DomainEvent'
        ]
    
    def analyze_project(self, source_path: Path) -> ContextMapperResult:
        """Analyze a Java project to extract bounded contexts and domain model."""
        logger.info(f"Starting Context Mapper analysis for: {source_path}")
        
        # First analyze the Java source code
        java_analysis = self.java_analyzer.analyze_directory(source_path)
        
        # Detect bounded contexts
        bounded_contexts = self._detect_bounded_contexts(java_analysis["classes"])
        
        # Build domain model
        domain_model = self._build_domain_model(bounded_contexts, java_analysis["classes"])
        
        # Generate Context Map DSL
        context_map_dsl = self._generate_context_map_dsl(domain_model)
        
        # Calculate metrics
        metrics = self._calculate_context_metrics(domain_model, java_analysis["classes"])
        
        result = ContextMapperResult(
            domain_model=domain_model,
            context_map_dsl=context_map_dsl,
            c4_model=None,  # Could be generated with Structurizr integration
            plant_uml=None,  # Could be generated separately
            metrics=metrics
        )
        
        logger.info(f"Context Mapper analysis complete: {len(bounded_contexts)} bounded contexts detected")
        return result
    
    def _detect_bounded_contexts(self, classes: Dict[str, JavaClass]) -> List[BoundedContext]:
        """Detect bounded contexts based on package structure and domain patterns."""
        logger.info("Detecting bounded contexts...")
        
        # Group classes by package prefixes (potential contexts)
        package_groups = {}
        
        for class_name, java_class in classes.items():
            package_parts = java_class.package.split('.')
            
            # Look for common context indicators in package names
            context_package = self._identify_context_package(package_parts)
            
            if context_package not in package_groups:
                package_groups[context_package] = {
                    'classes': [],
                    'services': [],
                    'repositories': [],
                    'controllers': [],
                    'aggregates': [],
                    'domain_events': []
                }
            
            # Classify the class based on annotations and naming patterns
            classification = self._classify_class(java_class)
            package_groups[context_package]['classes'].append(class_name)
            
            if classification == 'service':
                package_groups[context_package]['services'].append(class_name)
            elif classification == 'repository':
                package_groups[context_package]['repositories'].append(class_name)
            elif classification == 'controller':
                package_groups[context_package]['controllers'].append(class_name)
            elif classification == 'aggregate':
                package_groups[context_package]['aggregates'].append(class_name)
            elif classification == 'domain_event':
                package_groups[context_package]['domain_events'].append(class_name)
        
        # Create bounded contexts from package groups
        bounded_contexts = []
        for package_name, group_data in package_groups.items():
            if len(group_data['classes']) > 1:  # Only consider contexts with multiple classes
                
                context = BoundedContext(
                    name=self._generate_context_name(package_name),
                    description=f"Bounded context derived from package: {package_name}",
                    classes=group_data['classes'],
                    services=group_data['services'],
                    repositories=group_data['repositories'],
                    controllers=group_data['controllers'],
                    aggregates=group_data['aggregates'],
                    domain_events=group_data['domain_events'],
                    dependencies=self._calculate_context_dependencies(group_data['classes'], classes),
                    package_prefix=package_name
                )
                bounded_contexts.append(context)
        
        return bounded_contexts
    
    def _identify_context_package(self, package_parts: List[str]) -> str:
        """Identify the package that represents a bounded context."""
        # Common patterns for bounded contexts
        context_indicators = [
            'domain', 'service', 'module', 'component', 'feature',
            'user', 'order', 'payment', 'inventory', 'catalog',
            'account', 'customer', 'product', 'billing'
        ]
        
        # Look for context indicators in package parts
        for i, part in enumerate(package_parts):
            if any(indicator in part.lower() for indicator in context_indicators):
                # Return package up to this level
                return '.'.join(package_parts[:i+1])
        
        # Default: use the first 3-4 package levels
        max_levels = min(4, len(package_parts))
        return '.'.join(package_parts[:max_levels])
    
    def _classify_class(self, java_class: JavaClass) -> str:
        """Classify a Java class based on annotations and naming patterns."""
        annotations = set(java_class.annotations)
        class_name = java_class.name.lower()
        implements = [impl.split('<')[0].strip() for impl in java_class.implements]  # Remove generics
        
        # Check for domain events - implements DomainEvent interface or has event annotations
        if 'DomainEvent' in implements or any('event' in impl.lower() for impl in implements):
            return 'domain_event'
        if any(ann in annotations for ann in ['DomainEvent', 'Externalized']):
            return 'domain_event'
        if class_name.endswith('event') or class_name.endswith('ed') or class_name.endswith('completed'):
            return 'domain_event'
        
        # Check for aggregates - implements AggregateRoot or has Entity annotation
        if any('aggregateroot' in impl.lower() for impl in implements):
            return 'aggregate'
        if 'AggregateRoot' in annotations or 'Entity' in annotations:
            return 'aggregate'
        
        # Check Spring stereotypes
        if 'Service' in annotations or 'DomainService' in annotations:
            return 'service'
        elif 'Repository' in annotations:
            return 'repository'
        elif any(ann in annotations for ann in ['Controller', 'RestController']):
            return 'controller'
        
        # Check naming patterns
        if class_name.endswith('service') and 'management' in class_name:
            return 'service'
        elif class_name.endswith('repository'):
            return 'repository'
        elif class_name.endswith('controller'):
            return 'controller'
        elif any(pattern in class_name for pattern in ['entity', 'aggregate', 'root']):
            return 'aggregate'
        
        return 'other'
    
    def _generate_context_name(self, package_name: str) -> str:
        """Generate a human-readable context name from package."""
        parts = package_name.split('.')
        # Take the last meaningful part and capitalize it
        last_part = parts[-1] if parts else package_name
        return last_part.replace('_', ' ').title().replace(' ', '')
    
    def _calculate_context_dependencies(self, context_classes: List[str], 
                                      all_classes: Dict[str, JavaClass]) -> Set[str]:
        """Calculate dependencies between contexts."""
        dependencies = set()
        
        for class_name in context_classes:
            if class_name in all_classes:
                java_class = all_classes[class_name]
                
                # Add package-level dependencies
                for dep in java_class.dependencies:
                    # Extract package from dependency
                    if '.' in dep:
                        dep_package = '.'.join(dep.split('.')[:-1])
                        dependencies.add(dep_package)
        
        return dependencies
    
    def _build_domain_model(self, bounded_contexts: List[BoundedContext], 
                           all_classes: Dict[str, JavaClass]) -> DomainModel:
        """Build the overall domain model from bounded contexts."""
        
        # Detect relationships between contexts
        context_relationships = self._detect_context_relationships(bounded_contexts)
        
        # Identify shared kernel (common dependencies)
        shared_kernel = self._identify_shared_kernel(bounded_contexts)
        
        # Extract aggregates with more detail
        aggregates = self._extract_aggregates(bounded_contexts, all_classes)
        
        # Identify domain services
        domain_services = []
        for context in bounded_contexts:
            domain_services.extend(context.services)
        
        return DomainModel(
            bounded_contexts=bounded_contexts,
            context_relationships=context_relationships,
            aggregates=aggregates,
            domain_services=domain_services,
            shared_kernel=shared_kernel
        )
    
    def _detect_context_relationships(self, contexts: List[BoundedContext]) -> List[Dict[str, Any]]:
        """Detect relationships between bounded contexts."""
        relationships = []
        
        for i, context_a in enumerate(contexts):
            for j, context_b in enumerate(contexts):
                if i != j:
                    # Check if context A depends on context B
                    if any(dep.startswith(context_b.package_prefix) for dep in context_a.dependencies):
                        relationship = {
                            "from": context_a.name,
                            "to": context_b.name,
                            "type": "depends_on",
                            "strength": self._calculate_dependency_strength(context_a, context_b)
                        }
                        relationships.append(relationship)
        
        return relationships
    
    def _calculate_dependency_strength(self, context_a: BoundedContext, 
                                     context_b: BoundedContext) -> str:
        """Calculate the strength of dependency between contexts."""
        dependency_count = sum(1 for dep in context_a.dependencies 
                             if dep.startswith(context_b.package_prefix))
        
        if dependency_count > 10:
            return "strong"
        elif dependency_count > 3:
            return "medium"
        else:
            return "weak"
    
    def _identify_shared_kernel(self, contexts: List[BoundedContext]) -> List[str]:
        """Identify shared kernel components used by multiple contexts."""
        dependency_counts = {}
        
        for context in contexts:
            for dep in context.dependencies:
                if dep not in dependency_counts:
                    dependency_counts[dep] = 0
                dependency_counts[dep] += 1
        
        # Shared kernel = dependencies used by multiple contexts
        shared_kernel = [dep for dep, count in dependency_counts.items() if count > 1]
        return shared_kernel
    
    def _extract_aggregates(self, contexts: List[BoundedContext], 
                           all_classes: Dict[str, JavaClass]) -> List[Dict[str, Any]]:
        """Extract detailed aggregate information."""
        aggregates = []
        
        for context in contexts:
            for aggregate_class in context.aggregates:
                if aggregate_class in all_classes:
                    java_class = all_classes[aggregate_class]
                    
                    aggregate_info = {
                        "name": java_class.name,
                        "context": context.name,
                        "root_entity": aggregate_class,
                        "entities": self._find_related_entities(java_class, all_classes),
                        "value_objects": self._find_value_objects(java_class, all_classes),
                        "domain_events": [cls for cls in context.domain_events 
                                        if self._is_related_to_aggregate(cls, java_class, all_classes)]
                    }
                    aggregates.append(aggregate_info)
        
        return aggregates
    
    def _find_related_entities(self, aggregate_root: JavaClass, 
                              all_classes: Dict[str, JavaClass]) -> List[str]:
        """Find entities related to an aggregate root."""
        related_entities = []
        
        # Look for classes in the same package with Entity annotation
        for class_name, java_class in all_classes.items():
            if (java_class.package == aggregate_root.package and 
                'Entity' in java_class.annotations and 
                class_name != aggregate_root.full_name):
                related_entities.append(class_name)
        
        return related_entities
    
    def _find_value_objects(self, aggregate_root: JavaClass, 
                           all_classes: Dict[str, JavaClass]) -> List[str]:
        """Find value objects related to an aggregate root."""
        value_objects = []
        
        # Look for classes without Entity annotation in same package
        for class_name, java_class in all_classes.items():
            if (java_class.package == aggregate_root.package and 
                'Entity' not in java_class.annotations and
                not java_class.name.endswith('Service') and
                not java_class.name.endswith('Repository') and
                not java_class.name.endswith('Controller')):
                value_objects.append(class_name)
        
        return value_objects
    
    def _is_related_to_aggregate(self, event_class: str, aggregate_root: JavaClass, 
                                all_classes: Dict[str, JavaClass]) -> bool:
        """Check if a domain event is related to an aggregate."""
        if event_class in all_classes:
            event = all_classes[event_class]
            # Simple heuristic: same package or event name contains aggregate name
            return (event.package == aggregate_root.package or 
                    aggregate_root.name.lower() in event.name.lower())
        return False
    
    def _generate_context_map_dsl(self, domain_model: DomainModel) -> str:
        """Generate Context Mapper DSL representation."""
        dsl_lines = []
        
        # Header
        dsl_lines.append("ContextMap OmegaSystemContextMap {")
        dsl_lines.append("  type = SYSTEM_LANDSCAPE")
        dsl_lines.append("  state = TO_BE")
        dsl_lines.append("")
        
        # Define bounded contexts
        dsl_lines.append("  /* Bounded Contexts */")
        for context in domain_model.bounded_contexts:
            dsl_lines.append(f"  contains {context.name}")
        dsl_lines.append("")
        
        # Define relationships
        if domain_model.context_relationships:
            dsl_lines.append("  /* Context Relationships */")
            for rel in domain_model.context_relationships:
                if rel["type"] == "depends_on":
                    dsl_lines.append(f"  {rel['from']} -> {rel['to']}")
        dsl_lines.append("")
        
        dsl_lines.append("}")
        dsl_lines.append("")
        
        # Define each bounded context in detail
        for context in domain_model.bounded_contexts:
            dsl_lines.append(f"BoundedContext {context.name} {{")
            dsl_lines.append(f"  type = FEATURE")
            dsl_lines.append(f"  domainVisionStatement = \"{context.description}\"")
            dsl_lines.append("")
            
            # Aggregates
            if context.aggregates:
                dsl_lines.append("  Aggregate AggregateRoot {")
                for aggregate in context.aggregates:
                    class_name = aggregate.split('.')[-1]
                    dsl_lines.append(f"    Entity {class_name}")
                dsl_lines.append("  }")
                dsl_lines.append("")
            
            dsl_lines.append("}")
            dsl_lines.append("")
        
        return '\n'.join(dsl_lines)
    
    def _calculate_context_metrics(self, domain_model: DomainModel, 
                                  all_classes: Dict[str, JavaClass]) -> Dict[str, Any]:
        """Calculate metrics for the context map."""
        
        total_contexts = len(domain_model.bounded_contexts)
        total_relationships = len(domain_model.context_relationships)
        total_aggregates = len(domain_model.aggregates)
        
        # Calculate context sizes
        context_sizes = [len(ctx.classes) for ctx in domain_model.bounded_contexts]
        avg_context_size = sum(context_sizes) / len(context_sizes) if context_sizes else 0
        
        # Calculate coupling metrics
        incoming_dependencies = {}
        outgoing_dependencies = {}
        
        for rel in domain_model.context_relationships:
            from_ctx = rel["from"]
            to_ctx = rel["to"]
            
            if to_ctx not in incoming_dependencies:
                incoming_dependencies[to_ctx] = 0
            incoming_dependencies[to_ctx] += 1
            
            if from_ctx not in outgoing_dependencies:
                outgoing_dependencies[from_ctx] = 0
            outgoing_dependencies[from_ctx] += 1
        
        return {
            "total_bounded_contexts": total_contexts,
            "total_relationships": total_relationships,
            "total_aggregates": total_aggregates,
            "average_context_size": round(avg_context_size, 2),
            "max_context_size": max(context_sizes) if context_sizes else 0,
            "min_context_size": min(context_sizes) if context_sizes else 0,
            "shared_kernel_size": len(domain_model.shared_kernel),
            "coupling_metrics": {
                "max_incoming_dependencies": max(incoming_dependencies.values()) if incoming_dependencies else 0,
                "max_outgoing_dependencies": max(outgoing_dependencies.values()) if outgoing_dependencies else 0,
                "total_dependencies": total_relationships
            }
        }
    
    def export_to_json(self, result: ContextMapperResult, output_path: Path) -> None:
        """Export Context Mapper result to JSON format."""
        
        # Convert dataclasses to dictionaries for JSON serialization
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {field: dataclass_to_dict(getattr(obj, field)) 
                       for field in obj.__dataclass_fields__}
            elif isinstance(obj, list):
                return [dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {key: dataclass_to_dict(value) for key, value in obj.items()}
            else:
                return obj
        
        export_data = {
            "domain_model": dataclass_to_dict(result.domain_model),
            "context_map_dsl": result.context_map_dsl,
            "metrics": result.metrics,
            "generated_at": "2025-11-18T13:45:00Z"  # Could use datetime.now()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Context Mapper results exported to: {output_path}")
    
    def generate_c4_model_hints(self, result: ContextMapperResult) -> Dict[str, Any]:
        """Generate hints for C4 model generation (to be used with Structurizr)."""
        
        c4_hints = {
            "system": {
                "name": "Legacy Monolith System",
                "description": "System being analyzed for microservices migration"
            },
            "containers": [],
            "components": []
        }
        
        # Each bounded context could become a container or set of components
        for context in result.domain_model.bounded_contexts:
            container_hint = {
                "name": context.name,
                "description": context.description,
                "technology": "Spring Boot",
                "components": []
            }
            
            # Each service could become a component
            for service in context.services:
                component_hint = {
                    "name": service.split('.')[-1],
                    "description": f"Service component in {context.name}",
                    "technology": "Spring Service"
                }
                container_hint["components"].append(component_hint)
            
            c4_hints["containers"].append(container_hint)
        
        return c4_hints