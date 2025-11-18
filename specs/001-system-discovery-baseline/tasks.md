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

- [ ] T023 [P] [US1] Implement Context Mapper integration in tools/src/analysis/static/context_mapper.py
- [ ] T024 [P] [US1] Implement Structurizr integration for C4 diagrams in tools/src/analysis/static/structurizr.py
- [ ] T025 [P] [US1] Implement CodeQL integration for security scanning in tools/src/analysis/static/codeql.py
- [ ] T026 [P] [US1] Implement Microsoft AppCAT integration in tools/src/analysis/static/appcat.py
- [ ] T027 [US1] Create static analysis orchestration service using Microsoft Agent Framework in tools/src/services/orchestration/static_analyzer.py

### Runtime Analysis Integration for User Story 1

- [ ] T028 [P] [US1] Implement SigNoz deployment automation in tools/src/analysis/runtime/signoz_deployer.py
- [ ] T029 [P] [US1] Implement OpenTelemetry instrumentation templates in tools/src/analysis/runtime/otel_instrumentation.py
- [ ] T030 [P] [US1] Create synthetic load testing framework in tools/src/analysis/runtime/load_generator.py
- [ ] T031 [US1] Create runtime analysis orchestration service using Microsoft Agent Framework in tools/src/services/orchestration/runtime_analyzer.py

### Gap Analysis Engine for User Story 1

- [ ] T032 [US1] Implement gap analysis comparison engine in tools/src/analysis/gap/gap_analyzer.py
- [ ] T033 [US1] Create coupling metrics calculation in tools/src/analysis/gap/coupling_metrics.py
- [ ] T034 [US1] Implement architectural drift detection in tools/src/analysis/gap/drift_detector.py

### API Endpoints for User Story 1

- [x] T035 [US1] Implement project management endpoints in tools/src/omega_analysis/api/v1/projects.py (AnalysisProject CRUD API)
- [ ] T036 [US1] Implement analysis operations endpoints in tools/src/api/analysis/analysis.py
- [ ] T037 [US1] Implement architecture retrieval endpoints in tools/src/api/analysis/architecture.py
- [ ] T038 [US1] Implement dependency graph endpoints in tools/src/api/analysis/dependencies.py
- [ ] T039 [US1] Implement performance baselines endpoints in tools/src/api/analysis/baselines.py

### Analysis Orchestration for User Story 1

- [ ] T040 [US1] Create main analysis workflow orchestrator in tools/src/services/orchestration/analysis_orchestrator.py
- [ ] T041 [US1] Implement analysis progress tracking in tools/src/services/orchestration/progress_tracker.py
- [ ] T042 [US1] Create analysis result aggregation service in tools/src/services/orchestration/result_aggregator.py

### Dashboard Components for User Story 1

- [ ] T043 [P] [US1] Create project list component in dashboard/src/components/analysis/project-list.component.ts
- [ ] T044 [P] [US1] Create analysis progress component in dashboard/src/components/analysis/analysis-progress.component.ts
- [ ] T045 [P] [US1] Create architecture visualization component in dashboard/src/components/analysis/architecture-viewer.component.ts
- [ ] T046 [P] [US1] Create dependency graph visualization in dashboard/src/components/analysis/dependency-graph.component.ts
- [ ] T047 [P] [US1] Create performance metrics dashboard in dashboard/src/components/analysis/performance-dashboard.component.ts
- [ ] T048 [US1] Create main analysis dashboard page in dashboard/src/pages/dashboard/analysis-dashboard.page.ts

**Checkpoint**: At this point, User Story 1 should be fully functional with complete automated analysis capabilities

---

## Phase 4: User Story 2 - Migration Readiness Assessment (Priority: P2)

**Goal**: Engineering managers can understand migration complexity, effort estimates, and risk factors for informed go/no-go decisions with quantified risk scoring

**Independent Test**: Analyze systems with known migration outcomes and validate readiness scores correlate with actual migration success rates

### Risk Assessment Models for User Story 2

- [ ] T049 [P] [US2] Create RiskAssessment model in tools/src/models/risk.py
- [ ] T050 [P] [US2] Create ServiceBoundary model in tools/src/models/boundary.py
- [ ] T051 [P] [US2] Create supporting risk factor models in tools/src/models/risk_factors.py

### Risk Assessment Engine for User Story 2

- [ ] T052 [US2] Implement quantitative risk scoring framework in tools/src/services/assessment/risk_scorer.py
- [ ] T053 [US2] Create migration complexity analyzer in tools/src/services/assessment/complexity_analyzer.py
- [ ] T054 [US2] Implement service boundary recommendation engine in tools/src/services/assessment/boundary_recommender.py
- [ ] T055 [US2] Create effort estimation algorithms in tools/src/services/assessment/effort_estimator.py

### Assessment API Endpoints for User Story 2

- [ ] T056 [US2] Implement risk assessment endpoints in tools/src/api/analysis/assessments.py
- [ ] T057 [US2] Implement service boundary endpoints in tools/src/api/analysis/boundaries.py
- [ ] T058 [US2] Create boundary approval workflow endpoints in tools/src/api/validation/boundary_approval.py

### Human-in-the-Loop Validation for User Story 2

- [ ] T059 [US2] Implement architect approval workflow in tools/src/services/validation/approval_workflow.py
- [ ] T060 [US2] Create validation result tracking in tools/src/services/validation/validation_tracker.py
- [ ] T061 [US2] Implement notification system for approval requests in tools/src/services/validation/notification_service.py

### Dashboard Components for User Story 2

- [ ] T062 [P] [US2] Create risk assessment dashboard in dashboard/src/components/assessment/risk-dashboard.component.ts
- [ ] T063 [P] [US2] Create service boundary visualization in dashboard/src/components/assessment/boundary-viewer.component.ts
- [ ] T064 [P] [US2] Create approval workflow interface in dashboard/src/components/validation/approval-interface.component.ts
- [ ] T065 [US2] Create migration readiness report page in dashboard/src/pages/reports/readiness-report.page.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with complete risk assessment capabilities

---

## Phase 5: User Story 3 - Compliance and Security Baseline Documentation (Priority: P3)

**Goal**: Compliance officers and security engineers get comprehensive documentation of system state including data flows, security controls, and regulatory compliance for audit purposes

**Independent Test**: Validate generated compliance documentation passes enterprise security review and meets audit requirements

### Compliance Models for User Story 3

- [ ] T066 [P] [US3] Create ComplianceRecord model in tools/src/models/compliance.py
- [ ] T067 [P] [US3] Create supporting compliance requirement models in tools/src/models/compliance_requirements.py

### Compliance Analysis Engine for User Story 3

- [ ] T068 [US3] Implement regulatory framework analyzer in tools/src/services/compliance/regulatory_analyzer.py
- [ ] T069 [US3] Create data classification engine in tools/src/services/compliance/data_classifier.py
- [ ] T070 [US3] Implement security control assessment in tools/src/services/compliance/security_assessor.py
- [ ] T071 [US3] Create audit trail generator in tools/src/services/compliance/audit_trail_generator.py

### Compliance API Endpoints for User Story 3

- [ ] T072 [US3] Implement compliance records endpoints in tools/src/api/analysis/compliance.py
- [ ] T073 [US3] Create compliance report generation endpoints in tools/src/api/reports/compliance_reports.py

### Report Generation System for User Story 3

- [ ] T074 [US3] Implement comprehensive report generator in tools/src/services/reporting/report_generator.py
- [ ] T075 [US3] Create PDF report templates in tools/src/services/reporting/templates/
- [ ] T076 [US3] Implement Excel export functionality in tools/src/services/reporting/excel_exporter.py

### Dashboard Components for User Story 3

- [ ] T077 [P] [US3] Create compliance dashboard in dashboard/src/components/compliance/compliance-dashboard.component.ts
- [ ] T078 [P] [US3] Create audit trail viewer in dashboard/src/components/compliance/audit-trail.component.ts
- [ ] T079 [P] [US3] Create report generation interface in dashboard/src/components/reports/report-generator.component.ts
- [ ] T080 [US3] Create compliance report page in dashboard/src/pages/reports/compliance-report.page.ts

**Checkpoint**: All user stories should now be independently functional with complete compliance documentation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T081 [P] Create comprehensive API documentation in docs/api/
- [ ] T082 [P] Implement health check endpoints in tools/src/api/health/health.py
- [ ] T083 [P] Add system metrics and monitoring in tools/src/api/health/metrics.py
- [ ] T084 [P] Implement GraphQL query interface in tools/src/api/graphql/
- [ ] T085 [P] Create CLI tool for analysis operations in tools/src/cli/analyze.py
- [ ] T086 [P] Implement validation CLI in tools/src/cli/validate.py
- [ ] T087 Code cleanup and refactoring across all modules
- [ ] T088 Performance optimization for large codebase analysis
- [ ] T089 Security hardening and penetration testing
- [ ] T090 Run quickstart.md validation with Spring Modulith reference

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 models but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses analysis results from US1/US2 but independently testable

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

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (8 tasks)
2. Complete Phase 2: Foundational (10 tasks) - CRITICAL foundation
3. Complete Phase 3: User Story 1 (30 tasks) - Complete automated analysis system
4. **STOP and VALIDATE**: Test User Story 1 independently with Spring Modulith
5. Deploy/demo automated analysis capabilities

### Incremental Delivery

1. Complete Setup + Foundational → Analysis platform foundation ready
2. Add User Story 1 → Test with reference codebases → Deploy/Demo (MVP with automated analysis!)
3. Add User Story 2 → Test risk assessment → Deploy/Demo (Added migration readiness)
4. Add User Story 3 → Test compliance → Deploy/Demo (Complete enterprise solution)
5. Each story adds significant value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational phases together (18 tasks)
2. Once Foundational is done:
   - **Senior Developer**: User Story 1 (30 tasks) - Core analysis engine
   - **Mid-level Developer**: User Story 2 (17 tasks) - Risk assessment
   - **Junior/Mid Developer**: User Story 3 (15 tasks) - Compliance documentation
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (10 tasks)

### Resource Allocation

- **Total Tasks**: 90 tasks
- **MVP (US1 only)**: 48 tasks (Setup + Foundational + US1)
- **Full Feature Set**: 90 tasks
- **Estimated Timeline**: 
  - MVP: 6-8 weeks (single developer) or 3-4 weeks (3 developers)
  - Full System: 12-15 weeks (single developer) or 6-8 weeks (3 developers)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story delivers independent value and can be tested/deployed separately
- Foundational phase is critical - no user story work can proceed without it
- Models and static analysis tools can be developed in parallel within each story
- Dashboard components can be developed in parallel with backend APIs
- Focus on MVP (User Story 1) first for fastest value delivery
- Use Spring Modulith reference codebase for validation throughout development