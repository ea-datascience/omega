# Omega Project Constitution

**Established**: November 18, 2025  
**Status**: Living Document  
**Purpose**: Define core principles and standards for the Omega migration system

---

## I. Mission and Vision

### Mission Statement
Omega is an intelligent agentic system designed to aid in software migrations from monolithic to microservices architectures through intelligent automation and proven methodologies.

### Vision
To be the definitive system for enterprise-scale application modernization, demonstrating capabilities in:
- Automated codebase analysis
- Migration planning and execution
- Risk assessment and mitigation
- Compliance and security validation

---

## II. Core Principles

### 1. Reproducibility Above All

**PRINCIPLE**: Every tool, configuration, and setup must be reproducible across all developers and environments.

**STANDARDS**:
- All installations MUST be scripted and version-controlled
- No ad-hoc command-line installations or manual downloads
- All dependencies MUST have pinned versions
- All tools MUST be stored in `/workspace/tools/` directory
- All utilities MUST be in `/workspace/tools/src/utils/` directory
- Installation scripts MUST be executable and documented

**RATIONALE**: 
- Ensures consistent development environments
- Prevents "works on my machine" issues
- Enables new developers to onboard quickly
- Supports CI/CD pipeline reliability

**EXAMPLES**:
```bash
# CORRECT: Scripted, versioned installation
./tools/src/utils/install-tree-sitter-java.sh

# INCORRECT: Ad-hoc installation
pip install tree-sitter-java

# CORRECT: Using utility module
from src.utils.parser_manager import install_recommended_parser
install_recommended_parser()

# INCORRECT: Direct imports without version control
import some_parser  # Where did this come from? What version?
```

### 2. No Emojis Policy

**STRICT DIRECTIVE**: Emojis are ABSOLUTELY PROHIBITED in all project contexts.

**SCOPE**:
- Documentation
- Git commit messages
- Code comments
- Chat responses
- Agent communications
- User interfaces

**RATIONALE**:
- Professional communication standards
- Accessibility concerns
- Focus on technical content
- International audience support

### 3. Documentation First

**PRINCIPLE**: All features, tools, and configurations must be documented before or concurrent with implementation.

**REQUIREMENTS**:
- Tool documentation in `/workspace/docs/`
- Setup guides for all infrastructure
- API documentation for all services
- Architecture decision records (ADRs) for significant choices

### 4. Testing and Validation

**PRINCIPLE**: All components must have automated tests before deployment.

**STANDARDS**:
- Unit tests for all utilities (target 80%+ coverage)
- Integration tests for all services
- End-to-end tests for complete workflows
- Tests stored in `/workspace/tools/tests/`

### 5. Infrastructure as Code

**PRINCIPLE**: All infrastructure must be defined in code and version-controlled.

**REQUIREMENTS**:
- Docker Compose for development environments
- Dockerfiles for all services
- Environment variables documented
- Secrets management via secure mechanisms (not hardcoded)

---

## III. Technology Standards

### Programming Languages

**PRIMARY**: Python 3.12+
- Required for all analysis engine components
- Enforced via dev container configuration
- Package management via `uv`

**SECONDARY**: Java 17+
- Required for Java analysis capabilities
- Installed via scripted setup in dev container
- JAVA_HOME properly configured

**FRONTEND**: TypeScript/Angular (when applicable)
- Modern framework for dashboard interfaces
- Type safety required

### Infrastructure Services

**REQUIRED SERVICES** (all managed via docker-compose):
- PostgreSQL 15+ with pg_vector extension
- ClickHouse for analytics
- Redis Cluster for caching
- MinIO for object storage
- Apache Kafka for event streaming

**CONFIGURATION**:
- All services defined in `/workspace/.devcontainer/docker-compose.yml`
- All connection utilities in `/workspace/tools/src/utils/service_utils.py`
- Health checks required for all services
- Authentication required for all services

### Dependency Management

**CRITICAL PRINCIPLE**: All dependencies MUST be declared in configuration files BEFORE installation.

**VERSION CONTROL**:
- All Python dependencies in `pyproject.toml` with pinned versions
- All JavaScript dependencies in `package.json` with pinned versions
- All system dependencies in `Dockerfile` with pinned versions
- NO ad-hoc installations allowed (pip install, npm install without updating config)

**WORKFLOW** (MANDATORY):
1. Add dependency to `pyproject.toml` (Python) or `package.json` (JavaScript)
2. Pin exact version number (e.g., `tree-sitter==0.23.2`, not `tree-sitter>=0.23.0`)
3. Run `uv pip install -e .` (Python) or `npm install` (JavaScript) to install
4. Commit configuration file changes to Git

**EXAMPLES**:
```toml
# pyproject.toml - CORRECT
[project.dependencies]
tree-sitter = "==0.23.2"  # Pinned version - reproducible
tree-sitter-java = "==0.23.5"  # Pinned version - reproducible
pyyaml = ">=6.0.0"  # Minimum version for compatibility

# INCORRECT - ad-hoc installation without config update
# pip install tree-sitter  # NO! Update pyproject.toml first!
```

**RATIONALE**:
- Ensures all developers have identical dependency versions
- Enables reproducible builds and deployments
- Prevents "dependency drift" between environments
- Supports automated CI/CD pipelines
- Allows dependency security auditing

**ENFORCEMENT**:
- Pre-commit hooks to verify dependencies match config (future)
- Code review requirement: all PRs with new imports must update config files
- CI pipeline fails if installed packages differ from config files

---

## IV. Project Structure

### Directory Organization

```
omega/
├── .devcontainer/          # Dev container configuration (required)
│   ├── Dockerfile          # Base image with all system dependencies
│   ├── devcontainer.json   # VS Code dev container settings
│   └── docker-compose.yml  # Infrastructure services orchestration
├── .github/                # GitHub configuration
│   ├── copilot-instructions.md  # AI pair programming guidelines
│   └── workflows/          # CI/CD pipelines (future)
├── data/                   # Reference codebases (not tracked)
│   └── codebase/           # Analysis test subjects
├── docs/                   # Project documentation (required)
│   ├── git/                # Git and GitHub setup guides
│   ├── setup/              # Infrastructure setup documentation
│   └── *.md                # Feature and architecture docs
├── prds/                   # Product requirement documents
├── specs/                  # Technical specifications
│   └── 001-*/              # Spec-driven development per feature
├── tools/                  # Analysis engine and utilities (required)
│   ├── src/                # Source code
│   │   ├── omega_analysis/ # Main analysis package
│   │   └── utils/          # Shared utilities (CRITICAL)
│   └── tests/              # Test suites (required)
│       ├── unit/           # Unit tests
│       └── integration/    # Integration tests
└── README.md               # Project overview
```

### Critical Directories

**`/workspace/tools/src/utils/`**: 
- Houses ALL shared utilities for developers
- Java environment management
- Parser management
- Service connection utilities
- Installation scripts

**`/workspace/docs/`**:
- All documentation must live here
- Setup guides for onboarding
- Architecture decisions
- API documentation

**`/workspace/specs/`**:
- Spec-driven development artifacts
- Task breakdowns
- Data models
- API contracts

---

## V. Development Workflow

### 1. Spec-Driven Development

**PROCESS**:
1. Write specification in `/workspace/specs/{feature-id}/`
2. Break down into tasks in `tasks.md`
3. Implement according to spec
4. Test against acceptance criteria
5. Document in `/workspace/docs/`

### 2. Tool Development

**WHEN CREATING NEW TOOLS**:
1. Place source in `/workspace/tools/src/utils/`
2. Create installation script if needed
3. Add tests in `/workspace/tools/tests/`
4. Document in `/workspace/docs/setup/`
5. Update copilot instructions

**EXAMPLE**:
```python
# /workspace/tools/src/utils/my_new_tool.py
"""Clear description of tool purpose and usage."""

def install_tool(version: str) -> bool:
    """Reproducible installation with version control."""
    pass

# /workspace/tools/tests/unit/test_my_new_tool.py
"""Comprehensive test coverage."""
```

### 3. Git Workflow

**BRANCH STRATEGY**:
- `main`: Production-ready code
- `{feature-id}`: Feature branches matching spec IDs
- Example: `001-system-discovery-baseline`

**COMMIT STANDARDS**:
- Clear, descriptive messages
- NO EMOJIS
- Reference spec/task IDs when applicable
- Example: "T023: Implement Context Mapper integration"

---

## VI. Quality Standards

### Code Quality

**REQUIREMENTS**:
- Type hints for all Python functions
- Docstrings for all public APIs
- Error handling for all external calls
- Logging for all significant operations

### Testing Requirements

**COVERAGE TARGETS**:
- Unit tests: 80%+ coverage
- Integration tests: All critical paths
- End-to-end tests: All user workflows

**TEST ORGANIZATION**:
```
tools/tests/
├── unit/                   # Fast, isolated tests
│   ├── test_java_utils.py
│   └── test_parser_manager.py
└── integration/            # Service integration tests
    ├── test_infrastructure_services.py
    └── test_end_to_end.py
```

### Documentation Requirements

**ALL TOOLS MUST HAVE**:
- Purpose and usage description
- Installation instructions
- Example usage
- API reference
- Troubleshooting section

---

## VII. Security and Compliance

### Credentials Management

**STANDARDS**:
- NO hardcoded credentials
- Use environment variables
- Document required secrets
- Provide example configurations

### Dependency Security

**REQUIREMENTS**:
- Regular security audits
- Pinned versions for stability
- CVE monitoring for critical dependencies
- Documented upgrade paths

---

## VIII. Communication Standards

### Documentation Language

**STYLE**:
- Clear, professional language
- Technical accuracy over marketing speak
- NO EMOJIS
- Accessible to international audience

### Code Comments

**GUIDELINES**:
- Explain "why", not "what"
- Document complex algorithms
- Reference specifications
- NO EMOJIS

---

## IX. Enforcement

### Automated Checks (Future)

**PLANNED**:
- Pre-commit hooks for emoji detection
- Linting for code quality
- Test coverage reporting
- Documentation completeness checks

### Manual Review

**CURRENT**:
- Code review for all changes
- Documentation review for new features
- Adherence to constitution in PR descriptions

---

## X. Amendment Process

This constitution is a living document. Amendments may be proposed through:

1. Create issue documenting proposed change
2. Discuss rationale and impact
3. Update constitution
4. Communicate to all contributors
5. Update tooling to reflect changes

---

## Appendix A: Quick Reference

### Essential Commands

```bash
# Evaluate available Java parsers
cd /workspace/tools && python -m src.utils.parser_manager evaluate

# Install recommended parser
cd /workspace/tools && ./src/utils/install-tree-sitter-java.sh

# Check infrastructure services
cd /workspace/tools && python -m src.utils.service_utils

# Run all tests
cd /workspace/tools && uv run pytest tests/ -v

# Check Java environment
cd /workspace/tools && python -m src.utils.java_utils
```

### Key Files

- Constitution: `/workspace/docs/omega-constitution.md`
- Copilot Instructions: `/workspace/.github/copilot-instructions.md`
- Infrastructure: `/workspace/.devcontainer/docker-compose.yml`
- Utilities: `/workspace/tools/src/utils/`

---

**Remember**: Reproducibility is not optional. Every developer must have the same environment, tools, and capabilities. This is achieved through rigorous adherence to these constitutional principles.
