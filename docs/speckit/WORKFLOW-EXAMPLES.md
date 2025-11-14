# Spec Kit Workflow Examples for Omega

This document provides concrete examples of using Spec Kit for common Omega migration scenarios.

## Example 1: Migration Analysis Engine

### Complete Workflow

#### Step 1: Constitution
```
/speckit.constitution Create principles for Omega migration analysis focusing on:

CORE PRINCIPLES:
- Intelligent Analysis: Use AST parsing and pattern recognition to understand code structure
- Domain-Driven Decomposition: Identify service boundaries based on business domains
- Risk Assessment: Evaluate migration complexity and provide actionable insights
- Reference-Based Learning: Learn from Spring Modulith and other well-architected examples

TECHNICAL STANDARDS:
- Python 3.12 with type hints and comprehensive error handling
- Docker containers for isolated analysis environments
- JSON output for structured data exchange with other Omega tools
- Integration with existing checkpoint system for progress tracking
- Comprehensive logging for debugging analysis decisions

QUALITY REQUIREMENTS:
- Unit tests for all analysis algorithms
- Integration tests with Spring Modulith reference codebase
- Performance benchmarks for large codebases
- Clear documentation of analysis methodologies
- Professional communication standards (no emojis in output)
```

#### Step 2: Specification
```
/speckit.specify Build a Spring Boot migration analysis engine that can:

ANALYSIS CAPABILITIES:
- Parse Java source code using AST analysis to understand class structures, dependencies, and relationships
- Identify potential service boundaries based on package organization, class cohesion, and dependency patterns
- Analyze Spring annotations (@Service, @Repository, @Controller, @Component) to understand architectural layers
- Detect database access patterns and data model relationships
- Identify cross-cutting concerns and shared utilities

RECOMMENDATION ENGINE:
- Generate microservices decomposition suggestions with confidence scores
- Provide migration complexity assessments (low/medium/high risk)
- Suggest extraction order and dependencies between new services
- Identify shared libraries and common functionality that should remain centralized
- Flag potential issues like circular dependencies or tight coupling

OUTPUT AND INTEGRATION:
- Generate structured JSON reports compatible with Omega's checkpoint system
- Create visual dependency graphs using standard formats
- Provide detailed migration roadmaps with step-by-step instructions
- Output should integrate with existing Omega tools in /workspace/tools/
- Support both CLI execution and programmatic API access
```

#### Step 3: Implementation Plan
```
/speckit.plan The migration analysis engine should be implemented using:

TECHNOLOGY STACK:
- Python 3.12 as the core language (matching Omega dev container)
- javalang or similar library for Java AST parsing
- NetworkX for dependency graph analysis and visualization
- Click for CLI interface with comprehensive help and validation
- Pydantic for data modeling and JSON schema validation
- pytest for comprehensive testing framework

ARCHITECTURE:
- Modular design with separate analysis, recommendation, and output components
- Plugin architecture for different analysis strategies (package-based, annotation-based, dependency-based)
- Docker container execution for isolated analysis environments
- Integration with Omega's existing checkpoint system for progress tracking
- CLI and Python API interfaces for flexible usage

INTEGRATION WITH OMEGA:
- Place source code in /workspace/tools/src/migration-analyzer/
- Use Spring Modulith codebase in /workspace/data/codebase/ for testing and validation
- Follow existing tool patterns from /workspace/tools/src/
- Generate documentation in /workspace/docs/tools/migration-analyzer/
- Use existing Git workflow and commit message standards

DATA FLOW:
- Input: Path to Spring Boot application source code
- Processing: Multi-phase analysis (structure, dependencies, annotations, patterns)
- Output: JSON report, dependency graphs, migration recommendations
- Storage: Results can be stored in /workspace/checkpoints/ for session tracking
```

#### Step 4: Task Generation and Implementation
```
/speckit.tasks

/speckit.implement
```

## Example 2: Dependency Visualization Tool

### Abbreviated Workflow

#### Constitution (Reference Previous)
Use the same constitution from Example 1 or create a visualization-specific one.

#### Specification
```
/speckit.specify Create a dependency visualization tool that can:
- Generate interactive dependency graphs from Spring Boot applications
- Show package-level, class-level, and method-level dependencies
- Highlight potential service boundaries with different colors/styles
- Export visualizations in multiple formats (SVG, PNG, HTML interactive)
- Integrate with the migration analysis engine to show recommended boundaries
- Support filtering and zooming for large codebases
- Provide metrics like coupling strength and cohesion scores
```

#### Plan
```
/speckit.plan Use Python with:
- Graphviz or D3.js for graph visualization
- Flask for web-based interactive interface
- Integration with migration analysis engine output
- Docker container for web server deployment
- JSON configuration for visualization customization
```

## Example 3: Code Refactoring Assistant

### Constitution
```
/speckit.constitution Create principles for automated refactoring assistance:

SAFETY FIRST:
- Never modify source code without explicit user confirmation
- Provide detailed previews of all proposed changes
- Create backup recommendations and rollback strategies
- Validate refactoring safety through comprehensive testing

INTELLIGENCE:
- Learn from successful migration patterns in reference codebases
- Apply domain-driven design principles to refactoring suggestions
- Consider performance and scalability implications
- Respect existing code style and architectural decisions

INTEGRATION:
- Work seamlessly with existing development workflows
- Provide IDE integration where possible
- Support version control integration with clear commit strategies
- Generate comprehensive documentation for all changes
```

### Specification
```
/speckit.specify Build a refactoring assistant that can:
- Analyze code identified for extraction by the migration analysis engine
- Generate step-by-step refactoring instructions for service extraction
- Suggest API interface designs for new microservices
- Identify shared code that should be extracted to libraries
- Provide database migration strategies for data separation
- Generate boilerplate code for new service structures
- Validate refactoring safety through dependency analysis
- Create comprehensive test migration strategies
```

## Example 4: Migration Progress Tracker

### Specification
```
/speckit.specify Create a migration progress tracking system that:
- Tracks the status of microservices extraction across multiple services
- Integrates with Omega's checkpoint system for persistent state
- Provides migration timeline and milestone tracking
- Generates progress reports and dashboards
- Identifies blockers and dependencies between migration tasks
- Supports rollback and recovery strategies
- Provides integration with project management tools
```

## Best Practices from Examples

### 1. Always Start with Constitution
- Establish clear principles before diving into specifications
- Consider safety, quality, and integration requirements
- Define technical standards that align with Omega's architecture

### 2. Be Specific in Specifications
- Use concrete examples and clear acceptance criteria
- Consider integration points with existing Omega tools
- Think about data formats and API interfaces

### 3. Plan with Omega Context
- Reference existing tools and structures
- Use the dev container environment
- Follow established patterns and conventions

### 4. Iterate and Refine
- Use `/speckit.clarify` for complex requirements
- Apply `/speckit.analyze` before implementation
- Create `/speckit.checklist` for quality validation

## Integration Patterns

### With Checkpoints
```bash
# Before starting spec work
./tools/src/create-checkpoint.sh -e "Spec-Driven Development" -t "Migration analyzer specification"

# After completing implementation
./tools/src/create-checkpoint.sh -e "Migration Tools" -t "Completed migration analyzer with spec-driven approach"
```

### With Spring Modulith Reference
```
# Always reference in specifications
"Use the Spring Modulith codebase in /workspace/data/codebase/spring-modulith/ as a reference implementation for well-structured modular Spring applications"
```

### With Existing Tools
```
# Plan integration
"Integrate with existing Omega tools in /workspace/tools/src/ and follow the same patterns for CLI interfaces, error handling, and documentation"
```

## Common Pitfalls and Solutions

### Pitfall: Too Generic Specifications
**Bad**: "Build a migration tool"
**Good**: "Build a migration analysis engine that parses Spring Boot applications and identifies service boundaries based on package structure and dependency patterns"

### Pitfall: Ignoring Omega Context  
**Bad**: Planning tools in isolation
**Good**: "Place in /workspace/tools/src/, integrate with checkpoints, use Spring Modulith for testing"

### Pitfall: Missing Quality Considerations
**Bad**: Focus only on functionality
**Good**: Include testing, documentation, error handling, and professional communication standards

### Pitfall: One-Shot Development
**Bad**: `/speckit.specify` then `/speckit.implement`
**Good**: Use the full workflow with quality gates: constitution → specify → clarify → plan → tasks → analyze → implement