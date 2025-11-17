# Phase 1: Discover & Baseline - Legacy System Analysis Framework

**Document**: Phase 1 Discovery & Baseline Analysis  
**Version**: 1.0 Draft  
**Date**: November 17, 2025  
**Purpose**: Comprehensive legacy system analysis methodology for migration preparation  
**Context**: Based on Migration Epics Framework - Epic 1.1: System Discovery and Baseline Assessment

---

## Overview

Phase 1 represents the critical foundation of any monolith-to-microservices migration. This phase establishes the comprehensive understanding of the existing system through a dual-pronged analysis approach: Static Analysis (The Blueprint) and Runtime Analysis (The Reality). Success in this phase determines the accuracy and safety of all subsequent migration activities.

**Core Principle**: You cannot safely migrate what you do not fully understand. Legacy systems contain hidden dependencies, undocumented integrations, and implicit business rules that only emerge through systematic analysis.

---

## The Two-Pronged Analysis Strategy

### Static Analysis (The Blueprint)
**Purpose**: Reverse-engineer the intended architecture and discover Domain-Driven Design (DDD) boundaries

Static analysis reveals the system's designed structure by examining source code, configuration files, and documentation. This approach uncovers:
- Intended architectural patterns and design decisions
- Domain boundaries and business logic organization  
- Class relationships and dependency structures
- Configuration-driven integrations and data flows

### Runtime Analysis (The Reality)
**Purpose**: Map actual system behavior, traffic patterns, and runtime dependencies

Runtime analysis observes the living system in its operational environment, revealing:
- Actual traffic flows and communication patterns
- Hidden dependencies not visible in source code
- Performance characteristics and bottlenecks
- External system integrations and data exchanges

**Critical Insight**: The gap between static analysis (intended design) and runtime analysis (actual behavior) represents migration risk. Large gaps indicate technical debt, undocumented changes, or architectural drift.

---

## Phase 1 Analysis Toolkit

### Static Analysis Tools

| Tool | Type | OSS | Primary Function | CLI/Automation Method | Output Format |
|------|------|-----|------------------|----------------------|---------------|
| Context Mapper | DDD/Modeling | ✅ | Reverse-engineering DDD patterns. Finds Bounded Contexts & Aggregates. | context-map-discovery (Java Library). Invoked via CLI/Gradle to scan source. | .cml (DSL file) → Generates PlantUML C4 diagrams |
| Structurizr | C4 Diagramming | ✅ | Component Discovery. Maps classes to C4 Components based on rules. | Component Finder (Java/.NET Library). Run as custom CLI script to scan bytecode/assemblies. | .dsl (Workspace) → Generates JSON/PNG/SVG |
| CodeQL | Static Analysis | ✅ | Deep Code Querying. Finding specific logic patterns, security flaws, or rule violations. | codeql-cli. Runs queries against compiled database of code. | CSV, SARIF, or raw query results (No diagrams) |
| C4InterFlow | Architecture as Code | ✅ | .NET Specific Analysis. Deep static analysis of C# to generate C4. | c4interflow CLI. Scans solution files directly. | PlantUML, YAML, JSON models |
| **Microsoft AppCAT** | **Migration Assessment** | ✅ | **Enterprise Java migration assessment. Comprehensive cloud readiness analysis with Azure-specific recommendations.** | **appcat CLI. Cross-platform binary with multiple assessment scripts and rulesets.** | **HTML reports, JSON assessment data, migration recommendations** |
| **GitHub Copilot App Modernization** | **AI-Assisted Migration** | ❌ | **AI-powered Java project assessment and migration assistance with automated code remediation.** | **VS Code/IntelliJ extension with agent-based workflow automation.** | **Interactive reports, automated code changes, validation iterations** |

**When to Use Static Analysis**:
- Rescuing "Lost" Knowledge: When original team is gone and business rules must be discovered
- Defining Boundaries: When deciding where to cut the monolith for microservices (Bounded Contexts)
- Generating Documentation: Creating long-lived, version-controlled architecture diagrams (C4) that update with code
- **Enterprise Migration Assessment**: When comprehensive cloud readiness analysis is required (AppCAT)
- **AI-Assisted Modernization**: When automated code remediation and migration guidance is needed (GitHub Copilot App Modernization)

### Runtime Analysis Tools

| Tool | Type | OSS | Primary Function | Discovery Method | Key Feature for Monoliths |
|------|------|-----|------------------|------------------|---------------------------|
| SigNoz | APM/Observability | ✅ | Full-Stack Monitoring. One-stop shop for traces, metrics, and logs. | OpenTelemetry Agents. Auto-instrumentation of running app. | Service Map. Visualizes all external calls (DB, API, Queue) automatically |
| SkyWalking | APM | ✅ | Topology Mapping. Specialized in visualizing distributed systems. | Native Agents. Installs on server/container. | Topology Graph. Shows dependencies without code changes |
| Jaeger | Distributed Tracing | ✅ | Request Flow Tracing. Deep dive into specific request paths. | OpenTelemetry. Traces requests across boundaries. | DAG (Directed Acyclic Graph). Shows flow of requests |

**When to Use Runtime Analysis**:
- Migration De-risking: "If I move this server, what breaks?" (Finds hidden hardcoded IP calls)
- Virtualizing the Monolith: Using Custom Instrumentation (Grey Box) to define internal methods as "virtual services" to see coupling before refactoring
- Performance Baselines: Recording latency/throughput of legacy system before migration for comparison

---

## Recommended Workflow: The "Holy Grail" Approach

### Phase 1.1: Turn on the Lights (Runtime Analysis)

**Timeline**: 1-2 weeks  
**Objective**: Establish comprehensive runtime visibility into system behavior

**Step 1: Deploy Observability Infrastructure**
- Install SigNoz (or equivalent APM solution) on legacy system
- Configure OpenTelemetry agents with minimal performance impact
- Establish baseline monitoring for all system components

**Step 2: Runtime Data Collection**
- **Wait 24-48 Hours**: Allow collection of representative traffic patterns
- Capture peak, off-peak, and batch processing periods
- Document seasonal or periodic traffic variations

**Step 3: Service Map Generation**
- Generate comprehensive Service Map showing all external dependencies
- Identify every database, external API, message queue, and file system interaction
- Document network topology and communication protocols
- This becomes your "System Context" (C4 Level 1)

**Step 4: Grey Box Analysis (Internal Visibility)**
- Identify 3-4 key internal modules (e.g., "Checkout", "Inventory", "User Management")
- Add manual OpenTelemetry spans to critical method entry points
- Observe "virtual" traffic between internal modules in Service Map
- Quantify coupling between internal components

**Deliverables**:
- Runtime dependency map with external systems
- Internal module communication patterns
- Performance baseline metrics (latency, throughput, error rates)
- Traffic pattern analysis and capacity utilization

### Phase 1.2: Draw the Map (Static Analysis)

**Timeline**: 1-2 weeks  
**Objective**: Reverse-engineer intended system architecture and domain boundaries

**Step 1: Domain-Driven Design Discovery**
- Run Context Mapper against source code using context-map-discovery CLI
- Identify potential Bounded Contexts and Aggregates
- Map business capabilities to code modules

**Step 2: Component Architecture Generation**
- Execute Structurizr Component Finder against codebase
- Generate initial C4 Component diagrams
- Document class-to-component mappings

**Step 3: Deep Code Analysis**
- Use CodeQL for specific pattern discovery:
  - Security vulnerabilities and compliance violations
  - Architectural anti-patterns and technical debt
  - Business rule extraction and documentation
- **Execute Microsoft AppCAT assessment**:
  - Run comprehensive cloud readiness analysis using appcat CLI
  - Generate Azure-specific migration recommendations and effort estimates
  - Identify Java/Spring Boot specific migration challenges and solutions
- **Deploy GitHub Copilot App Modernization** (if available):
  - Use AI-powered assessment for automated issue identification
  - Generate migration plans with automated code remediation suggestions
  - Execute validation iterations with CVE detection and build verification

**Step 4: Architecture Documentation Generation**
- Generate PlantUML diagrams from analysis tools
- Create C4 model hierarchy (Context → Container → Component)
- Document Architectural Decision Records (ADRs) for discovered patterns

**Deliverables**:
- C4 architecture diagrams (Context, Container, Component levels)
- Domain model with Bounded Context identification
- Technical debt inventory and security assessment
- Architectural Decision Records documenting current state
- **Microsoft AppCAT assessment report** with cloud readiness categorization
- **Azure migration recommendations** with effort estimates and solution mappings
- **GitHub Copilot modernization plans** with automated remediation strategies (if applicable)

### Phase 1.3: Cross-Reference and Validation

**Timeline**: 1 week  
**Objective**: Reconcile static analysis (intended design) with runtime analysis (actual behavior)

**Step 1: Gap Analysis**
- Compare Static Map (what code says should happen) with Runtime Map (what actually happens)
- Identify discrepancies between intended and actual architecture
- Document architectural drift and undocumented changes

**Step 2: Risk Assessment**
- **Example Discrepancy**: Static analysis shows "Inventory" is isolated. Runtime analysis shows "Checkout" calls "Inventory" 50 times per request.
- **Conclusion**: Do not extract "Inventory" yet; it is too coupled. Refactor first.
- Quantify coupling strength and migration complexity

**Step 3: Migration Readiness Scoring**
- Score each potential service boundary for extraction readiness
- Identify high-risk dependencies requiring pre-migration refactoring
- Prioritize refactoring activities to reduce coupling

**Deliverables**:
- Gap analysis report comparing static vs runtime findings
- Migration risk assessment with quantified coupling metrics
- Service extraction roadmap with dependency priorities
- Go/no-go decision framework for migration progression

---

## Epic 1.1 Integration: System Discovery and Baseline Assessment

This analysis framework directly supports Epic 1.1 deliverables:

### Functional Requirements Mapping
- **FR1.1 (Automated code analysis)**: Achieved through Static Analysis toolkit producing dependency graphs
- **FR1.2 (Performance baseline collection)**: Delivered through Runtime Analysis phase capturing latency, throughput, and error rates
- **FR1.3 (Compliance inventory)**: Supported by CodeQL security and compliance pattern detection
- **FR1.4 (Risk assessment framework)**: Enabled by Cross-Reference phase gap analysis and coupling quantification

### Non-Functional Requirements Alignment
- **NFR1.1 (Analysis completion within 2 hours for 1M+ LOC)**: Static analysis tools designed for large codebase processing
- **NFR1.2 (Baseline metrics without production impact)**: Runtime analysis using lightweight OpenTelemetry instrumentation
- **NFR1.3 (Comprehensive audit trail)**: All analysis tools generate versioned artifacts and reports

### Acceptance Criteria Support
- **System architecture documentation**: Delivered through C4 model generation and ADR creation
- **Performance baselines with statistical confidence**: Achieved through 24-48 hour runtime data collection
- **Compliance requirements identification**: Supported by CodeQL compliance scanning
- **Migration readiness scoring**: Enabled by quantified gap analysis and coupling metrics

---

## Success Metrics and KPIs

### Discovery Quality Metrics
- **Static Analysis Coverage**: Percentage of codebase analyzed (target: 95%+)
- **Runtime Visibility**: Percentage of transactions traced (target: 90%+)
- **External Dependency Discovery**: Count of external systems identified
- **Internal Coupling Quantification**: Coupling strength metrics between modules

### Baseline Accuracy Metrics
- **Performance Baseline Confidence**: Statistical significance of collected metrics
- **Gap Analysis Accuracy**: Validation rate of discrepancy findings
- **Risk Prediction Quality**: Accuracy of migration complexity estimates

### Timeline and Efficiency Metrics
- **Analysis Completion Time**: Total time from start to final deliverables
- **Tool Automation Rate**: Percentage of analysis performed automatically
- **Manual Validation Effort**: Time spent on manual verification activities

---

## Common Pitfalls and Mitigation Strategies

### Pitfall 1: Analysis Paralysis
**Risk**: Spending excessive time on analysis without progressing to action
**Mitigation**: Time-box analysis phases and establish "good enough" thresholds for progression

### Pitfall 2: Runtime Analysis Performance Impact
**Risk**: Monitoring overhead affecting production system performance
**Mitigation**: Use sampling strategies and lightweight instrumentation; monitor overhead metrics

### Pitfall 3: Static Analysis Overwhelm
**Risk**: Generating too much information without actionable insights
**Mitigation**: Focus on migration-relevant patterns; prioritize business-critical components

### Pitfall 4: Ignoring Gap Analysis
**Risk**: Proceeding with migration based on static analysis alone
**Mitigation**: Mandate runtime validation of all static analysis findings before architectural decisions

---

## Next Steps and Phase Transition

### Phase 1 Completion Criteria
- [ ] Runtime analysis deployed and collecting data for minimum 48 hours
- [ ] Static analysis completed across entire codebase
- [ ] Gap analysis identifies and quantifies all major discrepancies
- [ ] Migration readiness assessment completed with go/no-go recommendation
- [ ] All deliverables reviewed and approved by architecture board

### Transition to Phase 2: Decompose & Design Guardrails
- **Input Dependencies**: Phase 1 analysis artifacts, risk assessment, and migration readiness score
- **Handoff Process**: Architecture findings and constraints inform service boundary design
- **Continuity Requirements**: Runtime monitoring continues through all subsequent phases

---

## Microsoft Enterprise Integration

### Microsoft AppCAT (Application and Code Assessment Tool)

**Overview**: Microsoft AppCAT is an enterprise-grade, open-source command-line tool designed specifically for Java application migration assessment to Azure. It provides comprehensive analysis with Azure-specific recommendations and migration effort estimates.

**Key Capabilities**:
- **Multi-Platform Support**: Cross-platform CLI (Windows, Linux, macOS) with Intel, ARM, and Apple Silicon support
- **Comprehensive Rulesets**: Pre-built rules for Azure App Service, OpenJDK migrations, and custom transformation scenarios
- **Assessment Categories**: Categorized cloud readiness issues with impact severity and remediation guidance
- **Migration Solutions**: Specific recommendations for Azure SQL Database, App Service, Container Apps, and other Azure services
- **Effort Estimation**: Quantified migration complexity scores and timeline projections

**Integration with Phase 1 Workflow**:
- **Phase 1.2 (Static Analysis)**: Execute AppCAT assessment alongside Context Mapper and Structurizr analysis
- **Azure-Specific Insights**: Generate cloud readiness reports with categorized migration issues
- **Enterprise Reporting**: HTML reports suitable for stakeholder communication and architectural reviews
- **Custom Rules**: Extend analysis with organization-specific migration patterns and constraints

**Sample Assessment Output**:
```
Assessment Categories:
├── Database Migration (Microsoft SQL) - HIGH IMPACT
│   └── Solution: Migrate to Azure SQL Database (Spring)
├── Configuration Externalization - MEDIUM IMPACT  
│   └── Solution: Azure App Configuration integration
├── Authentication Modernization - MEDIUM IMPACT
│   └── Solution: Azure Active Directory integration
└── Container Readiness - LOW IMPACT
    └── Solution: Azure Container Apps deployment
```

### GitHub Copilot App Modernization

**Overview**: GitHub Copilot App Modernization is an AI-powered Visual Studio Code and IntelliJ IDEA extension that provides intelligent assessment and automated migration assistance for Java applications.

**Key Capabilities**:
- **AI-Powered Assessment**: Automated identification of migration issues with intelligent solution recommendations
- **Automated Code Remediation**: AI-generated code changes with validation and testing iterations
- **Migration Workflow Orchestration**: Step-by-step guided migration process with automated validation
- **Quality Assurance Integration**: Built-in CVE detection, build verification, and unit test generation
- **Enterprise Integration**: Seamless integration with GitHub Enterprise and organizational development workflows

**Agent-Based Workflow**:
1. **Assessment Agent**: Analyzes codebase and generates categorized migration recommendations
2. **Migration Agent**: Orchestrates code changes with automated branching and validation
3. **Validation Agent**: Executes comprehensive validation including:
   - **Validate-CVEs Tool**: Detects and fixes Common Vulnerabilities and Exposures
   - **Build-Project Tool**: Resolves compilation errors and dependency conflicts
   - **Consistency-Validation Tool**: Analyzes functional consistency across changes
   - **Run-Test Tool**: Executes and fixes unit test failures iteratively
   - **Completeness-Validation Tool**: Ensures comprehensive migration coverage

**Integration Requirements**:
- **Enterprise License**: GitHub Copilot Business or Enterprise plan required
- **IDE Support**: Visual Studio Code 1.101+ or IntelliJ IDEA 2023.3+
- **Java Requirements**: Java 21+ with Maven or Gradle wrapper support
- **Version Control**: Git repository with appropriate branch permissions

**Omega System Integration**:
- **Automated Analysis Trigger**: Integration with Omega's discovery phase automation
- **Report Generation**: Structured output compatible with Omega's checkpoint system
- **Human-in-the-Loop**: Validation gates compatible with enterprise architecture review processes
- **Continuous Integration**: Pipeline integration for ongoing analysis and validation

---

## Tool Integration and Automation

### Recommended Tool Stack Integration
1. **Primary APM**: SigNoz for comprehensive runtime analysis
2. **Primary Static Analysis**: Context Mapper for DDD boundary discovery
3. **Secondary Static Analysis**: Structurizr for C4 component mapping
4. **Security/Compliance**: CodeQL for pattern detection and vulnerability assessment
5. **Enterprise Migration Assessment**: Microsoft AppCAT for comprehensive cloud readiness analysis
6. **AI-Assisted Modernization**: GitHub Copilot App Modernization for automated migration assistance (enterprise license required)

### Automation Opportunities
- Automated nightly static analysis runs with delta reporting
- Continuous runtime dependency discovery and alerting
- Automated gap analysis reporting comparing static vs runtime findings
- Integration with CI/CD pipeline for ongoing analysis validation

---

*This framework provides the systematic foundation for safe and successful monolith-to-microservices migration by ensuring comprehensive understanding of both intended design and actual system behavior before making architectural changes.*

---

## Appendix: Tool-Specific Implementation Guides

### Context Mapper Implementation
```bash
# Example CLI usage for Java Spring Boot monolith
context-map-discovery \
  --source-path /path/to/monolith/src \
  --output-format cml \
  --generate-diagrams \
  --bounded-context-detection aggressive
```

### SigNoz Deployment
```yaml
# Docker Compose example for SigNoz deployment
version: '3.8'
services:
  signoz:
    image: signoz/signoz:latest
    ports:
      - "3301:3301"
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=service.name=legacy-monolith
```

### Structurizr Component Discovery
```java
// Example Java code for component discovery
ComponentFinder componentFinder = new ComponentFinder(
    container,
    "com.company.monolith",
    new SpringComponentFinderStrategy()
);
componentFinder.findComponents();
```

### Microsoft AppCAT Assessment
```bash
# Download and extract AppCAT CLI for your platform
# Update PATH to include appcat binary location

# Clone target Java application
git clone https://github.com/your-org/spring-boot-monolith.git

# Run comprehensive assessment
./appcat assess /path/to/spring-boot-monolith \
  --output-dir ./assessment-reports \
  --ruleset azure-app-service \
  --include-packages com.yourcompany \
  --generate-static-report

# Run specific Azure migration assessments
./samples/run-assessment /path/to/spring-boot-monolith
./samples/run-assessment-openjdk21 /path/to/spring-boot-monolith
```

### GitHub Copilot App Modernization
```bash
# Prerequisites: VS Code with GitHub Copilot and App Modernization extensions
# Open Spring Boot project in VS Code

# Access GitHub Copilot App Modernization panel
# 1. Select "Run Assessment" in ASSESSMENT section
# 2. Review generated Assessment Report
# 3. Select migration solutions and "Run Task"
# 4. Follow agent-guided workflow with validation iterations:
#    - Validate-CVEs tool for dependency security
#    - Build-Project tool for compilation verification
#    - Consistency-Validation tool for functional analysis
#    - Run-Test tool for unit test execution and fixes
#    - Completeness-Validation tool for migration completeness
```

*These implementation guides provide concrete starting points for tool deployment and configuration specific to legacy system analysis requirements, including Microsoft's enterprise-grade Java assessment and migration tools.*