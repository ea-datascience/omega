"""Structurizr integration for C4 model generation and architecture visualization."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
import json
from datetime import datetime

from .context_mapper import ContextMapperAnalyzer, BoundedContext, ContextMapperResult
from .java_parser import JavaSourceAnalyzer, JavaClass

logger = logging.getLogger(__name__)


@dataclass
class C4Person:
    """Represents a person in the C4 model."""
    name: str
    description: str
    location: str = "External"
    tags: List[str] = None


@dataclass
class C4SoftwareSystem:
    """Represents a software system in the C4 model."""
    name: str
    description: str
    location: str = "Internal"
    tags: List[str] = None


@dataclass
class C4Container:
    """Represents a container in the C4 model."""
    name: str
    description: str
    technology: str
    tags: List[str] = None


@dataclass
class C4Component:
    """Represents a component in the C4 model."""
    name: str
    description: str
    technology: str
    category: str = ""
    tags: List[str] = None


@dataclass
class C4Relationship:
    """Represents a relationship in the C4 model."""
    source: str
    destination: str
    description: str
    technology: str = ""
    interaction_style: str = "Synchronous"
    tags: List[str] = None


@dataclass
class C4Model:
    """Complete C4 model representation."""
    name: str
    description: str
    people: List[C4Person]
    software_systems: List[C4SoftwareSystem]
    containers: List[C4Container]
    components: List[C4Component]
    relationships: List[C4Relationship]
    views: Dict[str, Any]


@dataclass
class StructurizrWorkspace:
    """Structurizr workspace containing the C4 model and views."""
    id: int
    name: str
    description: str
    model: C4Model
    views: Dict[str, Any]
    documentation: List[Dict[str, str]]
    decisions: List[Dict[str, Any]]


class StructurizrGenerator:
    """Generates C4 models and Structurizr workspaces from Java application analysis."""
    
    def __init__(self):
        self.context_mapper = ContextMapperAnalyzer()
        self.java_analyzer = JavaSourceAnalyzer()
    
    def generate_c4_model(self, source_path: Path, system_name: str = "Legacy Monolith") -> C4Model:
        """Generate a C4 model from Java source code analysis."""
        logger.info(f"Generating C4 model for: {source_path}")
        
        # First analyze with Context Mapper to get bounded contexts
        context_result = self.context_mapper.analyze_project(source_path)
        
        # Analyze Java source for additional details
        java_analysis = self.java_analyzer.analyze_directory(source_path)
        
        # Generate C4 model components
        people = self._generate_people()
        software_systems = self._generate_software_systems(system_name)
        containers = self._generate_containers(context_result.domain_model.bounded_contexts)
        components = self._generate_components(context_result.domain_model.bounded_contexts, java_analysis["classes"])
        relationships = self._generate_relationships(context_result.domain_model, java_analysis["classes"])
        views = self._generate_views(containers, components)
        
        c4_model = C4Model(
            name=system_name,
            description=f"C4 model for {system_name} system",
            people=people,
            software_systems=software_systems,
            containers=containers,
            components=components,
            relationships=relationships,
            views=views
        )
        
        logger.info(f"C4 model generated: {len(containers)} containers, {len(components)} components")
        return c4_model
    
    def _generate_people(self) -> List[C4Person]:
        """Generate typical personas for enterprise applications."""
        return [
            C4Person(
                name="Business User",
                description="End users who interact with the system through web interface",
                location="External",
                tags=["Person", "External"]
            ),
            C4Person(
                name="System Administrator",
                description="Administrators who manage and monitor the system",
                location="Internal",
                tags=["Person", "Internal", "Admin"]
            ),
            C4Person(
                name="API Consumer",
                description="External systems or applications that consume APIs",
                location="External",
                tags=["Person", "External", "API"]
            )
        ]
    
    def _generate_software_systems(self, system_name: str) -> List[C4SoftwareSystem]:
        """Generate software systems for the C4 model."""
        return [
            C4SoftwareSystem(
                name=system_name,
                description="The main monolithic application being analyzed for migration",
                location="Internal",
                tags=["Software System", "Internal", "Monolith"]
            ),
            C4SoftwareSystem(
                name="Database System",
                description="Relational database storing application data",
                location="Internal", 
                tags=["Software System", "Database", "Internal"]
            ),
            C4SoftwareSystem(
                name="External APIs",
                description="Third-party APIs and services",
                location="External",
                tags=["Software System", "External", "API"]
            )
        ]
    
    def _generate_containers(self, bounded_contexts: List[BoundedContext]) -> List[C4Container]:
        """Generate containers from bounded contexts."""
        containers = []
        
        # Main application container
        containers.append(C4Container(
            name="Web Application",
            description="Main Spring Boot application serving web requests",
            technology="Spring Boot, Java",
            tags=["Container", "Web Application", "Spring Boot"]
        ))
        
        # Generate a container for each significant bounded context
        for context in bounded_contexts:
            if len(context.classes) > 5:  # Only create containers for substantial contexts
                container = C4Container(
                    name=f"{context.name} Module",
                    description=f"Module handling {context.name.lower()} domain logic",
                    technology="Spring Boot Module, Java",
                    tags=["Container", "Module", "Spring Boot"]
                )
                containers.append(container)
        
        # Database container
        containers.append(C4Container(
            name="Database",
            description="Relational database storing all application data",
            technology="PostgreSQL/MySQL",
            tags=["Container", "Database"]
        ))
        
        return containers
    
    def _generate_components(self, bounded_contexts: List[BoundedContext], 
                           classes: Dict[str, JavaClass]) -> List[C4Component]:
        """Generate components from bounded contexts and Java classes."""
        components = []
        
        for context in bounded_contexts:
            # Controllers
            for controller_class in context.controllers:
                if controller_class in classes:
                    java_class = classes[controller_class]
                    component = C4Component(
                        name=java_class.name,
                        description=f"REST controller for {context.name.lower()} operations",
                        technology="Spring MVC Controller",
                        category="Controller",
                        tags=["Component", "Controller", "REST"]
                    )
                    components.append(component)
            
            # Services
            for service_class in context.services:
                if service_class in classes:
                    java_class = classes[service_class]
                    component = C4Component(
                        name=java_class.name,
                        description=f"Business logic service for {context.name.lower()}",
                        technology="Spring Service",
                        category="Service",
                        tags=["Component", "Service", "Business Logic"]
                    )
                    components.append(component)
            
            # Repositories
            for repo_class in context.repositories:
                if repo_class in classes:
                    java_class = classes[repo_class]
                    component = C4Component(
                        name=java_class.name,
                        description=f"Data access repository for {context.name.lower()}",
                        technology="Spring Data JPA",
                        category="Repository",
                        tags=["Component", "Repository", "Data Access"]
                    )
                    components.append(component)
            
            # Domain Models/Aggregates
            for aggregate_class in context.aggregates:
                if aggregate_class in classes:
                    java_class = classes[aggregate_class]
                    component = C4Component(
                        name=java_class.name,
                        description=f"Domain entity for {context.name.lower()}",
                        technology="JPA Entity",
                        category="Domain Model",
                        tags=["Component", "Domain Model", "Entity"]
                    )
                    components.append(component)
        
        return components
    
    def _generate_relationships(self, domain_model, classes: Dict[str, JavaClass]) -> List[C4Relationship]:
        """Generate relationships between components."""
        relationships = []
        
        # Add relationships from context map
        for rel in domain_model.context_relationships:
            relationship = C4Relationship(
                source=rel["from"],
                destination=rel["to"],
                description=f"Depends on {rel['to']} for domain operations",
                technology="Java Method Calls",
                interaction_style="Synchronous",
                tags=["Relationship", "Domain"]
            )
            relationships.append(relationship)
        
        # Add typical web application relationships
        relationships.extend([
            C4Relationship(
                source="Business User",
                destination="Web Application",
                description="Uses web interface to interact with the system",
                technology="HTTPS",
                interaction_style="Synchronous",
                tags=["Relationship", "User Interface"]
            ),
            C4Relationship(
                source="Web Application",
                destination="Database",
                description="Stores and retrieves application data",
                technology="JDBC",
                interaction_style="Synchronous",
                tags=["Relationship", "Data Access"]
            ),
            C4Relationship(
                source="API Consumer",
                destination="Web Application",
                description="Consumes REST APIs for integration",
                technology="REST/HTTP",
                interaction_style="Synchronous",
                tags=["Relationship", "API"]
            )
        ])
        
        return relationships
    
    def _generate_views(self, containers: List[C4Container], components: List[C4Component]) -> Dict[str, Any]:
        """Generate C4 views configuration."""
        views = {
            "systemLandscape": {
                "title": "System Landscape",
                "description": "High-level view of the system and its environment",
                "include": "people,softwareSystems",
                "exclude": "tags:Internal"
            },
            "systemContext": {
                "title": "System Context",
                "description": "System context showing external dependencies",
                "include": "people,softwareSystems,relationships",
                "focus": "Legacy Monolith"
            },
            "containerView": {
                "title": "Container View",
                "description": "Container-level view of the system architecture",
                "include": "containers,relationships",
                "focus": "Legacy Monolith"
            },
            "componentViews": []
        }
        
        # Generate component views for each container
        container_names = set()
        for container in containers:
            if container.name not in container_names and "Module" in container.name:
                component_view = {
                    "title": f"{container.name} Components",
                    "description": f"Component view of {container.name}",
                    "container": container.name,
                    "include": "components,relationships"
                }
                views["componentViews"].append(component_view)
                container_names.add(container.name)
        
        return views
    
    def create_structurizr_workspace(self, c4_model: C4Model, workspace_id: int = 1) -> StructurizrWorkspace:
        """Create a Structurizr workspace from a C4 model."""
        
        # Generate views configuration
        views = {
            "systemLandscape": {
                "key": "SystemLandscape",
                "title": "System Landscape",
                "description": c4_model.views.get("systemLandscape", {}).get("description", ""),
                "elements": "people,softwareSystems"
            },
            "systemContext": {
                "key": "SystemContext", 
                "title": "System Context",
                "description": c4_model.views.get("systemContext", {}).get("description", ""),
                "softwareSystemId": c4_model.name
            },
            "containers": {
                "key": "Containers",
                "title": "Container View", 
                "description": c4_model.views.get("containerView", {}).get("description", ""),
                "softwareSystemId": c4_model.name
            },
            "components": [
                {
                    "key": f"Components-{view['container'].replace(' ', '')}",
                    "title": view["title"],
                    "description": view["description"],
                    "containerId": view["container"]
                }
                for view in c4_model.views.get("componentViews", [])
            ]
        }
        
        # Generate documentation
        documentation = [
            {
                "title": "Architecture Overview",
                "content": f"This document describes the architecture of {c4_model.name}. "
                          f"The system contains {len(c4_model.containers)} containers and "
                          f"{len(c4_model.components)} components."
            },
            {
                "title": "Container Overview",
                "content": "The system is decomposed into the following containers:\n\n" +
                          "\n".join([f"- **{c.name}**: {c.description}" for c in c4_model.containers])
            },
            {
                "title": "Component Overview", 
                "content": "Key components in the system:\n\n" +
                          "\n".join([f"- **{c.name}** ({c.category}): {c.description}" 
                                   for c in c4_model.components[:10]])  # Limit to first 10
            }
        ]
        
        # Generate architectural decisions
        decisions = [
            {
                "id": "001",
                "date": datetime.now().isoformat(),
                "title": "Monolithic Architecture",
                "status": "Superseded",
                "content": "The system was initially built as a monolith for rapid development. "
                          "This decision is being reconsidered for microservices migration."
            },
            {
                "id": "002", 
                "date": datetime.now().isoformat(),
                "title": "Spring Boot Framework",
                "status": "Accepted",
                "content": "Spring Boot was chosen as the primary framework for its convention-over-configuration "
                          "approach and extensive ecosystem support."
            }
        ]
        
        workspace = StructurizrWorkspace(
            id=workspace_id,
            name=f"{c4_model.name} Architecture",
            description=f"Architecture documentation for {c4_model.name}",
            model=c4_model,
            views=views,
            documentation=documentation,
            decisions=decisions
        )
        
        return workspace
    
    def export_to_structurizr_json(self, workspace: StructurizrWorkspace, output_path: Path) -> None:
        """Export workspace to Structurizr JSON format."""
        
        # Convert to Structurizr JSON format
        structurizr_json = {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "lastModifiedDate": datetime.now().isoformat(),
            "model": {
                "people": [
                    {
                        "id": str(hash(p.name)),
                        "name": p.name,
                        "description": p.description,
                        "location": p.location,
                        "tags": ",".join(p.tags or [])
                    }
                    for p in workspace.model.people
                ],
                "softwareSystems": [
                    {
                        "id": str(hash(s.name)),
                        "name": s.name,
                        "description": s.description,
                        "location": s.location,
                        "tags": ",".join(s.tags or [])
                    }
                    for s in workspace.model.software_systems
                ],
                "relationships": [
                    {
                        "sourceId": str(hash(r.source)),
                        "destinationId": str(hash(r.destination)),
                        "description": r.description,
                        "technology": r.technology,
                        "interactionStyle": r.interaction_style,
                        "tags": ",".join(r.tags or [])
                    }
                    for r in workspace.model.relationships
                ]
            },
            "views": workspace.views,
            "documentation": {
                "sections": [
                    {
                        "title": doc["title"],
                        "content": doc["content"],
                        "format": "Markdown"
                    }
                    for doc in workspace.documentation
                ]
            },
            "decisions": [
                {
                    "id": decision["id"],
                    "date": decision["date"],
                    "title": decision["title"],
                    "status": decision["status"],
                    "content": decision["content"],
                    "format": "Markdown"
                }
                for decision in workspace.decisions
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structurizr_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Structurizr workspace exported to: {output_path}")
    
    def export_to_plantuml(self, c4_model: C4Model, output_path: Path) -> None:
        """Export C4 model to PlantUML format."""
        
        plantuml_lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
            "",
            f"LAYOUT_WITH_LEGEND()",
            f"title Container Diagram for {c4_model.name}",
            ""
        ]
        
        # Add people
        for person in c4_model.people:
            plantuml_lines.append(f"Person({person.name.replace(' ', '_')}, \"{person.name}\", \"{person.description}\")")
        
        plantuml_lines.append("")
        
        # Add systems
        for system in c4_model.software_systems:
            if system.location == "Internal":
                plantuml_lines.append(f"System({system.name.replace(' ', '_')}, \"{system.name}\", \"{system.description}\")")
            else:
                plantuml_lines.append(f"System_Ext({system.name.replace(' ', '_')}, \"{system.name}\", \"{system.description}\")")
        
        plantuml_lines.append("")
        
        # Add containers
        for container in c4_model.containers:
            plantuml_lines.append(f"Container({container.name.replace(' ', '_')}, \"{container.name}\", \"{container.technology}\", \"{container.description}\")")
        
        plantuml_lines.append("")
        
        # Add relationships
        for rel in c4_model.relationships:
            source_id = rel.source.replace(' ', '_')
            dest_id = rel.destination.replace(' ', '_')
            plantuml_lines.append(f"Rel({source_id}, {dest_id}, \"{rel.description}\", \"{rel.technology}\")")
        
        plantuml_lines.append("")
        plantuml_lines.append("@enduml")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(plantuml_lines))
        
        logger.info(f"PlantUML diagram exported to: {output_path}")
    
    def generate_c4_component_diagram(self, bounded_context: BoundedContext, 
                                    classes: Dict[str, JavaClass], output_path: Path) -> None:
        """Generate a detailed C4 component diagram for a specific bounded context."""
        
        plantuml_lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
            "",
            f"title Component Diagram for {bounded_context.name}",
            f"Container_Boundary(c1, \"{bounded_context.name} Container\") {{",
            ""
        ]
        
        # Add components for this context
        for class_name in bounded_context.classes:
            if class_name in classes:
                java_class = classes[class_name]
                component_type = self._get_component_type(java_class.annotations)
                
                component_line = f"    Component({java_class.name}, \"{java_class.name}\", \"{component_type}\", \"\")"
                plantuml_lines.append(component_line)
        
        plantuml_lines.append("}")
        plantuml_lines.append("")
        
        # Add external dependencies
        plantuml_lines.append("ContainerDb(db, \"Database\", \"Relational Database\", \"Stores data\")")
        plantuml_lines.append("")
        
        # Add relationships within the context
        for class_name in bounded_context.classes:
            if class_name in classes:
                java_class = classes[class_name]
                # Simple relationship inference based on Spring patterns
                if "Controller" in java_class.annotations:
                    for service in bounded_context.services:
                        service_name = service.split('.')[-1]
                        plantuml_lines.append(f"Rel({java_class.name}, {service_name}, \"uses\")")
                elif "Service" in java_class.annotations:
                    for repo in bounded_context.repositories:
                        repo_name = repo.split('.')[-1]
                        plantuml_lines.append(f"Rel({java_class.name}, {repo_name}, \"uses\")")
                elif "Repository" in java_class.annotations:
                    plantuml_lines.append(f"Rel({java_class.name}, db, \"reads/writes\")")
        
        plantuml_lines.append("")
        plantuml_lines.append("@enduml")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(plantuml_lines))
        
        logger.info(f"Component diagram for {bounded_context.name} exported to: {output_path}")
    
    def _get_component_type(self, annotations: List[str]) -> str:
        """Determine component type from annotations."""
        if any(ann in annotations for ann in ['Controller', 'RestController']):
            return "Spring MVC Controller"
        elif 'Service' in annotations:
            return "Spring Service"
        elif 'Repository' in annotations:
            return "Spring Data Repository"
        elif 'Entity' in annotations:
            return "JPA Entity"
        else:
            return "Spring Component"
    
    def analyze_and_export_all(self, source_path: Path, output_dir: Path) -> Dict[str, Path]:
        """Comprehensive analysis and export of all C4 artifacts."""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}
        
        # Generate C4 model
        c4_model = self.generate_c4_model(source_path)
        
        # Create Structurizr workspace
        workspace = self.create_structurizr_workspace(c4_model)
        
        # Export Structurizr JSON
        structurizr_path = output_dir / "structurizr-workspace.json"
        self.export_to_structurizr_json(workspace, structurizr_path)
        exported_files["structurizr_json"] = structurizr_path
        
        # Export PlantUML
        plantuml_path = output_dir / "container-diagram.puml"
        self.export_to_plantuml(c4_model, plantuml_path)
        exported_files["plantuml"] = plantuml_path
        
        # Export JSON summary
        summary_path = output_dir / "c4-model-summary.json"
        self._export_model_summary(c4_model, summary_path)
        exported_files["summary"] = summary_path
        
        logger.info(f"All C4 artifacts exported to: {output_dir}")
        return exported_files
    
    def _export_model_summary(self, c4_model: C4Model, output_path: Path) -> None:
        """Export a JSON summary of the C4 model."""
        
        summary = {
            "name": c4_model.name,
            "description": c4_model.description,
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "people": len(c4_model.people),
                "software_systems": len(c4_model.software_systems),
                "containers": len(c4_model.containers),
                "components": len(c4_model.components),
                "relationships": len(c4_model.relationships)
            },
            "containers": [
                {
                    "name": container.name,
                    "description": container.description,
                    "technology": container.technology
                }
                for container in c4_model.containers
            ],
            "component_categories": {}
        }
        
        # Categorize components
        for component in c4_model.components:
            category = component.category or "Other"
            if category not in summary["component_categories"]:
                summary["component_categories"][category] = 0
            summary["component_categories"][category] += 1
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"C4 model summary exported to: {output_path}")