# Research: System Discovery and Baseline Assessment

**Feature**: Epic 1.1 - System Discovery and Baseline Assessment  
**Date**: November 17, 2025  
**Phase**: Phase 0 - Outline & Research

## Technology Research Findings

### Static Analysis Tools Integration

**Decision**: Multi-tool static analysis approach using Context Mapper, Structurizr, CodeQL, and Microsoft AppCAT  
**Rationale**: 
- Context Mapper provides domain-driven design boundary identification through reverse engineering
- Structurizr enables C4 architecture diagram generation with component discovery
- CodeQL offers deep code querying for security patterns and compliance violations
- Microsoft AppCAT provides enterprise-grade Azure migration assessment capabilities

**Alternatives Considered**:
- Single-tool approach (e.g., only SonarQube): Rejected due to limited architectural analysis capabilities
- Commercial-only solutions (e.g., CAST): Rejected due to cost and vendor lock-in concerns
- Custom static analysis: Rejected due to development timeline and accuracy concerns

### Runtime Analysis Platform

**Decision**: SigNoz as primary APM with OpenTelemetry instrumentation  
**Rationale**:
- Open-source solution with comprehensive observability features (traces, metrics, logs)
- Native OpenTelemetry support for standardized instrumentation
- Service map generation capabilities for dependency visualization
- Lightweight deployment with <1% performance overhead requirement

**Alternatives Considered**:
- Jaeger + Prometheus + ELK: Rejected due to integration complexity and maintenance overhead
- Commercial APM (e.g., New Relic, Datadog): Rejected due to enterprise cost and data privacy concerns
- SkyWalking: Considered as secondary option, maintained as backup integration

### Programming Language and Framework

**Decision**: Python 3.12+ with FastAPI for backend services  
**Rationale**:
- Constitution requirement for Python 3.12+ compliance
- FastAPI provides high-performance async API capabilities with automatic OpenAPI generation
- Rich ecosystem for analysis tools integration (JavaParser, Docker SDK, etc.)
- Strong containerization and Kubernetes deployment support

**Alternatives Considered**:
- Java Spring Boot: Rejected despite monolith analysis focus due to constitution requirements
- Node.js with Express: Rejected due to less mature analysis tools ecosystem
- Go: Rejected due to limited analysis tools integration capabilities

### Storage Architecture

**Decision**: PostgreSQL 15+ with pg_vector extension for analysis artifacts  
**Rationale**:
- Robust relational database with ACID compliance for analysis metadata
- pg_vector extension enables vector similarity search for architectural pattern matching
- Proven enterprise scalability and backup/recovery capabilities
- Strong integration with Python ecosystem via SQLAlchemy

**Alternatives Considered**:
- MongoDB: Rejected due to lack of ACID compliance for critical analysis data
- ClickHouse: Considered for analytics workloads but rejected as primary storage due to complexity
- Pure file-based storage: Rejected due to concurrent access and querying limitations

### Container Orchestration Strategy

**Decision**: Docker containerization with Kubernetes deployment readiness  
**Rationale**:
- Consistent deployment environments across development and production
- Tool isolation for static analysis dependencies (Java, .NET, etc.)
- Scalable architecture supporting concurrent analysis workloads
- Enterprise integration requirements for hybrid cloud deployments

**Alternatives Considered**:
- Virtual machines: Rejected due to resource overhead and deployment complexity
- Serverless functions: Rejected due to long-running analysis requirements and tool state management
- Native deployment: Rejected due to dependency management complexity across environments

## Integration Patterns Research

### Tool Chain Orchestration

**Decision**: Microsoft Agent Framework for agentic workflow orchestration  
**Rationale**:
- Azure-native agentic orchestration with built-in Azure OpenAI integration
- Multi-agent coordination patterns for complex analysis workflows
- Native integration with Azure Container Apps for scalable deployment
- Enterprise-grade security and monitoring through Azure Monitor
- Structured agent communication and state management

**Alternatives Considered**:
- Apache Airflow: Rejected due to lack of native agentic capabilities and Azure integration complexity
- LangChain/LangGraph: Rejected due to vendor-neutral approach, prefer Azure-native solutions
- Custom orchestration: Rejected due to development timeline and lack of proven agentic patterns

### Human-in-the-Loop Integration

**Decision**: Web-based validation interfaces with role-based workflows  
**Rationale**:
- Enterprise architect approval workflows for boundary recommendations
- Manual validation interfaces for accuracy assessment
- Audit trail generation for compliance requirements
- Integration with enterprise identity providers (OIDC/SAML)

**Alternatives Considered**:
- CLI-only validation: Rejected due to user experience and enterprise adoption concerns
- Email-based workflows: Rejected due to lack of audit trails and process enforcement
- Slack/Teams integration: Considered as supplementary notification channel

### API Design Patterns

**Decision**: REST API with OpenAPI specification and GraphQL for complex queries  
**Rationale**:
- REST for standard CRUD operations and analysis triggering
- GraphQL for complex report queries and relationship traversal
- OpenAPI automatic generation for client SDK development
- Standard HTTP patterns for enterprise integration

**Alternatives Considered**:
- GraphQL-only: Rejected due to enterprise tooling compatibility concerns
- gRPC: Rejected due to limited web client support and debugging complexity
- WebSocket streaming: Considered for real-time analysis progress updates

## Performance and Scalability Research

### Analysis Performance Optimization

**Decision**: Parallel analysis execution with resource-aware scheduling  
**Rationale**:
- CPU-intensive static analysis tools benefit from parallel execution
- Memory-aware scheduling prevents resource contention
- Tool-specific optimization (e.g., CodeQL database caching)
- Incremental analysis capabilities for large codebases

**Implementation Approach**:
- Container resource limits per analysis tool
- Shared cache volumes for tool artifacts (Maven repositories, etc.)
- Distributed analysis for extremely large codebases (>1M LOC)
- Progress tracking and partial result persistence

### Data Management Strategy

**Decision**: Tiered storage with analysis artifact lifecycle management  
**Rationale**:
- Hot storage (PostgreSQL) for active analysis metadata and recent results
- Warm storage (MinIO) for analysis artifacts and generated reports
- Cold storage integration for long-term audit and compliance requirements
- Automated cleanup policies for ephemeral analysis data
- Container-native deployment within Docker Compose environment

**Implementation Approach**:
- Analysis project lifecycle states (active, completed, archived)
- Configurable retention policies per analysis type
- Export capabilities for external systems integration
- Backup and disaster recovery for critical analysis results

## Security and Compliance Research

### Enterprise Security Integration

**Decision**: OAuth 2.0/OIDC with role-based access control (RBAC)  
**Rationale**:
- Standard enterprise identity provider integration
- Fine-grained permissions for analysis access and validation workflows
- Audit logging for all system interactions and decisions
- SOC2 compliance for enterprise security requirements

**Implementation Approach**:
- Integration with enterprise identity providers (Azure AD, Okta, etc.)
- Role definitions: Analyst, Architect, Manager, Auditor
- Permission matrix for analysis operations and data access
- Comprehensive audit logging with tamper-evident storage

### Data Privacy and Protection

**Decision**: Encryption at rest and in transit with secure key management  
**Rationale**:
- Analysis may involve sensitive business logic and architectural patterns
- Compliance with enterprise data protection policies
- Secure transmission of analysis results and reports
- Key rotation and management capabilities

**Implementation Approach**:
- TLS 1.3 for all API communications
- Database encryption with customer-managed keys
- Analysis artifact encryption in object storage
- Integration with enterprise key management systems (HSM/KMS)

## Testing Strategy Research

### Migration Test Framework

**Decision**: Custom migration testing framework with known outcome validation  
**Rationale**:
- Validate analysis accuracy against manually reviewed reference systems
- Regression testing for analysis algorithm improvements
- Performance benchmarking for analysis completion times
- Integration testing for multi-tool coordination

**Implementation Approach**:
- Reference codebase collection (Spring Modulith, Pet Clinic, etc.)
- Manual baseline establishment by senior architects
- Automated accuracy scoring and reporting
- Continuous integration with analysis algorithm changes

### Contract Testing Strategy

**Decision**: Pact consumer-driven contract testing for API interfaces  
**Rationale**:
- Ensure API compatibility between analysis engine and dashboard
- Support for external system integration testing
- Version compatibility validation for API evolution
- Documentation generation from contract specifications

**Implementation Approach**:
- Consumer contracts for dashboard frontend interactions
- Provider contracts for analysis engine API responses
- Contract testing in CI/CD pipeline
- Contract evolution and compatibility matrix

## Next Steps

This research provides the foundation for Phase 1 design activities:

1. **Data Model Design**: Entity relationships and database schema design
2. **API Contract Specification**: REST and GraphQL API definitions
3. **Tool Integration Architecture**: Detailed integration patterns for static analysis tools
4. **Human-in-the-Loop Workflows**: Validation interface and approval process design
5. **Deployment Architecture**: Container orchestration and infrastructure requirements

All research findings support the constitutional requirements for migration intelligence, agent-driven architecture, and enterprise-grade quality and safety standards.