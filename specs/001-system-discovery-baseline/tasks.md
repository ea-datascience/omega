# Tasks: System Discovery and Baseline Assessment

**Input**: Design documents from `/specs/001-system-discovery-baseline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL and not explicitly requested in the specification - focusing on implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- **Analysis Engine Backend**: `tools/src/`
- **Dashboard Frontend**: `dashboard/src/`
- **Tests**: `tools/tests/`, `dashboard/tests/`
- **Docker**: `tools/docker/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create analysis engine project structure in tools/ per implementation plan
- [x] T002 Initialize Python 3.12+ project with FastAPI, Microsoft Agent Framework, and OpenTelemetry dependencies in tools/pyproject.toml
- [x] T003 [P] Initialize dashboard Angular project with dependencies in dashboard/package.json
- [ ] T004 [P] Configure Python linting and formatting tools (black, flake8, mypy) in tools/pyproject.toml
- [x] T005 [P] Configure TypeScript/Angular linting and formatting in dashboard/.eslintrc.json
- [x] T006 Create Docker Compose configuration for development environment in docker-compose.yml
- [x] T007 [P] Setup analysis tools container configuration in tools/docker/analysis-engine/Dockerfile
- [x] T008 [P] Setup SigNoz observability stack configuration in tools/docker/signoz/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Setup PostgreSQL database schema and Alembic migrations framework in tools/alembic/
- [x] T010 [P] Implement OAuth 2.0/OIDC authentication middleware in tools/src/omega_analysis/auth/middleware.py
- [x] T011 [P] Setup FastAPI routing and middleware structure in tools/src/omega_analysis/api/main.py
- [x] T012 Create base SQLAlchemy models and database connection in tools/src/omega_analysis/models/base.py
- [x] T013 [P] Configure error handling and logging infrastructure in tools/src/omega_analysis/logging/config.py
- [x] T014 [P] Setup environment configuration management in tools/src/omega_analysis/config/settings.py
- [x] T015 [P] Create Redis client configuration and caching utilities in tools/src/omega_analysis/cache/manager.py
- [x] T016 [P] Setup MinIO client for analysis artifact storage in tools/src/omega_analysis/storage/service.py
- [x] T017 [P] Configure OpenTelemetry instrumentation in tools/src/omega_analysis/tracing/config.py
- [x] T018 Create database migration for core entities schema in tools/alembic/versions/001_initial_schema.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Legacy System Analysis (Priority: P1) 🎯 MVP

**Goal**: Enterprise architects can analyze Spring Boot monoliths to understand architecture, dependencies, and performance through automated static and runtime analysis with gap analysis

**Independent Test**: Provide Spring Modulith reference codebase to analysis engine and validate accurate dependency graphs, C4 diagrams, and performance baselines matching manual architectural review

### Core Data Models for User Story 1

- [x] T019 [P] [US1] Create AnalysisProject model in tools/src/omega_analysis/models/analysis.py
- [x] T020 [P] [US1] Create SystemArchitecture model in tools/src/omega_analysis/models/analysis.py  
- [x] T021 [P] [US1] Create DependencyGraph model in tools/src/omega_analysis/models/analysis.py
- [x] T022 [P] [US1] Create PerformanceBaseline model in tools/src/omega_analysis/models/analysis.py

### Static Analysis Integration for User Story 1

- [x] T023 [P] [US1] Implement Context Mapper integration in tools/src/analysis/static/context_mapper.py ⚠️ **INCOMPLETE: Uses custom Python implementation instead of actual Context Mapper Java library**
- [x] T024 [P] [US1] Implement Structurizr integration for C4 diagrams in tools/src/analysis/static/structurizr.py ⚠️ **INCOMPLETE: Uses custom Python implementation instead of Structurizr DSL/CLI**
- [x] T025 [P] [US1] Implement CodeQL integration for security scanning in tools/src/analysis/static/codeql.py ⚠️ **INCOMPLETE: Wrapper exists but CodeQL CLI binary not installed**
- [x] T026 [P] [US1] Implement Microsoft AppCAT integration in tools/src/analysis/static/appcat.py ⚠️ **INCOMPLETE: Wrapper exists but AppCAT binary not installed**
- [x] T027 [US1] Create static analysis orchestration service using Microsoft Agent Framework in tools/src/services/orchestration/static_analyzer.py

### ⚠️ CRITICAL GAP: Third-Party Tool Installation and Integration (BLOCKING)

**Issue**: Current implementations use custom Python code instead of actual third-party tools. This bypasses the sophisticated analysis capabilities these tools provide.

**Impact**: System cannot deliver the promised 95% accuracy in dependency graphs and architectural analysis without the real tools.

**Required Actions**:

- [ ] T023a [P] [US1] Install Context Mapper Java library (Maven dependency org.contextmapper:context-mapper-dsl) in tools/src/utils/install-context-mapper.sh
- [ ] T023b [US1] Rewrite Context Mapper integration to use actual Java library via subprocess/JVM bridge in tools/src/analysis/static/context_mapper.py
- [ ] T024a [P] [US1] Install Structurizr CLI in tools/bin/structurizr/ via tools/src/utils/install-structurizr.sh
- [ ] T024b [US1] Rewrite Structurizr integration to use CLI and DSL files in tools/src/analysis/static/structurizr.py
- [ ] T025a [P] [US1] Install CodeQL CLI and Java query packs in tools/bin/codeql/ via tools/src/utils/install-codeql.sh
- [ ] T025b [US1] Update CodeQL integration to use installed CLI (remove mock fallback for production) in tools/src/analysis/static/codeql.py
- [ ] T026a [P] [US1] Install Microsoft AppCAT CLI in tools/bin/appcat/ via tools/src/utils/install-appcat.sh
- [ ] T026b [US1] Update AppCAT integration to use installed CLI (remove mock fallback for production) in tools/src/analysis/static/appcat.py
- [ ] T027a [US1] Update static analysis orchestrator to handle real tool execution and error handling in tools/src/services/orchestration/static_analyzer.py
- [ ] T027b [US1] Add tool version validation and health checks in tools/src/utils/tool_health_checker.py
- [ ] T027c [P] [US1] Update Docker/dev container configuration to include all third-party tools in .devcontainer/Dockerfile
- [ ] T027d [P] [US1] Create comprehensive tool installation documentation in docs/setup/static-analysis-tools.md

**Checkpoint**: Tools properly installed and integrated - ready for actual architectural analysis

### Runtime Analysis Integration for User Story 1

- [x] T028 [P] [US1] Implement SigNoz deployment automation in tools/src/analysis/runtime/signoz_deployer.py
- [x] T029 [P] [US1] Implement OpenTelemetry instrumentation templates in tools/src/analysis/runtime/otel_instrumentation.py
- [x] T030 [P] [US1] Create synthetic load testing framework in tools/src/analysis/runtime/load_generator.py
- [x] T031 [US1] Create runtime analysis orchestration service using Microsoft Agent Framework in tools/src/services/orchestration/runtime_analyzer.py

### Gap Analysis Engine for User Story 1

- [ ] T032 [US1] Implement gap analysis comparison engine in tools/src/analysis/gap/gap_analyzer.py
- [ ] T033 [US1] Create coupling metrics calculation in tools/src/analysis/gap/coupling_metrics.py
- [ ] T034 [US1] Implement architectural drift detection in tools/src/analysis/gap/drift_detector.py

### API Endpoints for User Story 1

- [x] T035 [US1] Implement project management endpoints in tools/src/omega_analysis/api/v1/projects.py (AnalysisProject CRUD API)
- [x] T036 [US1] Implement analysis operations endpoints in tools/src/omega_analysis/api/v1/analysis.py
- [x] T037 [US1] Implement architecture retrieval endpoints in tools/src/omega_analysis/api/v1/architecture.py
- [x] T038 [US1] Implement dependency graph endpoints in tools/src/omega_analysis/api/v1/dependencies.py
- [x] T039 [US1] Implement performance baselines endpoints in tools/src/omega_analysis/api/v1/baselines.py

### Analysis Orchestration for User Story 1

- [x] T040 [US1] Create main analysis workflow orchestrator in tools/src/omega_analysis/services/orchestration/analysis_orchestrator.py
- [x] T041 [US1] Implement analysis progress tracking in tools/src/omega_analysis/services/orchestration/progress_tracker.py
- [x] T042 [US1] Create analysis result aggregation service in tools/src/omega_analysis/services/orchestration/result_aggregator.py
- [x] T043 [US1] Create report generation CLI utility in tools/src/utils/report_generator.py (generates static analysis reports with C4 diagrams without dashboard dependencies; includes CodeQL and AppCAT integration placeholders for future implementation)

### Dashboard Components for User Story 1

- [x] T044 [P] [US1] Create project list component in dashboard/src/components/analysis/project-list.component.ts
- [x] T045 [P] [US1] Create analysis progress component in dashboard/src/components/analysis/analysis-progress.component.ts
- [x] T046 [P] [US1] Create architecture visualization component in dashboard/src/components/analysis/architecture-viewer.component.ts (948 lines: TS 327, HTML 219, SCSS 402)
- [x] T047 [P] [US1] Create dependency graph visualization in dashboard/src/components/analysis/dependency-graph.component.ts (1,494 lines: TS 567, HTML 296, SCSS 441, Model 191)
- [x] T048 [P] [US1] Create performance metrics dashboard in dashboard/src/components/analysis/performance-dashboard.component.ts (1,403 lines: TS 335, HTML 313, SCSS 579, Model 176)
- [x] T049 [US1] Create main analysis dashboard page in dashboard/src/pages/dashboard/analysis-dashboard.page.ts (1,356 lines: TS 394, HTML 240, SCSS 515, Model 147, Service 60)

**Checkpoint**: At this point, User Story 1 should be fully functional with complete automated analysis capabilities

---

## Phase 4: User Story 2 - Migration Readiness Assessment (Priority: P2)

**Goal**: Engineering managers can understand migration complexity, effort estimates, and risk factors for informed go/no-go decisions with quantified risk scoring

**Independent Test**: Analyze systems with known migration outcomes and validate readiness scores correlate with actual migration success rates

### Risk Assessment Models for User Story 2

- [ ] T050 [P] [US2] Create RiskAssessment model in tools/src/models/risk.py
- [ ] T051 [P] [US2] Create ServiceBoundary model in tools/src/models/boundary.py
- [ ] T052 [P] [US2] Create supporting risk factor models in tools/src/models/risk_factors.py

### Risk Assessment Engine for User Story 2

- [ ] T053 [US2] Implement quantitative risk scoring framework in tools/src/services/assessment/risk_scorer.py
- [ ] T054 [US2] Create migration complexity analyzer in tools/src/services/assessment/complexity_analyzer.py
- [ ] T055 [US2] Implement service boundary recommendation engine in tools/src/services/assessment/boundary_recommender.py
- [ ] T056 [US2] Create effort estimation algorithms in tools/src/services/assessment/effort_estimator.py

### Assessment API Endpoints for User Story 2

- [ ] T057 [US2] Implement risk assessment endpoints in tools/src/api/analysis/assessments.py
- [ ] T058 [US2] Implement service boundary endpoints in tools/src/api/analysis/boundaries.py
- [ ] T059 [US2] Create boundary approval workflow endpoints in tools/src/api/validation/boundary_approval.py

### Human-in-the-Loop Validation for User Story 2

- [ ] T060 [US2] Implement architect approval workflow in tools/src/services/validation/approval_workflow.py
- [ ] T061 [US2] Create validation result tracking in tools/src/services/validation/validation_tracker.py
- [ ] T062 [US2] Implement notification system for approval requests in tools/src/services/validation/notification_service.py

### Dashboard Components for User Story 2

- [ ] T063 [P] [US2] Create risk assessment dashboard in dashboard/src/components/assessment/risk-dashboard.component.ts
- [ ] T064 [P] [US2] Create service boundary visualization in dashboard/src/components/assessment/boundary-viewer.component.ts
- [ ] T065 [P] [US2] Create approval workflow interface in dashboard/src/components/validation/approval-interface.component.ts
- [ ] T066 [US2] Create migration readiness report page in dashboard/src/pages/reports/readiness-report.page.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with complete risk assessment capabilities

---

## Phase 5: User Story 3 - Compliance and Security Baseline Documentation (Priority: P3)

**Goal**: Compliance officers and security engineers get comprehensive documentation of system state including data flows, security controls, and regulatory compliance for audit purposes

**Independent Test**: Validate generated compliance documentation passes enterprise security review and meets audit requirements

### Compliance Models for User Story 3

- [ ] T067 [P] [US3] Create ComplianceRecord model in tools/src/models/compliance.py
- [ ] T068 [P] [US3] Create supporting compliance requirement models in tools/src/models/compliance_requirements.py

### Compliance Analysis Engine for User Story 3

- [ ] T069 [US3] Implement regulatory framework analyzer in tools/src/services/compliance/regulatory_analyzer.py
- [ ] T070 [US3] Create data classification engine in tools/src/services/compliance/data_classifier.py
- [ ] T071 [US3] Implement security control assessment in tools/src/services/compliance/security_assessor.py
- [ ] T072 [US3] Create audit trail generator in tools/src/services/compliance/audit_trail_generator.py

### Compliance API Endpoints for User Story 3

- [ ] T073 [US3] Implement compliance records endpoints in tools/src/api/analysis/compliance.py
- [ ] T074 [US3] Create compliance report generation endpoints in tools/src/api/reports/compliance_reports.py

### Report Generation System for User Story 3

- [ ] T075 [US3] Implement comprehensive report generator in tools/src/services/reporting/report_generator.py
- [ ] T076 [US3] Create PDF report templates in tools/src/services/reporting/templates/
- [ ] T077 [US3] Implement Excel export functionality in tools/src/services/reporting/excel_exporter.py

### Dashboard Components for User Story 3

- [ ] T078 [P] [US3] Create compliance dashboard in dashboard/src/components/compliance/compliance-dashboard.component.ts
- [ ] T079 [P] [US3] Create audit trail viewer in dashboard/src/components/compliance/audit-trail.component.ts
- [ ] T080 [P] [US3] Create report generation interface in dashboard/src/components/reports/report-generator.component.ts
- [ ] T081 [US3] Create compliance report page in dashboard/src/pages/reports/compliance-report.page.ts

**Checkpoint**: All user stories should now be independently functional with complete compliance documentation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T082 [P] Create comprehensive API documentation in docs/api/
- [ ] T083 [P] Implement health check endpoints in tools/src/api/health/health.py
- [ ] T084 [P] Add system metrics and monitoring in tools/src/api/health/metrics.py
- [ ] T085 [P] Implement GraphQL query interface in tools/src/api/graphql/
- [ ] T086 [P] Create CLI tool for analysis operations in tools/src/cli/analyze.py
- [ ] T087 [P] Implement validation CLI in tools/src/cli/validate.py
- [ ] T088 Code cleanup and refactoring across all modules
- [ ] T089 Performance optimization for large codebase analysis
- [ ] T090 Security hardening and penetration testing
- [ ] T091 Run quickstart.md validation with Spring Modulith reference

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - ⚠️ **BLOCKED**: T023a-T027d must be completed to fix third-party tool integration before US1 can be considered production-ready
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 models but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses analysis results from US1/US2 but independently testable

### Critical Path Update

**IMPORTANT**: The following tasks are now on the critical path and MUST be completed before US1 can be validated:

1. **Tool Installation (Parallel)**: T023a, T024a, T025a, T026a, T027c
2. **Tool Integration (Sequential)**: T023b, T024b, T025b, T026b
3. **Orchestration Update**: T027a, T027b
4. **Documentation**: T027d

**Estimated Impact**: 2-3 weeks additional work to properly integrate real tools

### Within Each User Story

- Models before services
- Services before API endpoints
- Core implementation before dashboard components
- Backend before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- API endpoints within a story marked [P] can run in parallel  
- Dashboard components within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create AnalysisProject model in tools/src/models/project.py"
Task: "Create SystemArchitecture model in tools/src/models/architecture.py"
Task: "Create DependencyGraph model in tools/src/models/dependency.py"
Task: "Create PerformanceBaseline model in tools/src/models/baseline.py"

# Launch all static analysis integrations together:
Task: "Implement Context Mapper integration in tools/src/analysis/static/context_mapper.py"
Task: "Implement Structurizr integration in tools/src/analysis/static/structurizr.py"
Task: "Implement CodeQL integration in tools/src/analysis/static/codeql.py"
Task: "Implement Microsoft AppCAT integration in tools/src/analysis/static/appcat.py"

# Launch all dashboard components together:
Task: "Create project list component in dashboard/src/components/analysis/project-list.component.ts"
Task: "Create analysis progress component in dashboard/src/components/analysis/analysis-progress.component.ts"
Task: "Create architecture visualization component in dashboard/src/components/analysis/architecture-viewer.component.ts"
```

---

## Implementation Strategy

### ⚠️ CRITICAL ISSUE DISCOVERED

**Current Status**: User Story 1 dashboard components (T044-T049) are complete, but the underlying static analysis tools (T023-T026) are incorrectly implemented.

**What's Wrong**:
- Context Mapper: Custom Python implementation instead of actual Java library
- Structurizr: Custom Python implementation instead of DSL/CLI
- CodeQL: Wrapper exists but binary not installed (falls back to mock data)
- AppCAT: Wrapper exists but binary not installed (falls back to mock data)

**Consequence**: System cannot achieve the promised 95% accuracy without real tools.

**Required Fix**: Complete T023a-T027d (12 new tasks) before US1 can be production-ready.

### Revised MVP Strategy (User Story 1)

**Phase 1: Current State (INCOMPLETE)**
1. ✅ Setup (8 tasks) - Complete
2. ✅ Foundational (18 tasks) - Complete
3. ✅ User Story 1 Backend (18 tasks) - Complete but using mock/custom tools
4. ✅ User Story 1 Dashboard (6 tasks) - Complete
5. ⚠️ **CRITICAL GAP**: Real tool integration missing

**Phase 2: Tool Integration Fix (REQUIRED)**
1. Install all third-party tools (T023a, T024a, T025a, T026a) - 4 tasks in parallel
2. Rewrite integrations to use real tools (T023b, T024b, T025b, T026b) - 4 tasks sequential
3. Update orchestration and add health checks (T027a, T027b) - 2 tasks
4. Update Docker/docs (T027c, T027d) - 2 tasks in parallel
5. **VALIDATE**: Test with real tools against Spring Modulith

**Estimated Additional Timeline**: 2-3 weeks to properly integrate real tools

### Incremental Delivery

1. Complete Setup + Foundational → Analysis platform foundation ready
2. Add User Story 1 → ⚠️ **BLOCKED: Must fix tool integration (T023a-T027d)** → Test with reference codebases → Deploy/Demo (MVP with automated analysis!)
3. Add User Story 2 → Test risk assessment → Deploy/Demo (Added migration readiness)
4. Add User Story 3 → Test compliance → Deploy/Demo (Complete enterprise solution)
5. Each story adds significant value without breaking previous functionality

**Current Reality**: Dashboard works but shows mock/incomplete analysis data. Real tools needed for production deployment.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational phases together (18 tasks) ✅ **DONE**
2. **CRITICAL PATH NOW**: Tool integration fix (T023a-T027d, 12 tasks) - **2-3 weeks**
   - **DevOps/Senior**: Install tools and Docker integration (T023a, T024a, T025a, T026a, T027c)
   - **Backend Lead**: Rewrite integrations (T023b, T024b, T025b, T026b)
   - **Backend Dev**: Update orchestration (T027a, T027b, T027d)
3. Once tools are integrated:
   - **Senior Developer**: User Story 1 validation and refinement
   - **Mid-level Developer**: User Story 2 (17 tasks) - Risk assessment
   - **Junior/Mid Developer**: User Story 3 (15 tasks) - Compliance documentation
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (10 tasks)

### Resource Allocation

- **Total Tasks**: 102 tasks (90 original + 12 tool integration fixes)
- **MVP (US1 only)**: 60 tasks (Setup + Foundational + US1 + Tool Integration)
- **Full Feature Set**: 102 tasks
- **Estimated Timeline**: 
  - **Original Estimate**: 6-8 weeks (single developer) or 3-4 weeks (3 developers)
  - **Revised with Tool Integration**: 8-11 weeks (single developer) or 5-7 weeks (3 developers)
  - **Additional Time for Tool Integration**: +2-3 weeks
  - Full System: 14-18 weeks (single developer) or 8-10 weeks (3 developers)

**Current Progress**:
- ✅ Setup: 8/8 tasks (100%)
- ✅ Foundational: 18/18 tasks (100%)
- ⚠️ User Story 1: 24/36 tasks (67% - missing tool integration)
- ❌ User Story 2: 0/17 tasks (0%)
- ❌ User Story 3: 0/15 tasks (0%)
- ❌ Polish: 0/10 tasks (0%)

**Immediate Priority**: Complete T023a-T027d (12 tasks) to unblock US1 production readiness

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- ⚠️ Symbol indicates incomplete or incorrectly implemented tasks requiring rework
- Each user story delivers independent value and can be tested/deployed separately
- Foundational phase is critical - no user story work can proceed without it
- Models and static analysis tools can be developed in parallel within each story
- Dashboard components can be developed in parallel with backend APIs
- Focus on MVP (User Story 1) first for fastest value delivery
- Use Spring Modulith reference codebase for validation throughout development