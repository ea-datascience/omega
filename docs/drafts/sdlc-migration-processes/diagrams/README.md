# Migration Epics Dependencies Diagrams

This directory contains UML diagrams supporting the Migration Epics Framework documentation.

## Diagrams

### migration-epics-dependencies.puml
**Type**: Activity Diagram (PlantUML)  
**Purpose**: Visualizes the execution flow and dependencies between migration epics across all 7 phases

**Key Features**:
- **Sequential Dependencies**: Shows mandatory phase ordering (1→2→3→4→5/6→7)
- **Parallel Execution**: Illustrates where epics can run concurrently
- **Iterative Patterns**: Represents Phase 4's per-service-slice execution model
- **Agent Ownership**: Each epic shows the primary owning agent
- **Lifecycle Steps**: References the 29 canonical migration steps
- **Color Coding**: Each phase has distinct colors for visual clarity

**Dependencies Visualized**:
1. Phase 1 (Discovery) must complete before any other phase
2. Phase 2 (Design) must complete before Platform preparation
3. Phase 3 (Platform) must complete before Execution
4. Phase 4 (Execution) runs iteratively per service slice
5. Phase 5 (Scaling) begins after first services are deployed
6. Phase 6 (Org Readiness) can run parallel with Phase 5
7. Phase 7 (Retirement) executes after all services are validated

## Generating Diagrams

### Using PlantUML
```bash
# Install PlantUML (requires Java)
sudo apt-get install plantuml

# Generate PNG from PlantUML source
plantuml migration-epics-dependencies.puml

# Generate SVG (scalable)
plantuml -tsvg migration-epics-dependencies.puml
```

### Using VS Code Extensions
- **PlantUML Extension**: Provides real-time preview and export
- **Markdown Preview Enhanced**: Supports inline PlantUML rendering

### Online Tools
- **PlantText**: http://www.planttext.com/
- **PlantUML Online Server**: http://www.plantuml.com/plantuml/

## Integration with Documentation

This diagram supports the **Migration Epics Framework** document by:
- Providing visual representation of epic dependencies
- Clarifying execution order and parallelization opportunities
- Supporting PRD development by showing epic relationships
- Enabling agent coordination through clear ownership visualization

## Usage in PRD Development

When creating detailed PRDs for specific epics:
1. Reference this diagram to understand upstream/downstream dependencies
2. Identify which supporting agents need coordination
3. Plan epic delivery considering parallel execution opportunities
4. Validate implementation order against dependency constraints

---

*These diagrams are part of the Omega Agentic Migration System documentation framework, supporting systematic monolith-to-microservices transformation.*