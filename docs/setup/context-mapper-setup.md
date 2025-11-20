# Context Mapper Installation and Usage Guide

## Overview

Context Mapper is a Domain-Driven Design (DDD) tool that provides:
- Context Map discovery from Spring Boot applications
- Bounded Context identification
- Relationship mapping
- CML (Context Mapping Language) generation
- Architecture visualization

This guide covers installation, configuration, and usage of Context Mapper within the Omega project.

**Analysis Modes:**
1. **Reflection-based Discovery**: Uses Context Mapper's Java libraries (requires compiled .class files)
2. **Source Code Analysis**: Uses Spring Boot Analyzer (works with source code only, no compilation needed)

## Prerequisites

- **Java 17+**: OpenJDK 17 or later (automatically installed in dev container)
- **Maven 3.9.9+**: For dependency management (install script provided)
- **Python 3.12+**: For Python integration wrapper

## Installation

### Step 1: Install Maven (if not already installed)

```bash
cd /workspace/tools/src/utils
chmod +x install-maven.sh
./install-maven.sh
source /etc/profile.d/maven.sh
```

**What this does:**
- Downloads Apache Maven 3.9.9 (pinned version)
- Installs to `/opt/maven`
- Configures environment variables
- Verifies installation

**Verification:**
```bash
mvn --version
# Should show: Apache Maven 3.9.9
```

### Step 2: Install Context Mapper Libraries

```bash
cd /workspace/tools/src/utils
chmod +x install-context-mapper.sh
./install-context-mapper.sh
```

**What this does:**
- Downloads Context Mapper DSL 6.12.0
- Downloads Context Map Discovery 1.1.0
- Installs all transitive dependencies to Maven local repository (`~/.m2/repository`)
- Verifies JARs are correctly installed

**Verification:**
```bash
ls -lh ~/.m2/repository/org/contextmapper/
# Should show:
#   context-mapper-dsl/6.12.0/context-mapper-dsl-6.12.0.jar
#   context-map-discovery/1.1.0/context-map-discovery-1.1.0.jar
```

### Step 3: Verify Python Integration

```bash
cd /workspace/tools
python -m src.utils.context_mapper
```

**Expected output:**
```
Context Mapper Integration
============================================================
Context Mapper DSL: 6.12.0
Context Map Discovery: 1.1.0
Java Version: 17.0.16
Maven Repository: /home/vscode/.m2/repository
============================================================

Context Mapper is ready to use!
```

## Library Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| `context-mapper-dsl` | 6.12.0 | Core Context Mapping DSL |
| `context-map-discovery` | 1.1.0 | Reverse engineering & discovery |
| Maven | 3.9.9 | Dependency management |
| Java | 17+ | Runtime environment |

These versions are **pinned** for reproducibility across all developers and environments.

## Usage

### Python API

Omega provides two methods for analyzing Spring Boot applications:

#### Method 1: Source Code Analysis (Recommended)

**Advantages:**
- No compilation required
- Works with any Spring Boot project
- Fast and lightweight
- Analyzes source code structure directly

```python
from src.utils.context_mapper import ContextMapper
from pathlib import Path

# Initialize Context Mapper
mapper = ContextMapper()

# Analyze Spring Boot project from source code
result = mapper.analyze_spring_boot_source(
    project_path=Path("/path/to/spring-boot-app"),
    base_package="com.example.app",
    output_dir=Path("/workspace/diagrams")
)

# Access discovered modules
print(f"Application: {result['application']}")
print(f"Discovered {len(result['modules'])} modules:")
for module in result['modules']:
    print(f"  - {module['name']}")
    print(f"    Services: {len(module['services'])}")
    print(f"    Entities: {len(module['entities'])}")

# Access dependencies
print(f"\nInter-module dependencies:")
for dep in result['dependencies']:
    print(f"  {dep['from']} -> {dep['to']}")

# Output files
print(f"\nCML file: {result['cml_file']}")
print(f"JSON report: {result['json_file']}")
```

#### Method 2: Reflection-based Discovery (Requires Compilation)

**Requirements:**
- Project must be compiled (`mvn compile`)
- All dependencies on classpath
- @SpringBootApplication annotations in compiled classes

**Note:** This method uses Java reflection and may not find contexts if dependencies are missing.

```python
from src.utils.context_mapper import ContextMapper
from pathlib import Path

# Initialize Context Mapper
mapper = ContextMapper()

# Discover bounded contexts from COMPILED Spring Boot application
# (Requires mvn compile to have been run)
result = mapper.discover_spring_boot_contexts(
    codebase_path=Path("/path/to/spring-boot-app"),
    base_package="com.example.app"
)

# Access discovered contexts
print(f"Discovered {len(result['bounded_contexts'])} bounded contexts:")
for bc in result['bounded_contexts']:
    print(f"  - {bc['name']}")

# Access relationships
print(f"\nDiscovered {len(result['relationships'])} relationships:")
for rel in result['relationships']:
    print(f"  {rel['from']} -> {rel['to']}")

# Get CML output file
cml_file = result['cml_file']
print(f"\nCML output written to: {cml_file}")
```

#### Direct Spring Boot Analyzer Usage

For more control, use the Spring Boot Analyzer directly:

```python
from src.utils.spring_boot_analyzer import SpringBootAnalyzer
from pathlib import Path

analyzer = SpringBootAnalyzer()

# Analyze project
result = analyzer.analyze_project(
    project_path=Path("/path/to/spring-boot-app"),
    base_package="com.example.app"
)

# Print summary to console
analyzer.print_summary(result)

# Generate outputs
analyzer.generate_cml(result, Path("/workspace/diagrams/output.cml"))
analyzer.generate_json_report(result, Path("/workspace/diagrams/output.json"))
```

#### Basic Usage (Legacy - Reflection-based)

```python
from src.utils.context_mapper import ContextMapper
from pathlib import Path

# Initialize Context Mapper
mapper = ContextMapper()

# Discover bounded contexts from Spring Boot application
result = mapper.discover_spring_boot_contexts(
    codebase_path=Path("/path/to/spring-boot-app"),
    base_package="com.example.app"
)

# Access discovered contexts
print(f"Discovered {len(result['bounded_contexts'])} bounded contexts:")
for bc in result['bounded_contexts']:
    print(f"  - {bc['name']}")

# Access relationships
print(f"\nDiscovered {len(result['relationships'])} relationships:")
for rel in result['relationships']:
    print(f"  {rel['from']} -> {rel['to']}")

# Get CML output file
cml_file = result['cml_file']
print(f"\nCML output written to: {cml_file}")
```

#### With Custom Output Directory

```python
from src.utils.context_mapper import ContextMapper
from pathlib import Path

mapper = ContextMapper()

# Specify output directory
output_dir = Path("/workspace/analysis/context-maps")
output_dir.mkdir(parents=True, exist_ok=True)

result = mapper.discover_spring_boot_contexts(
    codebase_path=Path("/workspace/data/codebase/spring-modulith"),
    base_package="de.springmodulith",
    output_dir=output_dir
)
```

#### Error Handling

```python
from src.utils.context_mapper import ContextMapper, ContextMapperError

try:
    mapper = ContextMapper()
    result = mapper.discover_spring_boot_contexts(
        codebase_path=Path("/path/to/app"),
        base_package="com.example"
    )
except ContextMapperError as e:
    print(f"Context Mapper error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Get Version Information

```python
from src.utils.context_mapper import ContextMapper

mapper = ContextMapper()
info = mapper.get_version_info()

print(f"Context Mapper DSL: {info['context_mapper_dsl']}")
print(f"Context Map Discovery: {info['context_map_discovery']}")
print(f"Java Version: {info['java_version']}")
print(f"Maven Repo: {info['maven_repo']}")
```

### Command-Line Interface

#### Spring Boot Analyzer CLI

Analyze any Spring Boot project from the command line:

```bash
cd /workspace/tools

# Analyze Spring Boot project
python -m src.utils.spring_boot_analyzer \
  /path/to/spring-boot-app \
  com.example.app \
  /workspace/diagrams

# Example: Analyze Spring Modulith example
python -m src.utils.spring_boot_analyzer \
  /workspace/data/codebase/spring-modulith/spring-modulith-examples/spring-modulith-example-full \
  example \
  /workspace/diagrams
```

**Output:**
- Console summary of modules and dependencies
- CML file: `<project-name>_context_map.cml`
- JSON report: `<project-name>_analysis.json`

#### Context Mapper Status Check

Check Context Mapper status:

```bash
cd /workspace/tools
python -m src.utils.context_mapper
```

## Architecture

### Components

1. **ContextMapper Python Class** (`src/utils/context_mapper.py`)
   - High-level Python API
   - Wraps Java library calls
   - Handles code generation and compilation
   - Parses CML output
   - Integrates Spring Boot Analyzer

2. **SpringBootAnalyzer Python Class** (`src/utils/spring_boot_analyzer.py`)
   - Source code analysis (no compilation required)
   - Module/package structure detection
   - Service, Entity, Repository, Controller classification
   - Inter-module dependency detection
   - CML and JSON generation
   - CLI interface

3. **Context Mapper Java Libraries**
   - `context-mapper-dsl`: Core DSL and model
   - `context-map-discovery`: Discovery strategies

3. **JavaEnvironmentManager**
   - Detects and validates Java installation
   - Manages JAVA_HOME
   - Builds classpaths

### Discovery Flow

```
Python API Call
    ↓
Generate Java Discovery Code
    ↓
Compile Java Code (javac)
    ↓
Execute Java Discovery (java)
    ↓
Context Mapper Library
    ↓
Parse Codebase (Spring Boot)
    ↓
Generate CML Output
    ↓
Parse CML in Python
    ↓
Return Results
```

### Data Flow

```
Spring Boot Source Code
    ↓
[Context Mapper Discovery]
    ↓
CML File (Context Mapping Language)
    ↓
[Python Parser]
    ↓
Python Dict:
{
  "bounded_contexts": [...],
  "relationships": [...],
  "cml_file": "path/to/output.cml",
  "raw_cml": "..."
}
```

## Testing

### Run Unit Tests

```bash
cd /workspace/tools
python -m pytest tests/unit/test_context_mapper.py -v
```

**Coverage:**
- Initialization and validation
- Version information retrieval
- Java code generation
- Classpath building
- CML parsing
- Error handling

### Run Integration Tests

```bash
cd /workspace/tools
python -m pytest tests/integration/test_context_mapper_integration.py -v
```

**Tests:**
- Real Context Mapper library interaction
- JAR file verification
- Java compilation and execution
- Sample Spring Boot codebase analysis

### Run All Tests

```bash
cd /workspace/tools
python -m pytest tests/ -v --cov=src/utils/context_mapper
```

## Troubleshooting

### Java Not Found

**Error:**
```
ContextMapperError: Failed to detect Java environment
```

**Solution:**
```bash
# Check Java installation
java -version

# If not installed, Java 17 should be in dev container
# Verify JAVA_HOME
echo $JAVA_HOME

# Set JAVA_HOME if needed
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
```

### Context Mapper JARs Not Found

**Error:**
```
ContextMapperError: Context Mapper DSL 6.12.0 not found
```

**Solution:**
```bash
# Re-run installation script
cd /workspace/tools/src/utils
./install-context-mapper.sh

# Verify JARs exist
ls -lh ~/.m2/repository/org/contextmapper/context-mapper-dsl/6.12.0/
ls -lh ~/.m2/repository/org/contextmapper/context-map-discovery/1.1.0/
```

### Maven Not Found

**Error:**
```
mvn: command not found
```

**Solution:**
```bash
# Install Maven
cd /workspace/tools/src/utils
./install-maven.sh
source /etc/profile.d/maven.sh

# Verify
mvn --version
```

### Java Compilation Errors

**Error:**
```
Java compilation failed
```

**Solution:**
1. Check Java version: `java -version` (must be 17+)
2. Verify Context Mapper JARs are installed
3. Check for syntax errors in generated code
4. Review error messages for missing dependencies

## Advanced Usage

### Custom Discovery Strategies

Context Mapper supports multiple discovery strategies. The Python wrapper currently implements:

- `SpringBootBoundedContextDiscoveryStrategy`: Discovers contexts from Spring Boot apps

Future strategies to implement:
- `DockerComposeRelationshipDiscoveryStrategy`: Derives relationships from docker-compose.yml
- Custom strategies based on your architecture

### CML Output Format

Example CML output:

```
ContextMap MySystem {
    contains PaymentContext
    contains OrderContext
    
    PaymentContext -> OrderContext
}

BoundedContext PaymentContext {
    implementationTechnology "Spring Boot"
    
    Aggregate PaymentAggregate {
        Entity Payment {
            String id
            BigDecimal amount
        }
    }
}

BoundedContext OrderContext {
    implementationTechnology "Spring Boot"
    
    Aggregate OrderAggregate {
        Entity Order {
            String id
            List<OrderItem> items
        }
    }
}
```

### Extending the Python Wrapper

To add new discovery strategies:

1. Create Java code generator method
2. Execute with `_run_java_discovery()`
3. Parse results with `_parse_cml_output()` or custom parser

Example:

```python
def discover_with_docker_compose(
    self,
    docker_compose_file: Path,
    ...
) -> Dict:
    java_code = self._generate_docker_compose_discovery_code(...)
    result = self._run_java_discovery(java_code)
    return self._parse_cml_output(...)
```

## References

- [Context Mapper Official Documentation](https://contextmapper.org/)
- [Context Mapper DSL Reference](https://contextmapper.org/docs/language-reference/)
- [Context Map Discovery Library](https://github.com/ContextMapper/context-map-discovery)
- [Omega Constitution](/workspace/docs/omega-constitution.md)

## Next Steps

After installing Context Mapper, you can:

1. Integrate with Spring Modulith analysis (see Epic 1.1)
2. Combine with other architectural analysis tools (Structurizr, CodeQL, AppCAT)
3. Extend discovery strategies for your specific architecture
4. Generate visualizations from CML output

## Support

For issues or questions:

1. Check this documentation
2. Review test files for usage examples
3. Consult Context Mapper documentation
4. Check Omega project issues
