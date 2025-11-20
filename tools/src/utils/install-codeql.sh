#!/bin/bash
#
# CodeQL CLI Installation Script
#
# This script provides reproducible installation of CodeQL CLI for the Omega project.
# It follows the Omega Constitution principles of version pinning and reproducibility.
#
# Version Information:
# - CodeQL CLI: 2.23.5 (latest stable as of 2025-11-20)
# - Java Required: 17+ (pre-installed in dev container)
# - Installation Location: /opt/codeql
#
# Usage:
#   ./install-codeql.sh
#
# References:
# - GitHub CodeQL CLI: https://github.com/github/codeql-cli-binaries
# - CodeQL Documentation: https://codeql.github.com/docs/codeql-cli/

set -euo pipefail

# Version pinning (CRITICAL: Do not change without updating tests and documentation)
CODEQL_VERSION="2.23.5"
CODEQL_URL="https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip"
INSTALL_DIR="/opt/codeql"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "CodeQL CLI Installation Script"
echo "Version: ${CODEQL_VERSION}"
echo "========================================"
echo ""

# Check if running in dev container
if [ ! -f "/.dockerenv" ]; then
    echo -e "${YELLOW}Warning: Not running in dev container${NC}"
    echo "This script is designed for the Omega dev container environment"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Java installation
echo "Checking Java installation..."
if ! command -v java &> /dev/null; then
    echo -e "${RED}Error: Java not found${NC}"
    echo "Java 17+ is required for CodeQL CLI"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo -e "${RED}Error: Java 17+ required, found Java $JAVA_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Java $JAVA_VERSION found"
echo ""

# Check if CodeQL is already installed
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}CodeQL installation directory already exists: $INSTALL_DIR${NC}"
    
    # Check installed version
    if [ -f "$INSTALL_DIR/codeql" ]; then
        INSTALLED_VERSION=$("$INSTALL_DIR/codeql" version --format=text 2>/dev/null | head -n 1 || echo "unknown")
        echo "Installed version: $INSTALLED_VERSION"
        
        if echo "$INSTALLED_VERSION" | grep -q "$CODEQL_VERSION"; then
            echo -e "${GREEN}✓${NC} CodeQL $CODEQL_VERSION is already installed"
            echo ""
            echo "Verifying installation..."
            "$INSTALL_DIR/codeql" version
            exit 0
        else
            echo "Version mismatch. Reinstalling..."
            sudo rm -rf "$INSTALL_DIR"
        fi
    else
        echo "Invalid installation. Cleaning up..."
        sudo rm -rf "$INSTALL_DIR"
    fi
fi

# Download CodeQL CLI
echo "Downloading CodeQL CLI v${CODEQL_VERSION}..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

if ! wget -q --show-progress "$CODEQL_URL" -O codeql-linux64.zip; then
    echo -e "${RED}Error: Failed to download CodeQL CLI${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Downloaded CodeQL CLI"
echo ""

# Verify download size (should be ~300MB)
FILE_SIZE=$(stat -f%z codeql-linux64.zip 2>/dev/null || stat -c%s codeql-linux64.zip)
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))
echo "Download size: ${FILE_SIZE_MB}MB"

if [ "$FILE_SIZE_MB" -lt 100 ]; then
    echo -e "${RED}Error: Downloaded file is too small (${FILE_SIZE_MB}MB), may be corrupted${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Extract CodeQL CLI
echo "Extracting CodeQL CLI..."
if ! unzip -q codeql-linux64.zip; then
    echo -e "${RED}Error: Failed to extract CodeQL CLI${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Extracted CodeQL CLI"
echo ""

# Install to /opt/codeql
echo "Installing CodeQL CLI to $INSTALL_DIR..."
sudo mv codeql "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR/codeql"

# Verify installation
if [ ! -f "$INSTALL_DIR/codeql" ]; then
    echo -e "${RED}Error: Installation failed - codeql binary not found${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Installed CodeQL CLI to $INSTALL_DIR"
echo ""

# Clean up
rm -rf "$TEMP_DIR"

# Verify CodeQL version
echo "Verifying CodeQL installation..."
"$INSTALL_DIR/codeql" version

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CodeQL CLI Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Installation Details:"
echo "  Version: ${CODEQL_VERSION}"
echo "  Location: ${INSTALL_DIR}"
echo "  Binary: ${INSTALL_DIR}/codeql"
echo ""
echo "Usage:"
echo "  ${INSTALL_DIR}/codeql --help"
echo "  ${INSTALL_DIR}/codeql version"
echo ""
echo "Next Steps:"
echo "  1. Download CodeQL query packs:"
echo "     ${INSTALL_DIR}/codeql pack download codeql/java-queries"
echo "     ${INSTALL_DIR}/codeql pack download codeql/python-queries"
echo ""
echo "  2. Create a CodeQL database:"
echo "     ${INSTALL_DIR}/codeql database create <db-path> --language=<lang>"
echo ""
echo "  3. Run queries:"
echo "     ${INSTALL_DIR}/codeql database analyze <db-path> --format=sarif-latest --output=results.sarif"
echo ""
echo "Documentation: https://codeql.github.com/docs/codeql-cli/"
