# Omega Utils

Common utilities for Omega project development and analysis.

## Java Utilities

The `java_utils` module provides consistent Java environment management for all developers and tools.

### Features

- **Automatic Java Detection**: Finds Java from JAVA_HOME or PATH
- **Version Validation**: Ensures Java 17+ is available
- **Build Tool Detection**: Locates Maven and Gradle executables
- **Environment Management**: Provides consistent Java configuration
- **Error Handling**: Clear error messages for setup issues

### Quick Start

#### Check Java Environment

```python
from utils.java_utils import get_java_environment, validate_java_setup

# Validate Java setup
is_valid, issues = validate_java_setup()
if not is_valid:
    for issue in issues:
        print(f"Issue: {issue}")

# Get environment details
env = get_java_environment()
print(f"Java {env.major_version} at {env.java_executable}")
```

#### Require Java in Your Code

```python
from utils.java_utils import require_java

def analyze_java_project():
    # This will raise JavaSetupError if Java is not valid
    env = require_java()
    
    # Continue with Java operations
    print(f"Using Java {env.version}")
```

#### Run Java Commands

```python
from utils.java_utils import JavaEnvironmentManager
import subprocess

manager = JavaEnvironmentManager()

# Run Java command
java_cmd = manager.get_java_command(['-version'])
subprocess.run(java_cmd)

# Run Maven command
maven_cmd = manager.get_maven_command(['clean', 'install'])
subprocess.run(maven_cmd, cwd='/path/to/project')

# Run Gradle command
gradle_cmd = manager.get_gradle_command(['build'])
subprocess.run(gradle_cmd, cwd='/path/to/project')
```

#### Environment Variables for Subprocesses

```python
from utils.java_utils import JavaEnvironmentManager
import subprocess

manager = JavaEnvironmentManager()

# Get environment with JAVA_HOME set
env_vars = manager.setup_environment_variables()

# Run subprocess with proper Java environment
subprocess.run(['some-tool'], env=env_vars)
```

### Command-Line Usage

Check your Java environment from the command line:

```bash
cd /workspace/tools
python -m src.utils.java_utils
```

Output:
```
============================================================
Java Environment Information
============================================================
Java Home:       /usr/local/openjdk-17
Java Executable: /usr/local/openjdk-17/bin/java
Java Version:    17.0.2
Major Version:   17
Vendor:          OpenJDK
Valid:           True
Maven:           Not found
Gradle:          Not found
============================================================

Environment is valid and ready!
```

### Integration with Analysis Tools

The Java utilities are designed to integrate seamlessly with Omega's static analysis tools:

```python
from utils.java_utils import require_java, JavaEnvironmentManager
from omega_analysis.analysis.static.java_parser import JavaSourceAnalyzer

def setup_java_analyzer():
    # Validate Java environment first
    env = require_java()
    
    # Create analyzer with validated environment
    analyzer = JavaSourceAnalyzer(
        java_home=env.java_home,
        java_version=env.major_version
    )
    
    return analyzer
```

### Error Handling

The module provides a `JavaSetupError` exception for all Java-related setup failures:

```python
from utils.java_utils import JavaSetupError, get_java_environment

try:
    env = get_java_environment()
except JavaSetupError as e:
    print(f"Java setup failed: {e}")
    print("Please install Java 17+ or set JAVA_HOME environment variable")
```

### Requirements

- **Java 17+**: Required for Spring Boot 3.x and modern Java features
- **Maven or Gradle**: Recommended for build tool integration (optional)

### Installation Guidance

If Java is not detected, developers should:

1. **Install Java 17 or later**:
   - OpenJDK: https://adoptium.net/
   - Oracle JDK: https://www.oracle.com/java/technologies/downloads/

2. **Set JAVA_HOME** (optional but recommended):
   ```bash
   export JAVA_HOME=/path/to/java
   export PATH=$JAVA_HOME/bin:$PATH
   ```

3. **Verify installation**:
   ```bash
   java -version
   python -m src.utils.java_utils
   ```

### Dev Container Support

The Omega dev container includes Java 17+ pre-installed and configured. No additional setup is needed when using the dev container.

### Testing

Unit tests for Java utilities:

```bash
cd /workspace/tools
pytest tests/unit/test_java_utils.py -v
```

Integration tests with real Java environments:

```bash
cd /workspace/tools
pytest tests/integration/test_java_integration.py -v
```

### API Reference

#### JavaEnvironment

Dataclass representing detected Java configuration:

- `java_home`: Path to JAVA_HOME (may be None)
- `java_executable`: Path to java executable
- `version`: Full version string (e.g., "17.0.2")
- `major_version`: Major version number (e.g., 17)
- `vendor`: Vendor name (e.g., "OpenJDK")
- `is_valid`: Whether environment meets minimum requirements
- `maven_executable`: Path to Maven (may be None)
- `gradle_executable`: Path to Gradle (may be None)

#### JavaEnvironmentManager

Main class for Java environment management:

- `detect_java_environment()`: Detect and validate Java environment
- `validate_environment()`: Check if environment is valid
- `get_java_command(args)`: Build Java command with arguments
- `get_maven_command(goals)`: Build Maven command with goals
- `get_gradle_command(tasks)`: Build Gradle command with tasks
- `setup_environment_variables()`: Get env vars dict with JAVA_HOME
- `print_environment_info()`: Print detailed environment information

#### Convenience Functions

- `get_java_environment()`: Get current Java environment (cached)
- `validate_java_setup()`: Validate Java setup and get issues
- `require_java()`: Require valid Java or raise exception

### Configuration

The minimum Java version is set to 17. This can be adjusted in the `JavaEnvironmentManager` class:

```python
class JavaEnvironmentManager:
    MINIMUM_JAVA_VERSION = 17  # Change if needed
```

### Troubleshooting

**Issue: "Java executable not found"**
- Install Java 17+ or set JAVA_HOME environment variable
- Verify java is on PATH: `which java`

**Issue: "Java 17+ required. Found Java 8"**
- Update Java to version 17 or later
- Ensure JAVA_HOME points to correct Java version

**Issue: "Maven not found"**
- This is a warning, not an error
- Install Maven if you need to analyze Maven projects
- Use Maven Wrapper (mvnw) in project directories

**Issue: "Could not parse Java version"**
- Unusual Java distribution format
- File an issue with output of `java -version`

### Future Enhancements

Planned improvements for java_utils:

- Support for multiple Java installations (version switching)
- Integration with SDKMAN for Java version management
- Automatic Java download and installation (optional)
- Classpath analysis and management utilities
- Java module system (JPMS) support
- GraalVM native-image detection and support
