#!/bin/bash
set -e

# install-angular-cli.sh - Reproducible Angular CLI and dashboard dependencies installation
# 
# This script installs Angular CLI globally and dashboard npm dependencies
# following Omega constitution reproducibility standards.
#
# Usage: ./install-angular-cli.sh [--global-only]
#
# Options:
#   --global-only    Install only Angular CLI globally, skip dashboard dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DASHBOARD_DIR="$WORKSPACE_ROOT/dashboard"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
GLOBAL_ONLY=false
if [[ "$1" == "--global-only" ]]; then
    GLOBAL_ONLY=true
fi

echo -e "${BLUE}[INFO]${NC} Angular CLI Installation Script"
echo -e "${BLUE}[INFO]${NC} Workspace: $WORKSPACE_ROOT"

# Verify Node.js installation
echo -e "\n${BLUE}[INFO]${NC} Verifying Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Node.js is not installed"
    echo -e "${YELLOW}[HINT]${NC} Node.js should be installed via .devcontainer/Dockerfile"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}[SUCCESS]${NC} Node.js $NODE_VERSION installed"
echo -e "${GREEN}[SUCCESS]${NC} npm $NPM_VERSION installed"

# Check Node.js version (should be 20.x)
NODE_MAJOR_VERSION=$(node --version | cut -d'.' -f1 | sed 's/v//')
if [[ "$NODE_MAJOR_VERSION" -lt 20 ]]; then
    echo -e "${RED}[ERROR]${NC} Node.js version must be 20.x or higher"
    echo -e "${YELLOW}[CURRENT]${NC} $NODE_VERSION"
    exit 1
fi

# Install Angular CLI globally
echo -e "\n${BLUE}[INFO]${NC} Installing Angular CLI globally..."
ANGULAR_CLI_VERSION="17.0.0"

if command -v ng &> /dev/null; then
    INSTALLED_VERSION=$(ng version --version 2>/dev/null || echo "unknown")
    echo -e "${YELLOW}[INFO]${NC} Angular CLI already installed: $INSTALLED_VERSION"
    echo -e "${BLUE}[INFO]${NC} Reinstalling to ensure version $ANGULAR_CLI_VERSION..."
fi

# Use sudo for global npm installation
sudo npm install -g @angular/cli@$ANGULAR_CLI_VERSION

# Verify Angular CLI installation
if ! command -v ng &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Angular CLI installation failed"
    exit 1
fi

INSTALLED_NG_VERSION=$(ng version --version 2>/dev/null || echo "unknown")
echo -e "${GREEN}[SUCCESS]${NC} Angular CLI $INSTALLED_NG_VERSION installed globally"

# If --global-only flag is set, skip dashboard dependencies
if [[ "$GLOBAL_ONLY" == true ]]; then
    echo -e "\n${GREEN}[SUCCESS]${NC} Angular CLI installation complete (global only)"
    echo -e "${BLUE}[INFO]${NC} Skipping dashboard dependencies (--global-only flag set)"
    exit 0
fi

# Install dashboard dependencies
echo -e "\n${BLUE}[INFO]${NC} Installing dashboard dependencies..."

if [[ ! -f "$DASHBOARD_DIR/package.json" ]]; then
    echo -e "${RED}[ERROR]${NC} package.json not found at $DASHBOARD_DIR/package.json"
    exit 1
fi

cd "$DASHBOARD_DIR"

# Check if node_modules exists and is populated
if [[ -d "node_modules" ]] && [[ -n "$(ls -A node_modules)" ]]; then
    echo -e "${YELLOW}[INFO]${NC} node_modules directory already exists"
    echo -e "${BLUE}[INFO]${NC} Running npm install to update dependencies..."
else
    echo -e "${BLUE}[INFO]${NC} Installing dashboard dependencies from package.json..."
fi

npm install

# Verify critical dependencies
echo -e "\n${BLUE}[INFO]${NC} Verifying critical dependencies..."

REQUIRED_DEPS=(
    "@angular/core"
    "@angular/cli"
    "@angular/material"
    "typescript"
    "rxjs"
)

MISSING_DEPS=()
for dep in "${REQUIRED_DEPS[@]}"; do
    if [[ ! -d "node_modules/$dep" ]]; then
        MISSING_DEPS+=("$dep")
    fi
done

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo -e "${RED}[ERROR]${NC} Missing required dependencies:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo -e "  - $dep"
    done
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} All critical dependencies verified"

# Display installation summary
echo -e "\n${GREEN}[SUCCESS]${NC} Angular CLI and dashboard dependencies installed successfully!"
echo -e "\n${BLUE}[SUMMARY]${NC}"
echo -e "  Node.js:     $NODE_VERSION"
echo -e "  npm:         $NPM_VERSION"
echo -e "  Angular CLI: $INSTALLED_NG_VERSION"
echo -e "  Dashboard:   $DASHBOARD_DIR"

echo -e "\n${BLUE}[USAGE]${NC}"
echo -e "  Start dev server:  cd $DASHBOARD_DIR && npm start"
echo -e "  Build production:  cd $DASHBOARD_DIR && npm run build"
echo -e "  Run tests:         cd $DASHBOARD_DIR && npm test"
echo -e "  Run linter:        cd $DASHBOARD_DIR && npm run lint"

exit 0
