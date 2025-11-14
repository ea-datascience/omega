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

### Development Environment
The project uses a containerized development environment that automatically sets up Python 3.12 and all necessary dependencies when opened in VS Code with the Dev Container extension.

### Documentation Standards
Comprehensive guides are maintained in the `/docs` directory:
- Git setup and SSH configuration documentation
- Data management and reference codebase integration guides
- Tool development and testing guidelines

### Contributing Context
This project welcomes contributions from developers interested in:
- Microservices migration strategies
- Agentic systems and intelligent automation
- Software architecture evolution
- Migration tooling and frameworks

### Communication and Style Guidelines

**Emoji Usage Policy**: Emojis are strongly discouraged and should NOT be used unless explicitly requested by the user. This applies to:
1. **Documentation**: All project documentation should use clear, professional language without decorative emojis
2. **Git Commit Messages**: Commit messages must be emoji-free and focus on clear, descriptive text
3. **Code Base**: No emojis in code comments, variable names, or any code-related content
4. **Chat Responses**: Provide direct, professional responses without emoji decorations
5. **General Communication**: Default to emoji-free communication in all project contexts

This policy ensures professional, accessible, and distraction-free communication that focuses on technical content rather than visual decorations.

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