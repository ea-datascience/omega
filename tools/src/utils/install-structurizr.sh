#!/bin/bash
#
# Structurizr CLI Installation Script
#
# This script installs Structurizr CLI for architecture diagram generation and
# export. Part of the Omega migration system tool suite.
#
# Requirements:
# - Java 17+ (automatically verified)
# - curl or wget for downloading
#
# Installation:
#   chmod +x install-structurizr.sh
#   ./install-structurizr.sh
#
# Verification:
#   /opt/structurizr-cli/structurizr.sh --version
#

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Version pinning for reproducibility
STRUCTURIZR_VERSION="2025.11.09"
STRUCTURIZR_DOWNLOAD_URL="https://github.com/structurizr/cli/releases/download/v${STRUCTURIZR_VERSION}/structurizr-cli.zip"
INSTALL_DIR="/opt/structurizr-cli"

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Structurizr CLI Installation${NC}"
echo -e "${GREEN}Version: ${STRUCTURIZR_VERSION}${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Step 1: Check if already installed
if [ -f "${INSTALL_DIR}/structurizr.sh" ]; then
    echo -e "${YELLOW}Structurizr CLI is already installed at ${INSTALL_DIR}${NC}"
    echo -e "${YELLOW}To reinstall, remove the directory first:${NC}"
    echo -e "${YELLOW}  sudo rm -rf ${INSTALL_DIR}${NC}"
    exit 0
fi

# Step 2: Verify Java 17+ is available
echo "[1/6] Verifying Java installation..."
if ! command -v java &> /dev/null; then
    echo -e "${RED}Error: Java is not installed${NC}"
    echo "Please install Java 17 or later"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo -e "${RED}Error: Java 17+ required, found Java ${JAVA_VERSION}${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Java ${JAVA_VERSION} detected${NC}"
echo ""

# Step 3: Create temporary download directory
echo "[2/6] Creating temporary download directory..."
TMP_DIR=$(mktemp -d)
trap "rm -rf ${TMP_DIR}" EXIT

echo -e "${GREEN}✓ Temporary directory: ${TMP_DIR}${NC}"
echo ""

# Step 4: Download Structurizr CLI
echo "[3/6] Downloading Structurizr CLI v${STRUCTURIZR_VERSION}..."
echo "URL: ${STRUCTURIZR_DOWNLOAD_URL}"

if command -v curl &> /dev/null; then
    curl -L -o "${TMP_DIR}/structurizr-cli.zip" "${STRUCTURIZR_DOWNLOAD_URL}"
elif command -v wget &> /dev/null; then
    wget -O "${TMP_DIR}/structurizr-cli.zip" "${STRUCTURIZR_DOWNLOAD_URL}"
else
    echo -e "${RED}Error: Neither curl nor wget is available${NC}"
    exit 1
fi

if [ ! -f "${TMP_DIR}/structurizr-cli.zip" ]; then
    echo -e "${RED}Error: Download failed${NC}"
    exit 1
fi

DOWNLOAD_SIZE=$(stat -c%s "${TMP_DIR}/structurizr-cli.zip" 2>/dev/null || stat -f%z "${TMP_DIR}/structurizr-cli.zip" 2>/dev/null)
echo -e "${GREEN}✓ Downloaded ${DOWNLOAD_SIZE} bytes${NC}"
echo ""

# Step 5: Extract and install
echo "[4/6] Extracting Structurizr CLI..."

unzip -q "${TMP_DIR}/structurizr-cli.zip" -d "${TMP_DIR}"

# Find the extracted directory (it contains structurizr.sh)
EXTRACTED_DIR=$(find "${TMP_DIR}" -name "structurizr.sh" -type f | head -1 | xargs dirname)

if [ -z "${EXTRACTED_DIR}" ]; then
    echo -e "${RED}Error: structurizr.sh not found in extracted files${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Extracted to: ${EXTRACTED_DIR}${NC}"
echo ""

echo "[5/6] Installing to ${INSTALL_DIR}..."

# Create install directory and move files
sudo mkdir -p "${INSTALL_DIR}"
sudo cp -r "${EXTRACTED_DIR}"/* "${INSTALL_DIR}/"

# Make shell scripts executable
sudo chmod +x "${INSTALL_DIR}/structurizr.sh" 2>/dev/null || true
sudo chmod +x "${INSTALL_DIR}/structurizr.bat" 2>/dev/null || true

echo -e "${GREEN}✓ Installed to ${INSTALL_DIR}${NC}"
echo ""

# Step 6: Verify installation
echo "[6/6] Verifying installation..."

if [ ! -f "${INSTALL_DIR}/structurizr.sh" ]; then
    echo -e "${RED}Error: Installation verification failed${NC}"
    exit 1
fi

# Test execution
if "${INSTALL_DIR}/structurizr.sh" --version &> /dev/null; then
    echo -e "${GREEN}✓ Structurizr CLI is executable${NC}"
else
    echo -e "${YELLOW}Warning: Could not verify version (may be normal)${NC}"
fi

# List installed files
echo ""
echo "Installed files:"
ls -lh "${INSTALL_DIR}" | grep -E "\.(sh|bat|jar)$" || ls -lh "${INSTALL_DIR}"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Structurizr CLI ${STRUCTURIZR_VERSION} has been installed successfully."
echo ""
echo "Installation directory: ${INSTALL_DIR}"
echo ""
echo "Usage:"
echo "  ${INSTALL_DIR}/structurizr.sh [command] [options]"
echo ""
echo "Available commands:"
echo "  export    - Export diagrams to PlantUML, Mermaid, DOT, etc."
echo "  validate  - Validate a DSL workspace"
echo "  inspect   - Inspect a workspace"
echo "  push      - Push to Structurizr cloud/on-premises"
echo "  pull      - Pull workspace from Structurizr"
echo ""
echo "Example:"
echo "  ${INSTALL_DIR}/structurizr.sh export --workspace workspace.dsl --format plantuml"
echo ""
echo "Add to PATH (optional):"
echo "  export PATH=\"\${PATH}:${INSTALL_DIR}\""
echo ""
