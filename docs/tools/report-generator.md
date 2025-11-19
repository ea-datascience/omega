# Report Generator - Comprehensive Codebase Analysis Tool

**Version:** 1.0.0  
**Location:** `/workspace/tools/src/utils/report_generator.py`  
**Type:** Standalone CLI Utility

## Overview

The Report Generator is a comprehensive analysis tool that generates detailed migration readiness reports for Java Spring Boot codebases. It performs static analysis and generates C4 architecture diagrams at multiple levels of abstraction.

### Key Capabilities

- **Static Code Analysis**: Analyzes Java source code using tree-sitter-java
- **C4 Diagram Generation**: Generates all 4 levels of C4 diagrams (Context, Container, Component, Code)
- **Dependency Mapping**: Identifies and classifies external dependencies
- **Module Analysis**: Analyzes modular codebases with multiple Spring Boot modules
- **Migration Assessment**: Provides complexity scoring and migration readiness indicators
- **Multiple Export Formats**: Generates Markdown reports, JSON data, and PlantUML diagrams

## Prerequisites

### Required Tools

```bash
# Java 17+ (for analyzing Java codebases)
java -version  # Should show 17 or higher

# Python 3.12+
python --version

# tree-sitter-java 0.23.5 (automatically installed via pyproject.toml)
```

### Optional Tools

```bash
# PlantUML (for rendering diagrams to images)
sudo apt-get install plantuml

# Or use online renderer: https://www.plantuml.com/plantuml/uml/
```

## Installation

The report generator is already available in the Omega development container. No additional installation required.

```bash
# Verify installation
cd /workspace/tools
python -m src.utils.report_generator --help
```

## Usage

### Basic Command Structure

```bash
python -m src.utils.report_generator analyze \
  --codebase /path/to/codebase \
  --output /path/to/output \
  --project-name project-name \
  [--no-diagrams] \
  [--verbose]
```

### Required Arguments

- `--codebase`: Path to the root directory of the codebase to analyze
- `--output`: Directory where reports and diagrams will be generated
- `--project-name`: Name of the project (used in report titles and filenames)

### Optional Arguments

- `--no-diagrams`: Skip C4 diagram generation (faster analysis)
- `--verbose`: Enable verbose logging for debugging

## Examples

### Example 1: Analyze Spring Modulith

```bash
cd /workspace/tools

python -m src.utils.report_generator analyze \
  --codebase /workspace/data/codebase/spring-modulith \
  --output /workspace \
  --project-name spring-modulith
```

**Generates:**
- `/workspace/spring-modulith_ANALYSIS_REPORT.md` (Markdown report)
- `/workspace/spring-modulith_analysis.json` (JSON data)
- `/workspace/diagrams/spring-modulith_context.puml` (C4 Context diagram)
- `/workspace/diagrams/spring-modulith_container.puml` (C4 Container diagram)
- `/workspace/diagrams/spring-modulith_component.puml` (C4 Component diagram)
- `/workspace/diagrams/spring-modulith-{module}_classes.puml` (C4 Code diagrams)

### Example 2: Analysis with Verbose Output

```bash
python -m src.utils.report_generator analyze \
  --codebase /workspace/data/codebase/spring-modulith \
  --output /workspace \
  --project-name spring-modulith \
  --verbose
```

### Example 3: Skip Diagram Generation

```bash
python -m src.utils.report_generator analyze \
  --codebase /workspace/data/codebase/spring-modulith \
  --output /workspace \
  --project-name spring-modulith \
  --no-diagrams
```

## Output Files

### Markdown Report

**Filename:** `{project-name}_ANALYSIS_REPORT.md`

**Contents:**
1. **Executive Summary**: High-level metrics and key findings
2. **C4 Architecture Diagrams**: Embedded PlantUML diagrams
   - Context Diagram (Level 1)
   - Container Diagram (Level 2)
   - Component Diagram (Level 3)
   - Code Diagrams (Level 4)
3. **Quantitative Analysis**: Detailed metrics tables
4. **Module Analysis**: Per-module breakdowns
5. **Dependency Analysis**: External dependency classification
6. **Migration Readiness Assessment**: Complexity scoring and recommendations
7. **Next Steps**: Suggested follow-up actions

### JSON Data Export

**Filename:** `{project-name}_analysis.json`

**Structure:**
```json
{
  "metadata": {
    "project_name": "spring-modulith",
    "analysis_date": "2025-11-19T00:50:54.048Z",
    "codebase_path": "/workspace/data/codebase/spring-modulith",
    "tool_version": "1.0.0"
  },
  "metrics": {
    "total_modules": 11,
    "total_classes": 106,
    "total_methods": 671,
    "total_fields": 198,
    "total_packages": 27
  },
  "modules": {
    "spring-modulith-core": {
      "classes": 39,
      "methods": 428,
      "fields": 91,
      "packages": 5
    }
    // ... more modules
  },
  "dependencies": {
    "count": 460,
    "nodes": [ /* dependency nodes */ ],
    "edges": [ /* dependency relationships */ ]
  }
}
```

### PlantUML Diagrams

All diagrams are generated in the `diagrams/` subdirectory of the output path.

#### C4 Context Diagram (Level 1)

**File:** `{project-name}_context.puml`

Shows the system landscape with:
- End users (Developer, Architect, End User)
- The system being analyzed
- External systems (Database, External APIs)
- High-level relationships

#### C4 Container Diagram (Level 2)

**File:** `{project-name}_container.puml`

Shows module-level architecture:
- All discovered modules as containers
- Module boundaries
- Inter-module dependencies
- Database and external system connections

#### C4 Component Diagram (Level 3)

**File:** `{project-name}_component.puml`

Shows detailed component view:
- Focuses on the largest module (typically the core module)
- Top 10 packages as components
- Component relationships

#### C4 Code Diagrams (Level 4)

**Files:** `{module-name}_classes.puml`

Class-level diagrams for top 3 largest modules:
- Top 25 classes per module
- Method and field counts
- Class characteristics

## Rendering PlantUML Diagrams

### Option 1: Command Line (Local)

```bash
# Install PlantUML
sudo apt-get install plantuml

# Render single diagram
plantuml /workspace/diagrams/spring-modulith_context.puml

# Render all diagrams
plantuml /workspace/diagrams/*.puml

# Output: PNG images created in same directory
```

### Option 2: Online Renderer

1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy contents of `.puml` file
3. Paste into text box
4. View rendered diagram
5. Download as PNG/SVG

### Option 3: VS Code Extension

1. Install PlantUML extension in VS Code
2. Open `.puml` file
3. Press `Alt+D` to preview
4. Right-click → "Export Current Diagram"

## Codebase Requirements

### Supported Project Structures

The report generator works best with:

1. **Multi-module Spring Boot projects**
   ```
   /project-root
   ├── module-1/
   │   └── src/main/java/
   ├── module-2/
   │   └── src/main/java/
   └── module-n/
       └── src/main/java/
   ```

2. **Single-module Spring Boot projects**
   ```
   /project-root
   └── src/main/java/
   ```

### Module Discovery

The tool automatically discovers modules by:
- Scanning for directories containing `src/main/java/`
- Excluding common non-module directories (`.git`, `target`, `build`, `node_modules`, `etc`, `docs`)
- Analyzing each discovered module independently

### Java Version Support

- **Minimum:** Java 8
- **Recommended:** Java 17+
- **Supported:** Java 21 (latest LTS)

Uses tree-sitter-java 0.23.5 which supports:
- Records (Java 14+)
- Pattern matching (Java 16+)
- Sealed classes (Java 17+)
- Text blocks and modern syntax

## Configuration

### ReportConfiguration Dataclass

For programmatic usage, configure the generator with:

```python
from pathlib import Path
from src.utils.report_generator import ReportConfiguration, ReportGenerator

config = ReportConfiguration(
    codebase_path=Path("/workspace/data/codebase/spring-modulith"),
    output_dir=Path("/workspace"),
    project_name="spring-modulith",
    generate_diagrams=True,
    diagram_formats=["puml"],
    include_test_code=False,
    max_depth=10,
    verbose=False
)

generator = ReportGenerator(config)
success = generator.run()
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `codebase_path` | Path | Required | Root directory of codebase |
| `output_dir` | Path | Required | Output directory for reports |
| `project_name` | str | Required | Project name for reports |
| `generate_diagrams` | bool | `True` | Generate C4 diagrams |
| `diagram_formats` | List[str] | `["puml"]` | Diagram formats (currently only PlantUML) |
| `include_test_code` | bool | `False` | Include test code in analysis |
| `max_depth` | int | `10` | Maximum directory traversal depth |
| `verbose` | bool | `False` | Enable verbose logging |

## Analysis Metrics

### Class-Level Metrics

- Total classes analyzed
- Methods per class (average, min, max)
- Fields per class (average, min, max)
- Class types (classes, interfaces, abstract classes)

### Package-Level Metrics

- Total packages discovered
- Classes per package
- Package depth and hierarchy

### Module-Level Metrics

- Modules discovered
- Classes per module
- Methods per module
- Fields per module
- Package count per module

### Dependency Metrics

- Total unique dependencies
- Dependency classification:
  - `spring-framework`: Spring Framework dependencies
  - `testing`: JUnit, AssertJ, testing frameworks
  - `architecture-testing`: ArchUnit, architecture validation
  - `json-processing`: JSON libraries
  - `jdk`: Java standard library
  - `external`: Other third-party dependencies

## Migration Readiness Assessment

### Complexity Scoring

| Complexity | Criteria |
|------------|----------|
| **Low** | < 50 classes |
| **Medium** | 50-200 classes |
| **High** | > 200 classes |

### Assessment Factors

1. **Modularity**: Number of distinct modules
2. **Size**: Total class count
3. **Dependencies**: External dependency count
4. **Package Organization**: Package structure clarity

### Recommendations

The report provides:
- **Strengths**: Positive architectural characteristics
- **Considerations**: Migration challenges to address
- **Recommended Approach**: Phased migration strategy

## Troubleshooting

### Issue: "No modules were successfully analyzed"

**Cause:** Codebase structure not recognized

**Solutions:**
1. Verify codebase path exists and contains Java source
2. Check for `src/main/java` directories
3. Use `--verbose` to see discovery process

### Issue: "ModuleNotFoundError" when running

**Cause:** Python module import issues

**Solutions:**
```bash
# Ensure you're in the tools directory
cd /workspace/tools

# Run with module syntax
python -m src.utils.report_generator analyze ...
```

### Issue: PlantUML diagrams won't render

**Cause:** PlantUML syntax or renderer issues

**Solutions:**
1. Verify `.puml` file exists and is not empty
2. Try online renderer first
3. Check PlantUML installation: `plantuml -version`
4. Ensure C4-PlantUML stdlib is accessible online

### Issue: Analysis takes too long

**Causes:** Large codebase or verbose logging

**Solutions:**
1. Remove `--verbose` flag
2. Use `--no-diagrams` for faster analysis
3. Analyze smaller module subsets
4. Monitor progress with standard logging

## Integration with Omega System

### Manual Analysis Workflow

```bash
# Step 1: Generate report
python -m src.utils.report_generator analyze \
  --codebase /workspace/data/codebase/spring-modulith \
  --output /workspace \
  --project-name spring-modulith

# Step 2: Review report
cat /workspace/spring-modulith_ANALYSIS_REPORT.md

# Step 3: Render diagrams
plantuml /workspace/diagrams/*.puml

# Step 4: Query JSON data
jq '.metrics' /workspace/spring-modulith_analysis.json
```

### Future Integrations

Planned integrations (not yet implemented):

- **CodeQL Integration**: Security vulnerability scanning
- **Microsoft AppCAT**: Azure migration assessment
- **Runtime Analysis**: Integration with SigNoz data
- **Gap Analysis**: Static vs runtime comparison
- **Risk Scoring**: Automated migration risk assessment

## Project Standards Compliance

### Reproducibility

- All dependencies pinned in `pyproject.toml`
- No ad-hoc installations required
- Scripted execution via module syntax
- Version-controlled configuration

### Professional Communication

- Zero emojis in output (strict policy compliance)
- Professional, technical language
- Structured reporting format
- Clear, actionable recommendations

### Documentation Standards

- Comprehensive usage examples
- Troubleshooting guides
- Configuration reference
- Integration workflows

## Performance Characteristics

### Analysis Speed

- **Small codebase** (< 50 classes): < 10 seconds
- **Medium codebase** (50-200 classes): 10-30 seconds
- **Large codebase** (> 200 classes): 30-60 seconds

Measured on Spring Modulith (106 classes): ~10 seconds

### Resource Usage

- **Memory**: < 500 MB for most codebases
- **Disk**: Reports typically < 1 MB (excluding diagrams)
- **CPU**: Single-threaded analysis

## Version History

### v1.0.0 (2025-11-19)

- Initial release
- C4 diagram generation (all 4 levels)
- Static code analysis with tree-sitter-java
- Dependency graph extraction
- Module discovery and analysis
- Markdown and JSON export
- Migration readiness assessment

## Related Documentation

- **Java Parser**: `/workspace/docs/setup/java-parser-setup.md`
- **C4 Model**: https://c4model.com/
- **PlantUML**: https://plantuml.com/
- **tree-sitter-java**: https://github.com/tree-sitter/tree-sitter-java

## Support

For issues or questions:

1. Check this documentation
2. Review Troubleshooting section
3. See `/workspace/.github/copilot-instructions.md` for project policies
4. Consult `/workspace/docs/omega-constitution.md` for standards
