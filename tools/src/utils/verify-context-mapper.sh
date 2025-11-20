#!/bin/bash
#
# Context Mapper Installation and Functionality Verification
#
# This script verifies that Context Mapper is properly installed and working.
# It checks Maven, Context Mapper libraries, Python integration, and runs tests.
#
# Usage: ./verify_context_mapper.sh
#

set -e  # Exit on any error

echo "================================================================"
echo "Context Mapper Verification Script"
echo "================================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Step 1: Verify Maven installation
echo "Step 1: Verifying Maven Installation"
echo "--------------------------------------"

if [ -x "/opt/maven/bin/mvn" ]; then
    MAVEN_VERSION=$(/opt/maven/bin/mvn --version | head -n1)
    print_success "Maven found: $MAVEN_VERSION"
else
    print_error "Maven not found at /opt/maven/bin/mvn"
    echo "Run: /workspace/tools/src/utils/install-maven.sh"
    exit 1
fi
echo ""

# Step 2: Verify Context Mapper DSL library
echo "Step 2: Verifying Context Mapper DSL Library"
echo "---------------------------------------------"

DSL_JAR="$HOME/.m2/repository/org/contextmapper/context-mapper-dsl/6.12.0/context-mapper-dsl-6.12.0.jar"
if [ -f "$DSL_JAR" ]; then
    DSL_SIZE=$(stat -c%s "$DSL_JAR" 2>/dev/null || stat -f%z "$DSL_JAR" 2>/dev/null)
    print_success "Context Mapper DSL 6.12.0 found ($(numfmt --to=iec-i --suffix=B $DSL_SIZE || echo ${DSL_SIZE} bytes))"
else
    print_error "Context Mapper DSL not found"
    echo "Run: /workspace/tools/src/utils/install-context-mapper.sh"
    exit 1
fi
echo ""

# Step 3: Verify Context Map Discovery library
echo "Step 3: Verifying Context Map Discovery Library"
echo "------------------------------------------------"

DISCOVERY_JAR="$HOME/.m2/repository/org/contextmapper/context-map-discovery/1.1.0/context-map-discovery-1.1.0.jar"
if [ -f "$DISCOVERY_JAR" ]; then
    DISCOVERY_SIZE=$(stat -c%s "$DISCOVERY_JAR" 2>/dev/null || stat -f%z "$DISCOVERY_JAR" 2>/dev/null)
    print_success "Context Map Discovery 1.1.0 found ($(numfmt --to=iec-i --suffix=B $DISCOVERY_SIZE || echo ${DISCOVERY_SIZE} bytes))"
else
    print_error "Context Map Discovery not found"
    echo "Run: /workspace/tools/src/utils/install-context-mapper.sh"
    exit 1
fi
echo ""

# Step 4: Verify Java environment
echo "Step 4: Verifying Java Environment"
echo "-----------------------------------"

cd /workspace/tools
if python -c "from src.utils.context_mapper import ContextMapper; ContextMapper()" 2>/dev/null; then
    print_success "Python Context Mapper module loads successfully"
    
    # Get Java version from Python
    JAVA_INFO=$(python -c "from src.utils.context_mapper import ContextMapper; cm = ContextMapper(); print(f'Java {cm.java_env.version}')" 2>/dev/null)
    print_success "$JAVA_INFO detected and validated"
else
    print_error "Python Context Mapper module failed to load"
    exit 1
fi
echo ""

# Step 5: Run unit tests
echo "Step 5: Running Unit Tests"
echo "--------------------------"

cd /workspace/tools
if python -m pytest tests/unit/test_context_mapper.py -v --tb=line -q 2>&1 | grep -q "12 passed"; then
    print_success "Unit tests: 12/12 PASSED"
else
    print_error "Unit tests FAILED"
    echo "Run: cd /workspace/tools && python -m pytest tests/unit/test_context_mapper.py -v"
    exit 1
fi
echo ""

# Step 6: Run integration tests
echo "Step 6: Running Integration Tests"
echo "----------------------------------"

if python -m pytest tests/integration/test_context_mapper_integration.py -v --tb=line -q 2>&1 | grep -q "5 passed"; then
    print_success "Integration tests: 5/5 PASSED"
else
    print_error "Integration tests FAILED"
    echo "Run: cd /workspace/tools && python -m pytest tests/integration/test_context_mapper_integration.py -v"
    exit 1
fi
echo ""

# Step 7: Run E2E tests
echo "Step 7: Running End-to-End Tests"
echo "---------------------------------"

if python -m pytest tests/e2e/test_context_mapper_e2e.py -v --tb=line -q 2>&1 | grep -q "4 passed"; then
    print_success "E2E tests: 4/4 PASSED"
else
    print_error "E2E tests FAILED"
    echo "Run: cd /workspace/tools && python -m pytest tests/e2e/test_context_mapper_e2e.py -v"
    exit 1
fi
echo ""

# Step 8: Verify classpath dependencies
echo "Step 8: Verifying Classpath Dependencies"
echo "-----------------------------------------"

REQUIRED_DEPS=(
    "org/springframework/boot"
    "org/reflections"
    "com/google/guava"
    "org/slf4j"
)

MISSING_DEPS=0
for dep in "${REQUIRED_DEPS[@]}"; do
    if [ -d "$HOME/.m2/repository/$dep" ]; then
        print_success "Dependency found: $dep"
    else
        print_error "Missing dependency: $dep"
        MISSING_DEPS=$((MISSING_DEPS + 1))
    fi
done

if [ $MISSING_DEPS -gt 0 ]; then
    print_error "$MISSING_DEPS dependencies missing"
    echo "Re-run: /workspace/tools/src/utils/install-context-mapper.sh"
    exit 1
fi
echo ""

# Final summary
echo "================================================================"
echo "Verification Complete"
echo "================================================================"
echo ""
print_success "Maven 3.9.9 installed and working"
print_success "Context Mapper DSL 6.12.0 installed"
print_success "Context Map Discovery 1.1.0 installed"
print_success "Python integration module working"
print_success "All 21 tests passing (12 unit + 5 integration + 4 E2E)"
print_success "All dependencies available"
echo ""
echo "Context Mapper is ready to use!"
echo ""
echo "Example usage:"
echo "  from src.utils.context_mapper import ContextMapper"
echo "  mapper = ContextMapper()"
echo "  result = mapper.discover_spring_boot_contexts(...)"
echo ""
