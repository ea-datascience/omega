# Java Setup for Omega Project

This guide covers installing and configuring Java for the Omega project.

## Quick Installation

For development in the Omega dev container:

```bash
cd /workspace/tools/src
chmod +x install-java.sh
./install-java.sh
```

This installs OpenJDK 17 and configures JAVA_HOME automatically.

## Manual Installation

### Ubuntu/Debian (including dev container)

```bash
# Update package list
sudo apt-get update

# Install OpenJDK 17
sudo apt-get install -y openjdk-17-jdk openjdk-17-jre

# Verify installation
java -version
```

### macOS (via Homebrew)

```bash
# Install OpenJDK 17
brew install openjdk@17

# Link it
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-17.jdk

# Verify installation
java -version
```

### Windows

1. Download Eclipse Temurin JDK 17:
   https://adoptium.net/temurin/releases/?version=17

2. Run the installer and follow the prompts

3. Verify in Command Prompt:
   ```cmd
   java -version
   ```

## Configure JAVA_HOME

After installation, set JAVA_HOME environment variable:

### Linux/macOS

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

Find your Java installation path:
```bash
readlink -f $(which java) | sed 's|/bin/java||'
```

Then reload:
```bash
source ~/.bashrc
```

### Windows

1. Open System Properties > Environment Variables
2. Add new System Variable:
   - Name: `JAVA_HOME`
   - Value: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x.x-hotspot`
3. Add to Path: `%JAVA_HOME%\bin`

## Verify Java Setup

Use the Omega Java utilities to verify your setup:

```bash
cd /workspace/tools
python -m src.utils.java_utils
```

Expected output:
```
============================================================
Java Environment Information
============================================================
Java Home:       /usr/lib/jvm/java-17-openjdk-amd64
Java Executable: /usr/lib/jvm/java-17-openjdk-amd64/bin/java
Java Version:    17.0.2
Major Version:   17
Vendor:          OpenJDK
Valid:           True
Maven:           Not found
Gradle:          Not found
============================================================

Environment is valid and ready!
```

## Install Build Tools (Optional)

### Maven

```bash
# Ubuntu/Debian
sudo apt-get install -y maven

# macOS
brew install maven

# Verify
mvn -version
```

### Gradle

```bash
# Ubuntu/Debian
sudo apt-get install -y gradle

# macOS
brew install gradle

# Verify
gradle --version
```

## Using Java Utilities in Code

Once Java is installed, you can use the utilities in your Python code:

```python
from utils.java_utils import require_java, JavaEnvironmentManager

# Validate Java is available
env = require_java()
print(f"Using Java {env.version} at {env.java_executable}")

# Run Java commands
manager = JavaEnvironmentManager()
java_cmd = manager.get_java_command(['-version'])

import subprocess
subprocess.run(java_cmd)
```

## Troubleshooting

### "Java executable not found"

Solution:
1. Install Java 17+ using the instructions above
2. Ensure `java` is on your PATH: `which java`
3. Set JAVA_HOME if not automatically detected

### "Java 17+ required. Found Java 8/11"

Solution:
1. Update to Java 17 or later
2. If multiple versions installed, set JAVA_HOME to Java 17 location
3. Verify with `java -version`

### "Maven not found"

This is a warning, not an error. Maven is optional but recommended:
- Install Maven using instructions above
- Or use Maven Wrapper (mvnw) in project directories

### Permission Denied

If you get permission errors:
```bash
# Make install script executable
chmod +x /workspace/tools/src/install-java.sh

# Run with appropriate permissions
./install-java.sh
```

## Development Container Setup

To add Java to the dev container permanently:

1. **Option A: Update Dockerfile** (recommended for permanent setup)

   Edit `/workspace/.devcontainer/Dockerfile`:
   ```dockerfile
   # Add after existing RUN commands
   RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
       && apt-get -y install --no-install-recommends \
           openjdk-17-jdk \
           openjdk-17-jre \
           maven \
       && apt-get clean -y && rm -rf /var/lib/apt/lists/*
   
   # Set JAVA_HOME
   ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
   ENV PATH=$JAVA_HOME/bin:$PATH
   ```

   Rebuild container: `Dev Containers: Rebuild Container`

2. **Option B: Post-Create Command** (for temporary/testing)

   Edit `/workspace/.devcontainer/devcontainer.json`:
   ```json
   "postCreateCommand": "bash /workspace/tools/src/install-java.sh && uv python install 3.12 && uv venv .venv --python 3.12"
   ```

3. **Option C: Manual Installation** (current session only)

   Run install script manually:
   ```bash
   cd /workspace/tools/src
   ./install-java.sh
   source ~/.bashrc
   ```

## System Requirements

- **Java Version**: 17 or later (LTS recommended)
- **Disk Space**: ~300-500 MB for JDK
- **Memory**: 512 MB minimum (2 GB recommended for builds)
- **OS**: Ubuntu 22.04, macOS 11+, Windows 10+

## Supported Distributions

Tested and supported Java distributions:

- **Eclipse Temurin** (recommended): https://adoptium.net/
- **Oracle JDK**: https://www.oracle.com/java/technologies/downloads/
- **OpenJDK**: Pre-installed on most Linux distributions
- **Azul Zulu**: https://www.azul.com/downloads/
- **Amazon Corretto**: https://aws.amazon.com/corretto/

All distributions are compatible with Omega's Java utilities.

## Next Steps

After installing Java:

1. Verify setup: `python -m src.utils.java_utils`
2. Run integration tests: `pytest tests/integration/test_static_analysis_integration.py -v`
3. Analyze Spring Modulith codebase: Start with static analysis tools

## Additional Resources

- OpenJDK Documentation: https://openjdk.org/
- Eclipse Temurin Installation: https://adoptium.net/installation/
- Java Version Management: https://sdkman.io/
- Maven Documentation: https://maven.apache.org/guides/
- Gradle Documentation: https://docs.gradle.org/
