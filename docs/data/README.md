# Data and Codebase Documentation

This section contains documentation for data management and reference codebase integration within the Omega project.

## Structure

```
docs/data/
└── codebase/
    └── reference-setup.md    # Guide for integrating reference repositories
```

## Purpose

The data documentation section covers:

- **Reference Codebase Management**: How to add, configure, and maintain external repositories for analysis
- **Data Organization**: Best practices for organizing datasets and reference materials
- **Version Control Integration**: Proper Git configuration to exclude reference data while maintaining project cleanliness

## Quick Start

For setting up reference codebases like Spring Modulith, see the [Reference Setup Guide](./codebase/reference-setup.md).

## Key Concepts

### Reference Repositories
External codebases used for:
- Migration analysis and testing
- Demonstrating system capabilities
- Providing real-world examples
- Algorithm validation

### Data Isolation
Reference data is:
- Stored locally in `/workspace/data/`
- Excluded from version control via `.gitignore`
- Organized by type (codebase, datasets, etc.)
- Documented for reproducibility

### Automated Tools
The project provides automated workflows for reference codebase management:
- **Bash Script**: Idempotent cloning with comprehensive validation (`/workspace/tools/src/clone-spring-modulith.sh`)
- **GitHub Prompt**: Operational wrapper with validation commands (`/workspace/.github/prompts/clonecodebase.prompt.md`)
- **Integrated Workflow**: Combined approach for consistent, reliable setup

### Clean Repository Maintenance
- Only Omega project files are tracked
- Reference materials remain available locally
- Repository size stays manageable
- Clear separation between project and reference code

## Contributing

When adding new reference materials:
1. Follow the established directory structure
2. Update `.gitignore` appropriately
3. Document the integration process
4. Ensure licensing compliance

---

*This documentation supports the systematic integration of reference materials for the Omega agentic migration system.*