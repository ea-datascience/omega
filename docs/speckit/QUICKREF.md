# Spec Kit Quick Reference

## Installation Commands

```bash
# Automated setup (recommended)
./tools/src/setup-speckit.sh

# Check installation status
./tools/src/setup-speckit.sh --check

# Force reinstall
./tools/src/setup-speckit.sh --reinstall

# Manual installation
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init --here --ai copilot --force
```

## GitHub Copilot Slash Commands

### Core Workflow
- `/speckit.constitution` - Create project principles
- `/speckit.specify` - Define requirements
- `/speckit.plan` - Create implementation plans  
- `/speckit.tasks` - Generate task lists
- `/speckit.implement` - Execute implementation

### Quality & Analysis
- `/speckit.clarify` - Clarify specifications
- `/speckit.analyze` - Consistency analysis
- `/speckit.checklist` - Quality validation

## CLI Commands

```bash
# System check
specify check

# Project initialization
specify init <project-name> --ai copilot

# Tool management
uv tool list
uv tool upgrade specify-cli
uv tool uninstall specify-cli
```

## Omega Integration Examples

### Migration Analysis Engine
```
/speckit.specify Build a migration analysis engine that analyzes Spring Modulith codebases and generates microservices decomposition recommendations with JSON output.
```

### Project Constitution
```
/speckit.constitution Create principles focusing on migration workflows, code quality, AI-driven automation, and integration with existing Omega tools.
```

### Implementation Planning
```
/speckit.plan Use Python 3.12, Docker dev containers, existing Omega infrastructure, and JSON data formats for seamless integration.
```

## File Structure

```
omega/
├── .speckit/              # Spec Kit configuration
├── features/              # Feature specifications
├── specs/                 # Technical specifications  
├── constitution.md        # Project principles
└── docs/speckit/         # This documentation
```

## Troubleshooting

```bash
# Verify installation
./tools/src/setup-speckit.sh --check

# System diagnostics
specify check

# Reinstall if needed
./tools/src/setup-speckit.sh --reinstall
```