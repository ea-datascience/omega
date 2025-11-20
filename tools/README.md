# Tools Directory

This directory hosts the development of tools required for monolith-to-microservices migration work within the Omega agentic system.

## Purpose

The `tools` directory contains custom-built utilities, scripts, and automation tools specifically designed to support the migration analysis and decomposition processes. These tools work in conjunction with the agentic system to provide comprehensive migration capabilities.

## Directory Structure

```
tools/
├── src/           # Source code for migration tools
├── tests/         # Test suites for tool validation
└── README.md      # This file
```

## Tool Categories

### Analysis Tools
- Codebase dependency analyzers
- Service boundary identification utilities
- Data flow mapping tools
- API interface discovery scripts

### Migration Planning Tools
- Decomposition strategy generators
- Migration roadmap creators
- Risk assessment utilities
- Resource estimation calculators

### Implementation Support Tools
- Code refactoring assistants
- API design generators
- Database schema migration helpers
- Infrastructure provisioning scripts

### Validation Tools
- Migration validation frameworks
- Performance comparison utilities
- Integration testing automation
- Rollback strategy validators

## Development Guidelines

### Source Code (`src/`)
- Organize tools by functionality or migration phase
- Use clear, descriptive naming conventions
- Include comprehensive docstrings and comments
- Follow Python best practices and PEP 8 standards

### Testing (`tests/`)
- Maintain corresponding test files for each tool
- Use pytest framework for consistency
- Include unit tests, integration tests, and end-to-end tests
- Ensure adequate test coverage for critical functionality

### Tool Requirements
- Each tool should be self-contained and modular
- Provide clear command-line interfaces where applicable
- Include configuration options for different migration scenarios
- Support integration with the broader agentic system

## Usage

Tools in this directory are designed to:
1. **Analyze** reference codebases like Spring Modulith
2. **Generate** migration strategies and plans
3. **Assist** in implementation and refactoring
4. **Validate** migration success and performance

## Integration

These tools integrate with:
- Reference codebases in `/data/codebase/`
- Documentation and analysis results in `/docs/`
- The main agentic system components
- External APIs and services as needed

## Contributing

When developing new tools:
1. Create source files in the appropriate `src/` subdirectory
2. Write comprehensive tests in the `tests/` directory
3. Update this README with tool descriptions
4. Document tool usage and integration points
5. Ensure tools follow the established patterns and conventions

## Available Tools

### System Discovery & Analysis Tools

#### 1. Context Mapper Integration (`src/utils/context_mapper.py`)

Python wrapper for Context Mapper DSL and Discovery libraries, providing two analysis modes:

**Features:**
- **Source Code Analysis** (recommended): Direct analysis without compilation
- **Reflection-based Analysis**: Bytecode analysis for compiled applications
- CML and JSON report generation
- Spring Boot module and bounded context discovery
- Integration with Spring Boot Analyzer

**Installation:** `./src/utils/install-context-mapper.sh`  
**Documentation:** `/docs/setup/context-mapper-setup.md`  
**Tests:** 21 tests (12 unit + 5 integration + 4 E2E)  
**Version:** Context Mapper DSL 6.12.0, Discovery 1.1.0

#### 2. Spring Boot Analyzer (`src/utils/spring_boot_analyzer.py`)

Source code analyzer for Spring Boot applications providing module structure discovery.

**Features:**
- Module detection and classification
- Service, entity, and repository identification
- Dependency graph analysis
- CML and JSON export
- No compilation required

**Documentation:** `/docs/setup/context-mapper-setup.md` (integrated section)  
**Tests:** 24 tests (16 unit + 8 integration)  
**Python Module:** Import as `from src.utils.spring_boot_analyzer import SpringBootAnalyzer`

#### 3. Structurizr CLI Integration (`src/utils/structurizr_cli.py`)

Python wrapper for Structurizr CLI providing C4 model diagram generation.

**Features:**
- Workspace DSL validation
- Export to PlantUML, Mermaid, DOT, WebSequenceDiagrams, Ilograph
- Workspace inspection and element listing
- Support for System Context, Container, Component, and Dynamic views

**Installation:** `./src/utils/install-structurizr.sh`  
**Documentation:** `/docs/setup/structurizr-cli-setup.md`  
**Tests:** 23 tests (14 unit + 9 integration)  
**Version:** Structurizr CLI 2025.11.09

### Infrastructure & Environment Tools

#### 4. Java Environment Manager (`src/utils/java_utils.py`)

Comprehensive Java environment detection and validation utilities.

**Features:**
- Java 17+ detection and validation
- JAVA_HOME management
- Maven/Gradle detection
- Classpath utilities
- Vendor identification (OpenJDK, Oracle, etc.)

**Python Module:** Import as `from src.utils.java_utils import JavaEnvironmentManager`  
**Tests:** 27 unit tests  
**Required:** Java 17+ (pre-installed in dev container)

#### 5. Service Connection Manager (`src/utils.service_utils.py`)

Database and infrastructure service connection management.

**Features:**
- PostgreSQL 15 with pg_vector
- ClickHouse for analytics
- Redis Cluster for caching
- MinIO for object storage
- Apache Kafka for event streaming
- Connection health checks and validation

**Python Module:** Import as `from src.utils.service_utils import get_postgres_connection`  
**Tests:** 14 integration tests  
**Services:** All running in docker-compose

### Build & Setup Tools

#### 6. Maven Installation (`src/utils/install-maven.sh`)

Reproducible Maven 3.9.9 installation script.

**Features:**
- Version-pinned download (3.9.9)
- Automatic environment configuration
- PATH setup
- Verification tests

**Installation Location:** `/opt/maven`  
**Usage:** Run once during project setup

#### 7. Spring Modulith Clone (`src/utils/clone-spring-modulith.sh`)

Idempotent script for cloning the Spring Modulith reference repository.

**Purpose:**
- Clone official Spring Modulith repository for migration analysis
- Idempotent operation (safe to run multiple times)
- Latest version availability with validation
- Integration with Omega workflow

**Target Directory:** `/workspace/data/codebase/spring-modulith`  
**Usage:** Run when setting up reference codebase

### Development Utilities

#### 8. Parser Manager (`src/utils/parser_manager.py`)

Java parser evaluation and installation tool.

**Features:**
- Compare parser options (tree-sitter-java, javalang, JavaParser)
- Automated installation with version pinning
- Performance and capability evaluation
- Reproducible setup

**CLI Usage:** `python -m src.utils.parser_manager evaluate`  
**Recommended:** tree-sitter-java 0.23.5

#### 9. Checkpoint Creator (`src/utils/create-checkpoint.sh`)

Project state checkpoint creation for progress tracking.

**Features:**
- Captures full project context
- JSON format with timestamp
- Git integration
- Progress validation

**Output:** `/workspace/checkpoints/checkpoint_YYYYMMDD_HHMMSS.json`  
**Usage:** Run after completing major work units

#### 10. Report Generator (`src/utils/report_generator.py`)

Analysis report generation utilities.

**Features:**
- Markdown report generation
- Data aggregation and formatting
- Template-based output

**Python Module:** Import as `from src.utils.report_generator import generate_report`

### Coming Soon

The following tools are planned for system discovery baseline:

- **CodeQL CLI Integration** (T025a): Static code analysis and security scanning
- **Microsoft AppCAT CLI** (T026a): Azure migration assessment and recommendations

#### Features
- **Idempotent Operation**: Safely handles existing repositories by removing and re-cloning
- **Comprehensive Logging**: Color-coded output with detailed progress reporting
- **Error Handling**: Robust error checking and graceful failure handling
- **Repository Validation**: Verifies repository structure, remote URL, and file integrity
- **Information Display**: Shows repository metadata (size, branch, last commit)
- **Directory Management**: Automatically creates required directory structure

#### Usage
```bash
# Basic usage - execute the script
/workspace/tools/src/clone-spring-modulith.sh

# Alternative execution methods
cd /workspace/tools/src
./clone-spring-modulith.sh

# Run from anywhere in the project
bash /workspace/tools/src/clone-spring-modulith.sh
```

#### Configuration
The script uses these default settings:
- **Source Repository**: `https://github.com/spring-projects/spring-modulith.git`
- **Target Directory**: `/workspace/data/codebase/spring-modulith`
- **Operation Mode**: Idempotent (removes existing, clones fresh)

#### Output Example
```
========================================
Spring Modulith Repository Setup Script
========================================
[INFO] Starting idempotent repository setup...
[SUCCESS] Directory structure created: /workspace/data/codebase
[INFO] Cloning Spring Modulith repository...
[SUCCESS] Repository cloned successfully
[SUCCESS] Repository verification passed
[INFO] Repository Information:
  Location: /workspace/data/codebase/spring-modulith
  Size: 12M
  Remote URL: https://github.com/spring-projects/spring-modulith.git
  Current Branch: main
  Last Commit: b6c2d006 - GH-1455 - Cleanup configuration metadata creation. (3 hours ago)
========================================
[SUCCESS] Spring Modulith repository setup completed successfully!
========================================
```

#### Integration
- Works with GitHub Copilot prompt at `/workspace/.github/prompts/clonecodebase.prompt.md`
- Respects `.gitignore` rules to exclude cloned repository from version control
- Provides foundation for migration analysis workflows
- Supports automated validation through comprehensive verification steps

### 2. Project Checkpoint Script (`src/create-checkpoint.sh`)

A comprehensive tool for creating detailed project state snapshots to facilitate resuming development sessions.

#### Purpose
- Capture complete project state for development session continuity
- Provide comprehensive context for GitHub Copilot integration
- Enable seamless work resumption after breaks or handoffs
- Document current tasks, blockers, and next steps
- Preserve Git status and modified file information

#### Features
- **Interactive Context Capture**: Prompts for current work details (epics, tasks, status)
- **Comprehensive Git Analysis**: Staged, unstaged, and untracked file tracking
- **Environment Documentation**: Development environment and tool version capture
- **Recent Activity Summary**: Last commits and file changes overview  
- **Project Structure Snapshot**: Directory tree and organization overview
- **Resume Instructions**: Step-by-step guidance for continuing work
- **Timestamped Storage**: Organized checkpoint files with date/time naming
- **Multiple Output Modes**: Create, list, or help functionality

#### Usage
```bash
# Create new checkpoint (interactive mode)
/workspace/tools/src/create-checkpoint.sh

# Alternative creation syntax
/workspace/tools/src/create-checkpoint.sh --create

# List existing checkpoints
/workspace/tools/src/create-checkpoint.sh --list

# Show help and usage information
/workspace/tools/src/create-checkpoint.sh --help
```

#### Interactive Prompts
When creating a checkpoint, the script prompts for:
- **Current Epic/Feature**: High-level work area
- **Current Task/Issue**: Specific task or issue being addressed
- **Task Status**: Current progress (in-progress, blocked, testing, etc.)
- **Next Planned Tasks**: Upcoming work items
- **Blockers/Issues**: Current obstacles or dependencies
- **Notes/Context**: Additional relevant information

#### Checkpoint Content Structure
Each checkpoint file includes:

1. **Overview Section**
   - Timestamp and project identification
   - Repository information

2. **Git Status Information**
   - Current branch and latest commit details
   - Remote URL and repository status
   - Staged, unstaged, and untracked file counts

3. **Modified Files Analysis**
   - Detailed tables of staged files with status
   - Unstaged modifications with change types
   - Untracked files listing

4. **Work Context**
   - Current epic, task, and status information
   - Next planned tasks and blockers
   - Additional notes and context

5. **Recent Activity Summary**
   - Last 5 commits with details
   - Recent file changes by commit

6. **Development Environment**
   - Operating system and tool versions
   - Virtual environment status
   - Development container detection

7. **Project Structure**
   - Directory tree overview (3-level depth)
   - Key directory explanations

8. **Resume Instructions**
   - Step-by-step environment setup
   - Context recovery procedures
   - Development continuation guidance
   - Reference resource locations

9. **GitHub Copilot Context**
   - Project goals and objectives
   - Key directory purposes
   - Current development phase information

#### File Organization
- **Storage Location**: `/workspace/checkpoints/`
- **Naming Convention**: `checkpoint_YYYYMMDD_HHMMSS.md`
- **Format**: Markdown for easy reading and GitHub integration
- **File Size**: Typically 3-8KB depending on project state

#### Example Checkpoint Filename
```
checkpoint_20251113_152345.md
```

#### Output Example
```
========================================
Omega Project Checkpoint Script
========================================
[INFO] Creating project checkpoint...
[SECTION] Capturing Current Work Context
Please provide information about your current work:

Current Epic/Feature: Reference Codebase Integration
Current Task/Issue: Implement checkpoint system
Current Status: in-progress
...

[SUCCESS] Checkpoint created successfully!
[INFO] Checkpoint saved to: /workspace/checkpoints/checkpoint_20251113_152345.md
[INFO] Checkpoint size: 4.2K
```

#### Best Practices
- **Create checkpoints** at natural stopping points (end of sessions, before breaks)
- **Use descriptive context** when prompted to aid in work resumption
- **Review previous checkpoints** when resuming work to understand recent progress
- **Clean up old checkpoints** periodically to maintain organization
- **Include blockers and dependencies** to help prioritize next steps

#### Integration Benefits
- **GitHub Copilot Enhancement**: Provides rich context for AI assistance
- **Team Collaboration**: Enables seamless handoffs between developers
- **Progress Tracking**: Maintains historical record of development progression
- **Issue Resolution**: Documents blockers and their resolution over time
- **Development Continuity**: Reduces context switching overhead

## Tool Integration Workflow

Both tools are designed to work together as part of the comprehensive Omega development workflow:

1. **Setup Phase**: Use `clone-spring-modulith.sh` to establish reference codebase
2. **Development Phase**: Regular use of `create-checkpoint.sh` for state management
3. **Analysis Phase**: Reference codebase available for migration analysis
4. **Collaboration Phase**: Checkpoints facilitate team handoffs and context sharing

## Future Development

This directory will evolve to include:
- Machine learning models for migration decision-making
- Advanced static analysis tools
- Real-time monitoring and feedback systems
- Integration with popular development frameworks
- Cloud-native deployment utilities
- Automated checkpoint creation triggers
- Checkpoint comparison and diff tools

---

*The tools directory serves as the practical implementation layer of the Omega agentic migration system, providing the concrete utilities needed to transform monolithic applications into microservices architectures.*