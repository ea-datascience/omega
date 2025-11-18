# Reproducibility Standards - Quick Reference

This document provides a quick reference for the reproducibility standards established in the Omega Constitution.

## Core Principle

**Every tool, configuration, and setup MUST be reproducible across all developers and environments.**

## Mandatory Checklist for New Tools

When creating any new tool or utility:

- [ ] Source code in `/workspace/tools/src/utils/`
- [ ] Pinned versions for all dependencies
- [ ] Installation script (if needed) in `/workspace/tools/src/utils/`
- [ ] Unit tests in `/workspace/tools/tests/unit/`
- [ ] Integration tests (if applicable) in `/workspace/tools/tests/integration/`
- [ ] Documentation in `/workspace/docs/setup/`
- [ ] Updated `/workspace/.github/copilot-instructions.md`
- [ ] Updated `/workspace/tools/src/utils/__init__.py` exports

## What NOT to Do

### INCORRECT: Ad-hoc installations
```bash
# DON'T DO THIS - not reproducible, no version control
pip install some-library
curl -O https://example.com/tool.zip && unzip tool.zip
apt-get install some-package  # unless in Dockerfile
```

### CORRECT: Scripted installations
```bash
# DO THIS - reproducible, versioned, documented
./tools/src/utils/install-my-tool.sh
python -m src.utils.my_tool_manager install
```

## Example: Java Parser Installation

### Incorrect Approach (Ad-hoc)
```bash
# This is NOT reproducible
pip install tree-sitter-java
```

### Correct Approach (Scripted)
```bash
# Option 1: Use installation script
./tools/src/utils/install-tree-sitter-java.sh

# Option 2: Use parser manager
python -m src.utils.parser_manager install --parser tree-sitter

# Option 3: Programmatic installation
from src.utils.parser_manager import install_recommended_parser
install_recommended_parser()
```

## Version Pinning

All dependencies MUST have explicitly pinned versions:

```python
# parser_manager.py
TREE_SITTER_VERSION = "0.23.5"  # Pinned, not "latest"
TREE_SITTER_CORE_VERSION = "0.23.2"  # Pinned, not "^0.23"
```

```toml
# pyproject.toml
[project.dependencies]
tree-sitter = "==0.23.2"  # Exact version, not ">= or ~="
tree-sitter-java = "==0.23.5"
```

## Testing Requirements

Every utility must have tests:

```
tools/tests/
├── unit/
│   ├── test_java_utils.py       # 27 tests
│   ├── test_parser_manager.py   # Required for new tool
│   └── test_my_new_tool.py      # Create for your tool
└── integration/
    ├── test_infrastructure_services.py  # 14 tests
    └── test_my_tool_integration.py      # If tool integrates with services
```

## Documentation Requirements

Every tool must have documentation:

```
docs/setup/
├── java-setup.md
├── infrastructure-services.md
└── my-new-tool-setup.md  # Create for your tool
```

Minimum documentation sections:
1. **Purpose**: What does this tool do?
2. **Installation**: How to install (reproducibly)
3. **Usage**: Examples of common use cases
4. **Configuration**: Environment variables, config files
5. **Troubleshooting**: Common issues and solutions
6. **Version History**: Major version changes and migration guides

## Available Utilities

Current reproducible utilities in `/workspace/tools/src/utils/`:

1. **java_utils.py**: Java environment detection and validation
   - Command: `python -m src.utils.java_utils`
   - Tests: 27 unit tests
   
2. **service_utils.py**: Infrastructure service connections
   - Command: `python -m src.utils.service_utils`
   - Tests: 14 integration tests
   
3. **parser_manager.py**: Java parser installation and evaluation
   - Command: `python -m src.utils.parser_manager evaluate`
   - Versions: tree-sitter==0.23.2, tree-sitter-java==0.23.5

## Rationale

Why is reproducibility so critical?

1. **Onboarding**: New developers can set up environment in minutes
2. **CI/CD**: Automated builds are consistent and reliable
3. **Debugging**: "Works on my machine" problems are eliminated
4. **Security**: All dependencies are tracked and auditable
5. **Compliance**: Audit trails for all software components
6. **Collaboration**: Team members have identical environments

## Enforcement

Current enforcement mechanisms:
- Manual code review
- Documentation checks in PR process
- Test coverage requirements

Future enforcement (planned):
- Pre-commit hooks to detect ad-hoc installations
- Automated documentation completeness checks
- CI/CD pipeline validation of reproducibility

## Getting Help

If you're unsure whether your approach is reproducible:

1. Check existing utilities in `/workspace/tools/src/utils/` for patterns
2. Review `/workspace/docs/omega-constitution.md` Section II.1
3. Review `/workspace/.github/copilot-instructions.md` reproducibility section
4. Ask: "Can another developer run this command on a fresh dev container?"

## Related Documents

- `/workspace/docs/omega-constitution.md` - Full constitutional principles
- `/workspace/.github/copilot-instructions.md` - AI assistant guidelines
- `/workspace/tools/src/utils/README.md` - Utilities overview (if exists)

---

**Remember**: If it's not scripted, versioned, and tested, it's not reproducible.
