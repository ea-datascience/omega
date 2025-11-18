# Implementation Plan: System Discovery and Baseline Assessment

**Branch**: `001-system-discovery-baseline` | **Date**: November 17, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-system-discovery-baseline/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Epic 1.1 implements a comprehensive legacy system analysis platform that combines static analysis (Context Mapper, Structurizr, CodeQL, Microsoft AppCAT) with runtime analysis (SigNoz, OpenTelemetry) to create accurate migration baselines. The system provides automated discovery of Spring Boot monolith architectures, performance baselines, and gap analysis between intended and actual system behaviors, enabling data-driven migration decisions with quantified risk assessments.

## Technical Context

**Language/Version**: Python 3.12+ (per constitution requirements) with Java 17+ for analysis tools  
**Primary Dependencies**: Microsoft Agent Framework, FastAPI, Docker, OpenTelemetry, Context Mapper, Structurizr, CodeQL, Microsoft AppCAT  
**Storage**: PostgreSQL 15+ with pg_vector for analysis artifacts, MinIO for file storage, Redis Cluster for caching  
**Testing**: pytest, testcontainers, contract testing with Pact, migration test framework  
**Target Platform**: Linux server (containerized), Kubernetes deployment ready  
**Project Type**: web (backend API + analysis engine + dashboard frontend)  
**Performance Goals**: Analyze 1M+ LOC within 2 hours, support 10 concurrent analyses, <1% runtime overhead for observability  
**Constraints**: 95% dependency identification accuracy, <2s API response times, enterprise security compliance (SOC2)  
**Scale/Scope**: Enterprise portfolio analysis (10+ monoliths), 24/7 operations, enterprise integration via REST APIs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Migration Lifecycle Compliance**:
- [x] Feature aligns with specified lifecycle steps (1, 5, 6, 12, 13, 14 from Discover & Baseline phase)
- [x] Agent roles clearly identified (Planner/Conductor owner, Architect & Decomposition, SRE/Observability, Security & Compliance supporting)
- [x] Test strategy follows constitution taxonomy (Integration, Migration, Contract tests specified)
- [x] Human-in-the-loop points defined (architectural review validation, enterprise architecture board approval, manual validation workflows)
- [x] Integration with cockpit monitoring planned (analysis progress tracking, quality metrics, user adoption analytics)

**Core Principles Compliance**:
- [x] Migration Intelligence: Two-pronged analysis strategy provides actionable insights combining static and runtime analysis with gap analysis
- [x] Agent-Driven: Multi-agent orchestration with clear role assignments and supporting agent coordination
- [x] Reference-Based: Validates against Spring Modulith reference codebase and proven enterprise patterns
- [x] Quality & Safety: 95% accuracy validation, enterprise security compliance, human oversight for critical decisions
- [x] Test-Driven: Functional requirements map to specific test scenarios and measurable success criteria

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Analysis Engine Backend
tools/
├── src/
│   ├── analysis/
│   │   ├── static/           # Context Mapper, Structurizr, CodeQL, AppCAT integrations
│   │   ├── runtime/          # SigNoz, OpenTelemetry instrumentation
│   │   └── gap/              # Gap analysis and risk assessment
│   ├── models/
│   │   ├── project.py        # Analysis Project entity
│   │   ├── architecture.py   # System Architecture entity
│   │   ├── dependency.py     # Dependency Graph entity
│   │   ├── baseline.py       # Performance Baseline entity
│   │   ├── risk.py           # Risk Assessment entity
│   │   ├── compliance.py     # Compliance Record entity
│   │   └── boundary.py       # Service Boundary entity
│   ├── services/
│   │   ├── orchestration/    # Microsoft Agent Framework-based analysis workflow orchestration
│   │   ├── reporting/        # Report generation and export
│   │   └── validation/       # Accuracy validation and human oversight
│   ├── api/
│   │   ├── analysis/         # Analysis management endpoints
│   │   ├── reports/          # Report retrieval endpoints
│   │   └── health/           # System health and monitoring
│   └── cli/
│       ├── analyze.py        # CLI for analysis execution
│       └── validate.py       # CLI for accuracy validation
├── tests/
│   ├── contract/             # API contract tests
│   ├── integration/          # Tool integration tests
│   ├── migration/            # Migration accuracy validation tests
│   └── unit/                 # Unit tests for models and services
└── docker/
    ├── analysis-engine/      # Main analysis engine container
    ├── signoz/               # SigNoz observability stack
    └── tools/                # Static analysis tools container

# Dashboard Frontend
dashboard/
├── src/
│   ├── components/
│   │   ├── analysis/         # Analysis progress and results components
│   │   ├── reports/          # Report visualization components
│   │   └── validation/       # Human validation interface components
│   ├── pages/
│   │   ├── projects/         # Analysis project management
│   │   ├── dashboard/        # Analysis monitoring dashboard
│   │   └── reports/          # Report viewing and export
│   └── services/
│       ├── api/              # Backend API integration
│       └── validation/       # Human-in-the-loop workflows
└── tests/
    ├── e2e/                  # End-to-end user journey tests
    ├── integration/          # Frontend-backend integration tests
    └── unit/                 # Component unit tests
```

**Structure Decision**: Web application architecture selected with separate analysis engine backend and dashboard frontend, powered by Microsoft Agent Framework for agentic orchestration. The backend focuses on containerized analysis orchestration and API services, while the frontend provides human-in-the-loop interfaces for validation and reporting. This structure supports enterprise integration requirements, multi-agent orchestration patterns defined in the constitution, and Docker-based deployment from devcontainer environments.

## Complexity Tracking

No constitution violations identified - all requirements align with migration lifecycle principles and agent-driven architecture patterns.

---

## Phase 0: Research (✅ COMPLETED)

**Objective**: Resolve technical unknowns and establish technology foundation

**Key Decisions Made**:
- **Static Analysis Stack**: Context Mapper + Structurizr + CodeQL + Microsoft AppCAT for comprehensive architectural discovery
- **Runtime Analysis Platform**: SigNoz with OpenTelemetry for lightweight observability with <1% performance overhead
- **Core Technology**: Python 3.12+ with FastAPI for constitution compliance and high-performance async APIs
- **Storage Architecture**: PostgreSQL 15+ with pg_vector for analysis artifacts and vector similarity search
- **Orchestration**: Apache Airflow for workflow management with custom analysis tool operators

**Research Deliverable**: [research.md](./research.md) - Comprehensive technology analysis and decision rationale

---

## Phase 1: Design & Contracts (✅ COMPLETED)

**Objective**: Generate data model, API contracts, and implementation foundation

### Deliverables Created:

#### 1. Data Model Design
- **File**: [data-model.md](./data-model.md)
- **Key Entities**: AnalysisProject, SystemArchitecture, DependencyGraph, PerformanceBaseline, RiskAssessment, ComplianceRecord, ServiceBoundary
- **Database Schema**: PostgreSQL with pg_vector extension, comprehensive indexing strategy, business rule constraints
- **Entity Relationships**: Full ERD with navigation paths and computed fields for complex analysis queries

#### 2. API Contracts
- **REST API**: [contracts/analysis-api.yaml](./contracts/analysis-api.yaml) - OpenAPI 3.0.3 specification with comprehensive endpoints
- **GraphQL Schema**: [contracts/analysis-schema.graphql](./contracts/analysis-schema.graphql) - Complex query interface for analysis relationships
- **Authentication**: OAuth 2.0/OIDC with JWT tokens and role-based access control
- **API Coverage**: Project management, analysis operations, baselines, assessments, boundaries, compliance, reports, validation workflows

#### 3. Implementation Guidance
- **File**: [quickstart.md](./quickstart.md)
- **Coverage**: Development setup, production deployment, API usage examples, CLI commands, configuration reference
- **Docker Configuration**: Multi-service architecture with analysis engine, PostgreSQL, Redis, SigNoz, dashboard
- **Enterprise Integration**: Kubernetes deployment, authentication providers, monitoring, troubleshooting

#### 4. Agent Context Update
- **GitHub Copilot Integration**: Updated with Python 3.12+, LangChain/LangGraph, FastAPI, PostgreSQL 15+, analysis tool stack
- **Technology Stack**: Comprehensive context for AI-assisted development with migration-specific patterns

### Constitution Check - Post Design ✅

**Migration Lifecycle Compliance**:
- ✅ Feature aligns with specified lifecycle steps (1, 5, 6, 12, 13, 14) - All Phase 1 steps covered in design
- ✅ Agent roles clearly implemented (Planner/Conductor orchestration, supporting agent coordination via API)
- ✅ Test strategy integrated (Contract tests via Pact, Integration tests via testcontainers, Migration validation framework)
- ✅ Human-in-the-loop workflows designed (Approval endpoints, validation interfaces, audit trails)
- ✅ Monitoring integration planned (OpenTelemetry instrumentation, SigNoz observability, health endpoints)

**Core Principles Compliance**:
- ✅ Migration Intelligence: Two-pronged analysis strategy implemented with gap analysis and quantified risk scoring
- ✅ Agent-Driven: Multi-agent API orchestration with role-based endpoints and workflow coordination
- ✅ Reference-Based: Spring Modulith validation patterns integrated, enterprise architecture approval workflows
- ✅ Quality & Safety: 95% accuracy validation implemented, enterprise security (OAuth2/OIDC), comprehensive audit trails
- ✅ Test-Driven: All functional requirements mapped to API endpoints with testable acceptance criteria

**Design Quality Assessment**:
- **API Completeness**: 100% functional requirements covered by REST + GraphQL APIs
- **Data Model Integrity**: All entity relationships defined with proper constraints and validation rules  
- **Security Integration**: Enterprise-grade authentication, authorization, audit logging, encryption
- **Scalability Design**: Container orchestration ready, horizontal scaling support, resource management
- **Human Integration**: Comprehensive validation workflows, approval processes, enterprise integration patterns

---

## Next Phase: Implementation Planning

The design phase is complete with all constitutional requirements satisfied. Ready to proceed to:

**Phase 2: Task Decomposition** (`/speckit.tasks` command)
- Break down implementation into actionable tasks
- Define agent assignments and coordination workflows  
- Establish development milestones and dependencies
- Create testing strategies and validation checkpoints

**Implementation Foundation Established**:
- ✅ Technology stack finalized and documented
- ✅ Data architecture designed with full entity modeling
- ✅ API contracts specified for all functional requirements
- ✅ Deployment patterns defined for enterprise integration
- ✅ Human-in-the-loop workflows designed for validation
- ✅ Agent context updated for AI-assisted development
