# GitHub Copilot Instructions for Omega Project

## Project Overview

Omega is an intelligent agentic system designed to aid in software migrations from monolithic to microservices architectures. This project demonstrates the various capabilities and workflows necessary to successfully decompose monolithic applications into microservices through agentic systems and intelligent automation.

## Project Goals

When working on this project, keep in mind the primary objectives:

- **Demonstrate Migration Workflows**: Showcase end-to-end processes for breaking down monolithic applications
- **Provide Intelligent Automation**: Utilize agentic systems to assist in complex migration decisions
- **Establish Best Practices**: Document proven methodologies for microservices decomposition
- **Enable Practical Implementation**: Offer tools and frameworks that can be applied to real-world migration projects

## Key Capabilities Areas

### Automated Analysis
- Codebase dependency mapping
- Service boundary identification
- Data flow analysis
- API interface discovery

### Migration Planning
- Decomposition strategy generation
- Migration roadmap creation
- Risk assessment and mitigation
- Resource estimation and timeline planning

### Implementation Support
- Code refactoring assistance
- API design and documentation
- Database schema migration
- Infrastructure provisioning guidance

### Validation & Testing
- Migration validation frameworks
- Performance comparison tools
- Integration testing automation
- Rollback strategy implementation

## Architecture Context

The system is built using modern development practices and containerized environments:

- **Development Environment**: Docker-based dev containers for consistent development experience
- **Version Control**: Git with comprehensive documentation and workflow guides
- **Documentation**: Structured documentation for all processes and procedures
- **Extensibility**: Modular design allowing for custom migration scenarios

## Current Project Structure

```
omega/
├── .devcontainer/          # Development container configuration
├── .github/                # GitHub workflows and prompts
├── data/                   # Reference codebases and datasets (not tracked)
├── docs/                   # Project documentation
│   ├── git/               # Git and GitHub setup guides
│   └── data/              # Data management documentation
├── tools/                  # Migration tools and utilities
│   ├── src/               # Tool source code
│   └── tests/             # Tool test suites
└── README.md              # Project overview
```

## Development Guidelines

### Prerequisites
- Docker and Docker Compose
- Git with SSH access to GitHub
- VS Code with Dev Container extension (recommended)
- Python 3.12 (automatically configured in dev container)
- Node.js 20 LTS (automatically configured in dev container)
- Java 17 (automatically configured in dev container)

### Development Environment
The project uses a containerized development environment that automatically sets up Python 3.12, Node.js 20 LTS, Java 17, and all necessary dependencies when opened in VS Code with the Dev Container extension.

### Documentation Standards
Comprehensive guides are maintained in the `/docs` directory:
- Git setup and SSH configuration documentation
- Data management and reference codebase integration guides
- Tool development and testing guidelines
- Node.js and dashboard development setup guides

### Contributing Context
This project welcomes contributions from developers interested in:
- Microservices migration strategies
- Agentic systems and intelligent automation
- Software architecture evolution
- Migration tooling and frameworks

### Communication and Style Guidelines

**STRICT NO EMOJI POLICY**: Emojis are ABSOLUTELY PROHIBITED in this project. This is a strict directive that must be followed without exception:

1. **Documentation**: All project documentation must use clear, professional language with ZERO emojis or decorative symbols
2. **Git Commit Messages**: Commit messages are STRICTLY emoji-free and must focus on clear, descriptive text only
3. **Code Base**: NO emojis in code comments, variable names, or any code-related content whatsoever
4. **Chat Responses**: Provide direct, professional responses with ABSOLUTELY NO emoji decorations
5. **General Communication**: Default to completely emoji-free communication in ALL project contexts
6. **GitHub Copilot Interactions**: All GitHub Copilot responses must be completely free of emojis
7. **Agent Communications**: All agent modality interactions must maintain strict emoji-free professional communication

This is a non-negotiable requirement that ensures professional, accessible, and distraction-free communication focused exclusively on technical content. Any use of emojis violates project standards and must be immediately corrected.

### Reproducibility and Tooling Standards

**CRITICAL PRINCIPLE**: All tools, configurations, and setup procedures MUST be reproducible across all developers and environments.

**MANDATORY REQUIREMENTS**:

1. **No Ad-Hoc Installations**: Never use ad-hoc command-line installations or manual downloads
2. **Scripted Setup**: All installations MUST be scripted in `/workspace/tools/src/utils/`
3. **Version Pinning**: All dependencies MUST have explicitly pinned versions
4. **Utility Modules**: All shared utilities MUST be in `/workspace/tools/src/utils/`
5. **Documentation**: All tools MUST have setup documentation in `/workspace/docs/setup/`
6. **Testing**: All utilities MUST have tests in `/workspace/tools/tests/`
7. **Dependency Declaration**: ALL dependencies MUST be declared in configuration files BEFORE installation

**DEPENDENCY MANAGEMENT WORKFLOW** (STRICTLY ENFORCED):

```bash
# STEP 1: Add dependency to pyproject.toml FIRST
# Edit /workspace/tools/pyproject.toml:
#   dependencies = [
#       "pyyaml==6.0.3",  # Pin exact version
#   ]

# STEP 2: Install from configuration file
cd /workspace/tools && uv pip install -e .

# STEP 3: Commit configuration change
git add pyproject.toml
git commit -m "Add pyyaml==6.0.3 dependency for YAML config parsing"
```

**CORRECT EXAMPLES**:
```bash
# CORRECT: Update config file, then install
# 1. Edit pyproject.toml to add dependency
# 2. Run: cd /workspace/tools && uv pip install -e .

# CORRECT: Use scripted installation
./tools/src/utils/install-tree-sitter-java.sh

# CORRECT: Use utility module
python -m src.utils.parser_manager install --parser tree-sitter

# CORRECT: Check service status
python -m src.utils.service_utils
```

**INCORRECT EXAMPLES**:
```bash
# INCORRECT: Ad-hoc pip install (no version control, not reproducible)
pip install pyyaml  # NO! Update pyproject.toml first!

# INCORRECT: Ad-hoc uv pip install (not in config)
uv pip install tree-sitter  # NO! Add to pyproject.toml first!

# INCORRECT: Direct download (not tracked, not reproducible)
curl -O https://example.com/tool.zip && unzip tool.zip

# INCORRECT: Manual configuration (not documented, not reproducible)
# Manually editing config files without scripts
```

**WHEN CREATING NEW TOOLS**:

1. Create source in `/workspace/tools/src/utils/my_tool.py`
2. Pin all versions in the tool (e.g., `TOOL_VERSION = "1.2.3"`)
3. Add dependencies to `/workspace/tools/pyproject.toml` with pinned versions
4. Create installation script if needed in `/workspace/tools/src/utils/install-my-tool.sh`
5. Add tests in `/workspace/tools/tests/unit/test_my_tool.py`
6. Document in `/workspace/docs/setup/my-tool-setup.md`
7. Update this file (copilot-instructions.md) with tool availability

**RATIONALE**:
- Prevents "works on my machine" issues
- Enables consistent CI/CD pipelines
- Supports fast onboarding for new developers
- Ensures audit trail for all dependencies
- Facilitates security and compliance reviews
- Eliminates dependency drift between environments

See `/workspace/docs/omega-constitution.md` for complete reproducibility standards.

## Current Development Phase

The project is in its initial phase with the following established:
- Development container environment
- Git workflow and documentation framework
- Tools directory structure for migration utilities
- Reference codebase integration (Spring Modulith)

## Upcoming Development Areas

- Core agentic system implementation
- Migration analysis engines
- Sample monolith applications for demonstration
- Microservices decomposition tools
- Comprehensive testing frameworks

---

*Omega represents the culmination (Ω) of monolithic architecture evolution - the final transformation into distributed microservices.*

## Active Technologies
- Python 3.12+ (per constitution requirements) + Microsoft Agent Framework + JavaParser, Microsoft App Cat, SonarQube Enterprise (001-omega-migration-system)
- PostgreSQL 15+ with pg_vector, ClickHouse for analytics, MinIO for file storage, Redis Cluster for caching, Apache Kafka for events (001-omega-migration-system)
- Python 3.12+ (per constitution requirements) with Java 17+ for analysis tools + Microsoft Agent Framework, FastAPI, Docker, OpenTelemetry, Context Mapper, Structurizr, CodeQL, Microsoft AppCAT (001-system-discovery-baseline)
- PostgreSQL 15+ with pg_vector for analysis artifacts, MinIO for file storage, Redis Cluster for caching (001-system-discovery-baseline)

## Infrastructure Services (Available in Dev Container)
All infrastructure services are running and accessible via docker-compose:
- PostgreSQL 15 with pg_vector at postgres:5432 - OPERATIONAL
- ClickHouse at clickhouse:8123 (HTTP) and clickhouse:9000 (native) - OPERATIONAL  
- Redis at redis:6379 - OPERATIONAL
- MinIO at minio:9000 (console at localhost:9001) - OPERATIONAL
- Apache Kafka at kafka:9092 - OPERATIONAL
- SigNoz OTel Collector at signoz-otel-collector:4317 (gRPC), :4318 (HTTP) - OPERATIONAL
- SigNoz Query Service at signoz-query-service:8080 - OPERATIONAL
- SigNoz Frontend at localhost:3301 - OPERATIONAL

Service utilities available at `/workspace/tools/src/utils/service_utils.py` for connection management.

## Available Developer Utilities (All Reproducible)

All utilities are located in `/workspace/tools/src/utils/` for reproducible setup across all developers:

**Java Environment Management**:
- Module: `java_utils.py` - Java 17+ detection, validation, environment setup
- Command: `python -m src.utils.java_utils` - Check Java environment status
- Installation: Automatic in Dockerfile (OpenJDK 17)
- Tests: `tools/tests/unit/test_java_utils.py` (27 tests)

**Service Connection Management**:
- Module: `service_utils.py` - PostgreSQL, ClickHouse, Redis, MinIO, Kafka connections
- Command: `python -m src.utils.service_utils` - Check all service connections
- Configuration: All services in docker-compose.yml with health checks
- Tests: `tools/tests/integration/test_infrastructure_services.py` (14 tests)

**Java Parser Management**:
- Module: `parser_manager.py` - Reproducible parser installation and evaluation
- Command: `python -m src.utils.parser_manager evaluate` - Compare parser options
- Command: `python -m src.utils.parser_manager install --parser tree-sitter` - Install recommended parser
- Script: `install-tree-sitter-java.sh` - Standalone installation script
- Pinned Versions: tree-sitter==0.23.2, tree-sitter-java==0.23.5
- Documentation: See `/workspace/docs/setup/` for setup guides

**Context Mapper Integration**:
- Module: `context_mapper.py` - Context Mapper DSL & Discovery wrapper (481 lines)
- Installation: `install-context-mapper.sh` - Maven-based installer for CM libraries
- Pinned Versions: Context Mapper DSL 6.12.0, Discovery 1.1.0, Maven 3.9.9
- Features: Source code analysis (recommended), reflection-based analysis, CML/JSON export
- Tests: `tools/tests/unit/test_context_mapper.py` (12 tests)
- Tests: `tools/tests/integration/test_context_mapper_integration.py` (5 tests)
- Tests: `tools/tests/e2e/test_context_mapper_e2e.py` (4 tests)
- Documentation: `/workspace/docs/setup/context-mapper-setup.md`

**Spring Boot Analyzer**:
- Module: `spring_boot_analyzer.py` - Source code analyzer for Spring Boot apps (470 lines)
- Features: Module detection, service/entity classification, dependency analysis, no compilation
- Tests: `tools/tests/unit/test_spring_boot_analyzer.py` (16 tests)
- Tests: `tools/tests/integration/test_spring_boot_analyzer_integration.py` (8 tests)
- Documentation: `/workspace/docs/setup/context-mapper-setup.md` (integrated)

**Structurizr CLI Integration**:
- Module: `structurizr_cli.py` - Structurizr CLI wrapper for C4 diagrams (421 lines)
- Installation: `install-structurizr.sh` - Downloads CLI v2025.11.09 from GitHub
- Features: DSL validation, export to PlantUML/Mermaid/DOT, workspace inspection
- Tests: `tools/tests/unit/test_structurizr_cli.py` (14 tests)
- Tests: `tools/tests/integration/test_structurizr_cli_integration.py` (9 tests)
- Documentation: `/workspace/docs/setup/structurizr-cli-setup.md`

All utilities follow constitution principles: scripted, versioned, tested, and documented.

**Total Test Coverage**: 114 tests across all utilities (100% passing)

## Recent Changes
- 001-omega-migration-system: Added Python 3.12+ (per constitution requirements) + Microsoft Agent Framework + JavaParser, Microsoft App Cat, SonarQube Enterprise
- Agent Framework: Migrated from LangChain/LangGraph to Microsoft Agent Framework for agentic orchestration and deployment
