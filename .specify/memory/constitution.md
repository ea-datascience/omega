<!--
Sync Impact Report:
Version change: template → 1.0.0
Added sections: Migration Lifecycle, Agent Archetypes, Test Strategy
Templates requiring updates: ✅ constitution updated
Follow-up TODOs: Review spec-template.md, plan-template.md, tasks-template.md for lifecycle alignment
-->

# Omega Agentic Migration System Constitution

## Core Principles

### I. Migration Intelligence First
Every feature must advance intelligent software migration from monoliths to microservices. Provide insights humans couldn't easily derive manually through AI-powered analysis of Spring Boot codebases. Generate actionable, practical recommendations over theoretical analysis. Learn from real-world patterns in reference architectures like Spring Modulith. Prioritize automation that enhances human decision-making rather than replacing it.

### II. Agent-Driven Development  
Build systems that amplify human capabilities through intelligent automation. Design tools that can be composed and orchestrated in multi-agent workflows. Create learning systems that improve from analyzing codebases and migration outcomes. Enable systematic approaches to complex migration decisions. Support both CLI and programmatic interfaces for maximum flexibility and integration.

### III. Reference-Based Learning
Use proven, well-architected examples as learning foundations. Extract and apply patterns from Spring Modulith and other successful modular architectures. Validate all approaches against real-world implementations before recommending them. Build comprehensive knowledge base of migration patterns, anti-patterns, and best practices. Maintain traceability from recommendations back to proven examples.

### IV. Quality and Safety (NON-NEGOTIABLE)
Reliability and correctness in migration recommendations are paramount. Never modify source code without explicit user confirmation and detailed previews. Comprehensive testing with real codebases including edge cases and problematic legacy scenarios. Clear error handling and graceful degradation for all analysis tools. Professional communication standards with no decorative elements or emojis.

### V. Test-Driven Migration
All specifications transform into executable tests before implementation. Every requirement must have associated test cases covering migration lifecycle aspects. Agent-aligned testing where each agent role defines and maintains relevant test types. Human-in-the-loop validation for critical migration decisions and security assessments. Coverage across all 29 migration lifecycle steps, not just application behavior.

## Migration Lifecycle Framework

Omega follows a structured 29-step migration lifecycle across 7 phases. All specifications, plans, and tasks must reference specific lifecycle steps:

**Phases**: Discover & Baseline → Decompose & Design Guardrails → Prepare Platform → Strangler Execution → Scale & Optimize → Org Readiness → Retire Monolith

**Normative Rules**:
- Every requirement, plan element, and task must reference at least one lifecycle step (1-29)
- Each step must identify accountable agent roles and supporting roles
- Migration follows incremental vertical slices using Strangler Fig pattern
- All artifacts must be traceable, testable, and observable throughout migration

## Agent Orchestration and Monitoring

### Multi-Agent Cockpit System
Centralized monitoring dashboard providing real-time visibility into all agent activities and states. Human oversight of distributed agent operations like a production floor of a robotic factory. Clear process mapping and workflow visualization with current progress tracking at every step. Well-defined human intervention points for critical decisions and risk management.

### Metrics and Telemetry Framework
Comprehensive observability through performance metrics (execution times, accuracy scores, completion rates), process metrics (workflow bottlenecks, intervention patterns, error rates), and quality metrics (recommendation acceptance rates, post-migration validation scores). Integration with existing Omega checkpoint system and external monitoring tools.

### Agent Archetypes
Fixed set of specialized agent roles: Planner/Conductor, Architect & Decomposition, API & Integration, Data Migration, Platform/CI-CD, QA/Quality, Security & Compliance, SRE/Observability/FinOps, Release/Change. Each agent has defined persona, tools, memory, and lifecycle hooks with specific KPIs and deliverables.

## Technical Standards

### Development Environment
Python 3.12+ with comprehensive type hints and error handling. Docker containers for reproducible and isolated execution environments. Integration with Omega development container and existing toolchain. JSON for structured data exchange between agents and systems. CLI and programmatic API interfaces for flexible usage patterns.

### Architecture Requirements
Modular design with clear separation of concerns between agent roles. Plugin architecture for extensible analysis strategies and new migration patterns. Integration with checkpoint and documentation systems for session continuity. Structured output formats compatible with existing Omega infrastructure. Version control integration following established Git workflows and commit standards.

## Governance

This constitution supersedes all other development practices within the Omega project. All specifications, plans, and implementations must demonstrate compliance with these principles and lifecycle requirements. 

Amendments require documentation of rationale, impact analysis, and migration plan for affected artifacts. Version changes follow semantic versioning: MAJOR for backward-incompatible principle changes, MINOR for new principles or material expansions, PATCH for clarifications and refinements.

All agent roles must verify compliance during reviews. Complexity in migration recommendations must be justified with reference to proven patterns. Human accountability remains paramount for all risk-bearing decisions despite automation capabilities.

**Version**: 1.0.0 | **Ratified**: 2025-11-14 | **Last Amended**: 2025-11-14
