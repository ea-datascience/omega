#!/bin/bash
#
# Context Mapper Installation Script
# Installs Context Mapper Java libraries in a reproducible way with pinned versions
#
# Usage: ./install-context-mapper.sh
#
# Follows Omega Constitution principles:
# - Pinned versions (context-mapper-dsl: 6.12.0, context-map-discovery: 1.1.0)
# - Reproducible installation
# - Maven-based dependency management
# - Verification included
#

set -e  # Exit on error

# Pinned versions
CONTEXT_MAPPER_DSL_VERSION="6.12.0"
CONTEXT_MAP_DISCOVERY_VERSION="1.1.0"
MAVEN_LOCAL_REPO="${HOME}/.m2/repository"

echo "Installing Context Mapper libraries..."
echo "  - context-mapper-dsl: ${CONTEXT_MAPPER_DSL_VERSION}"
echo "  - context-map-discovery: ${CONTEXT_MAP_DISCOVERY_VERSION}"

# Ensure Maven is available
if ! command -v mvn &> /dev/null; then
    echo "ERROR: Maven is not installed. Please run install-maven.sh first."
    exit 1
fi

# Create a temporary Maven project to download dependencies
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "Creating temporary Maven project..."
cat > pom.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>org.omega.temp</groupId>
    <artifactId>context-mapper-installer</artifactId>
    <version>1.0.0</version>
    
    <dependencies>
        <!-- Context Mapper DSL -->
        <dependency>
            <groupId>org.contextmapper</groupId>
            <artifactId>context-mapper-dsl</artifactId>
            <version>${CONTEXT_MAPPER_DSL_VERSION}</version>
        </dependency>
        
        <!-- Context Map Discovery -->
        <dependency>
            <groupId>org.contextmapper</groupId>
            <artifactId>context-map-discovery</artifactId>
            <version>${CONTEXT_MAP_DISCOVERY_VERSION}</version>
        </dependency>
    </dependencies>
</project>
EOF

echo "Downloading Context Mapper libraries and dependencies..."
mvn dependency:resolve

echo "Copying dependencies to local repository..."
mvn dependency:copy-dependencies -DoutputDirectory="${MAVEN_LOCAL_REPO}"

# Verify installation
echo "Verifying installation..."
DSL_JAR="${MAVEN_LOCAL_REPO}/org/contextmapper/context-mapper-dsl/${CONTEXT_MAPPER_DSL_VERSION}/context-mapper-dsl-${CONTEXT_MAPPER_DSL_VERSION}.jar"
DISCOVERY_JAR="${MAVEN_LOCAL_REPO}/org/contextmapper/context-map-discovery/${CONTEXT_MAP_DISCOVERY_VERSION}/context-map-discovery-${CONTEXT_MAP_DISCOVERY_VERSION}.jar"

if [ -f "$DSL_JAR" ]; then
    echo "✓ context-mapper-dsl ${CONTEXT_MAPPER_DSL_VERSION} installed"
    echo "  Location: $DSL_JAR"
else
    echo "✗ context-mapper-dsl installation failed"
    cd /
    rm -rf "$TEMP_DIR"
    exit 1
fi

if [ -f "$DISCOVERY_JAR" ]; then
    echo "✓ context-map-discovery ${CONTEXT_MAP_DISCOVERY_VERSION} installed"
    echo "  Location: $DISCOVERY_JAR"
else
    echo "✗ context-map-discovery installation failed"
    cd /
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "Context Mapper installation complete!"
echo ""
echo "To use Context Mapper in your Java project, add to your pom.xml:"
echo ""
cat <<'EOF'
<dependencies>
    <dependency>
        <groupId>org.contextmapper</groupId>
        <artifactId>context-mapper-dsl</artifactId>
        <version>6.12.0</version>
    </dependency>
    <dependency>
        <groupId>org.contextmapper</groupId>
        <artifactId>context-map-discovery</artifactId>
        <version>1.1.0</version>
    </dependency>
</dependencies>
EOF

echo ""
echo "Or to verify from command line:"
echo "  ls -lh ${MAVEN_LOCAL_REPO}/org/contextmapper/"
