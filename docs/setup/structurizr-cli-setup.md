# Structurizr CLI Setup Guide

This guide provides complete setup and usage instructions for Structurizr CLI integration in the Omega project.

## Overview

**Structurizr CLI** is a command-line tool for working with Structurizr workspaces. It supports:

- **Architecture Diagram Export**: PlantUML, Mermaid, DOT, WebSequenceDiagrams, Ilograph
- **Workspace Validation**: DSL syntax checking and semantic validation
- **Workspace Inspection**: Analyze model structure and relationships
- **C4 Model Support**: Full support for Context, Container, Component, and Code diagrams

**Version Pinning:**
- Structurizr CLI: `2025.11.09`
- Java: `17+` (OpenJDK 17.0.16 in dev container)
- Installation Location: `/opt/structurizr-cli/`

## Prerequisites

Before installing Structurizr CLI:

1. **Java 17+** is required
2. **Git** for installation from GitHub releases
3. **Write access** to `/opt/` directory

## Installation

### Automated Installation (Recommended)

Use the reproducible installation script:

```bash
cd /workspace/tools/src/utils
./install-structurizr.sh
```

The script:
- Downloads Structurizr CLI v2025.11.09 from GitHub releases
- Extracts to `/opt/structurizr-cli/`
- Makes CLI scripts executable
- Verifies Java 17+ availability
- Tests CLI installation

### Manual Installation

If you need to install manually:

```bash
# Download specific version
cd /tmp
wget https://github.com/structurizr/cli/releases/download/v2025.11.09/structurizr-cli.zip

# Extract to /opt
sudo unzip structurizr-cli.zip -d /opt/structurizr-cli

# Make scripts executable
sudo chmod +x /opt/structurizr-cli/structurizr.sh
sudo chmod +x /opt/structurizr-cli/structurizr.bat

# Verify installation
/opt/structurizr-cli/structurizr.sh help
```

### Verification

Check that Structurizr CLI is properly installed:

```bash
/opt/structurizr-cli/structurizr.sh version
```

Expected output:
```
structurizr-cli: 2025.11.09
structurizr-java: 3.1.0
```

## Python Integration

### Basic Usage

```python
from pathlib import Path
from src.utils.structurizr_cli import StructurizrCLI

# Initialize CLI
cli = StructurizrCLI()

# Validate workspace
workspace_file = Path("/workspace/diagrams/workspace.dsl")
result = cli.validate_workspace(workspace_file)

if result.valid:
    print("✓ Workspace is valid")
else:
    print(f"✗ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### Export Diagrams

```python
# Export to PlantUML
result = cli.export_diagrams(
    workspace_file=Path("workspace.dsl"),
    format="plantuml",
    output_dir=Path("/workspace/diagrams/plantuml")
)

if result.success:
    print(f"Exported {len(result.files)} diagram(s)")
    for file in result.files:
        print(f"  - {file}")
```

### Supported Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `plantuml` | `.puml` | PlantUML diagram format |
| `mermaid` | `.mmd` | Mermaid diagram format |
| `dot` | `.dot` | Graphviz DOT format |
| `websequencediagrams` | `.txt` | WebSequenceDiagrams format |
| `ilograph` | `.json` | Ilograph format |
| `json` | `.json` | Structurizr JSON format |

### Inspect Workspace

```python
# Get workspace metadata
result = cli.inspect_workspace(Path("workspace.dsl"))
print(result["output"])
```

Example output:
```
Model:
- 1 person(s)
- 1 software system(s)
- 2 container(s)
- 0 component(s)
- 3 relationship(s)

Views:
- 1 system context view(s)
- 1 container view(s)
```

### Error Handling

```python
from src.utils.structurizr_cli import StructurizrError

try:
    cli = StructurizrCLI()
    result = cli.export_diagrams(
        workspace_file=Path("workspace.dsl"),
        format="plantuml"
    )
except StructurizrError as e:
    print(f"Error: {e}")
```

## Creating Structurizr Workspaces

### Minimal Workspace Example

Create `workspace.dsl`:

```
workspace "My System" "Architecture documentation" {

    model {
        user = person "User"
        system = softwareSystem "My System" {
            webapp = container "Web App" "Delivers content" "React"
            api = container "API" "Business logic" "Python/FastAPI"
            db = container "Database" "Stores data" "PostgreSQL"
        }
        
        user -> webapp "Uses"
        webapp -> api "Makes API calls to"
        api -> db "Reads/writes"
    }
    
    views {
        systemContext system "SystemContext" {
            include *
            autolayout lr
        }
        
        container system "Containers" {
            include *
            autolayout lr
        }
        
        theme default
    }
}
```

### C4 Model Best Practices

1. **Start with System Context**: Define external actors and systems
2. **Add Containers**: Show high-level technology choices
3. **Drill into Components**: Detail internal structure where needed
4. **Use Meaningful Names**: Clear, business-oriented terminology
5. **Add Descriptions**: Explain purpose and technology choices
6. **Apply Themes**: Use consistent styling

## CLI Reference

### Command-Line Usage

```bash
# Validate workspace
/opt/structurizr-cli/structurizr.sh validate \
    --workspace workspace.dsl

# Export to PlantUML
/opt/structurizr-cli/structurizr.sh export \
    --workspace workspace.dsl \
    --format plantuml \
    --output /workspace/diagrams

# Inspect workspace
/opt/structurizr-cli/structurizr.sh inspect \
    --workspace workspace.dsl

# Show version
/opt/structurizr-cli/structurizr.sh version

# Show help
/opt/structurizr-cli/structurizr.sh help
```

## Testing

### Run Unit Tests

```bash
cd /workspace/tools
python -m pytest tests/unit/test_structurizr_cli.py -v
```

### Run Integration Tests

```bash
cd /workspace/tools
python -m pytest tests/integration/test_structurizr_cli_integration.py -v
```

### Test Coverage

The test suite includes:
- **14 unit tests**: API validation, mocking, error handling
- **9 integration tests**: Real CLI execution, format validation

## Troubleshooting

### Java Version Issues

If you see "Java 17+ is required":

```bash
# Check Java version
java -version

# Verify JAVA_HOME
echo $JAVA_HOME

# Update if needed (in dev container, Java 17 is pre-installed)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
```

### CLI Not Found

If initialization fails with "Structurizr CLI not found":

```bash
# Check installation
ls -la /opt/structurizr-cli/structurizr.sh

# Reinstall if needed
cd /workspace/tools/src/utils
./install-structurizr.sh
```

### Validation Errors

Common DSL validation errors:

1. **Undefined element**: Element referenced before definition
   ```
   # ✗ Wrong
   a -> b "uses"
   b = softwareSystem "B"
   
   # ✓ Correct
   b = softwareSystem "B"
   a -> b "uses"
   ```

2. **Missing quotes**: String literals must be quoted
   ```
   # ✗ Wrong
   person User
   
   # ✓ Correct
   person "User"
   ```

3. **Invalid syntax**: Check braces and semicolons
   ```
   # ✗ Wrong
   softwareSystem "System" {
       container "App"
   # Missing closing brace
   
   # ✓ Correct
   softwareSystem "System" {
       container "App" "Description" "Tech"
   }
   ```

## Integration with Omega Tools

### With Context Mapper

Generate C4 diagrams from Spring Boot analysis:

```python
from src.utils.context_mapper import ContextMapper
from src.utils.structurizr_cli import StructurizrCLI

# Analyze Spring Boot codebase
cm = ContextMapper()
result = cm.analyze_spring_boot_source(
    source_root=Path("/workspace/data/codebase/spring-modulith")
)

# TODO: Convert CML to Structurizr DSL
# This would require a CML->DSL transformer

# Export diagrams
cli = StructurizrCLI()
cli.export_diagrams(
    workspace_file=Path("generated-workspace.dsl"),
    format="plantuml"
)
```

### With Spring Boot Analyzer

```python
from src.utils.spring_boot_analyzer import SpringBootAnalyzer
from src.utils.structurizr_cli import StructurizrCLI

# Analyze Spring Boot structure
analyzer = SpringBootAnalyzer(
    source_root=Path("/workspace/data/codebase/my-app")
)
result = analyzer.analyze()

# TODO: Generate Structurizr DSL from analysis result
# workspace_dsl = generate_structurizr_workspace(result)

# Export diagrams
cli = StructurizrCLI()
cli.export_diagrams(
    workspace_file=Path("app-workspace.dsl"),
    format="mermaid"
)
```

## Version Information

```python
from src.utils.structurizr_cli import StructurizrCLI

cli = StructurizrCLI()
info = cli.get_version_info()

print(f"Structurizr CLI: {info['structurizr_cli']}")
print(f"Java: {info['java_version']}")
print(f"CLI Path: {info['cli_path']}")
```

## References

- **Structurizr CLI GitHub**: https://github.com/structurizr/cli
- **Structurizr DSL Language Reference**: https://docs.structurizr.com/dsl/language
- **C4 Model**: https://c4model.com/
- **PlantUML**: https://plantuml.com/
- **Mermaid**: https://mermaid.js.org/

## See Also

- [Context Mapper Setup](./context-mapper-setup.md)
- [Java Utils Reference](../tools/java-utils.md)
- [System Discovery Baseline](../../prds/epic-1.1-system-discovery-baseline-assessment.md)
