#!/bin/bash
#
# Microsoft Application Inspector CLI Installation Script
#
# This script provides reproducible installation of Microsoft Application Inspector
# for the Omega project. It follows the Omega Constitution principles of version
# pinning and reproducibility.
#
# Version Information:
# - Application Inspector: 1.9.53 (latest stable as of 2025-11-20)
# - .NET Required: 8.0+ (pre-installed in dev container)
# - Installation Location: /opt/appinspector
#
# Usage:
#   ./install-appinspector.sh
#
# References:
# - GitHub: https://github.com/microsoft/ApplicationInspector
# - Documentation: https://github.com/microsoft/ApplicationInspector/wiki

set -euo pipefail

# Version pinning (CRITICAL: Do not change without updating tests and documentation)
APPINSPECTOR_VERSION="1.9.53"
INSTALL_DIR="/opt/appinspector"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Use netcoreapp package (cross-platform .NET DLLs)
APPINSPECTOR_URL="https://github.com/microsoft/ApplicationInspector/releases/download/v${APPINSPECTOR_VERSION}/ApplicationInspector_netcoreapp_${APPINSPECTOR_VERSION}.zip"

echo "========================================"
echo "Application Inspector Installation Script"
echo "Version: ${APPINSPECTOR_VERSION}"
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

# Check .NET installation
echo "Checking .NET installation..."
if ! command -v dotnet &> /dev/null; then
    echo -e "${RED}Error: .NET SDK not found${NC}"
    echo "Please install .NET 8.0 SDK or rebuild the dev container"
    echo "See: https://dotnet.microsoft.com/download"
    exit 1
fi

DOTNET_VERSION=$(dotnet --version)
echo -e "${GREEN}✓${NC} .NET SDK ${DOTNET_VERSION} found"
echo ""

# Check if already installed
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Warning: Application Inspector already installed at ${INSTALL_DIR}${NC}"
    read -p "Reinstall? This will remove the existing installation. (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    else
        echo "Installation cancelled"
        exit 0
    fi
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "Downloading Application Inspector v${APPINSPECTOR_VERSION} (netcoreapp)..."
if ! curl -L --progress-bar "$APPINSPECTOR_URL" -o appinspector.zip; then
    echo -e "${RED}Error: Failed to download Application Inspector${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Downloaded Application Inspector"
echo ""

# Verify download size
FILE_SIZE=$(stat -f%z "appinspector.zip" 2>/dev/null || stat -c%s "appinspector.zip")
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))
echo "Download size: ${FILE_SIZE_MB}MB"

if [ "$FILE_SIZE_MB" -lt 5 ]; then
    echo -e "${RED}Error: Downloaded file is too small (${FILE_SIZE_MB}MB), may be corrupted${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Extract Application Inspector
echo "Extracting Application Inspector..."
if ! unzip -q appinspector.zip; then
    echo -e "${RED}Error: Failed to extract Application Inspector${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Extracted Application Inspector"
echo ""

# Install to /opt/appinspector
echo "Installing Application Inspector to ${INSTALL_DIR}..."
mkdir -p /opt
mv ApplicationInspector_netcoreapp_${APPINSPECTOR_VERSION} "$INSTALL_DIR"

echo -e "${GREEN}✓${NC} Installed Application Inspector to ${INSTALL_DIR}"
echo ""

# Cleanup
cd /
rm -rf "$TEMP_DIR"

# Create wrapper script in /usr/local/bin
echo "Creating wrapper script..."
cat > /usr/local/bin/appinspector <<'EOF'
#!/bin/bash
# Application Inspector wrapper script
exec dotnet /opt/appinspector/ApplicationInspector.CLI.dll "$@"
EOF

chmod +x /usr/local/bin/appinspector

echo -e "${GREEN}✓${NC} Created wrapper script at /usr/local/bin/appinspector"
echo ""

# Verify installation
echo "Verifying Application Inspector installation..."
if appinspector --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Application Inspector installed successfully!"
    echo ""
    echo "Version information:"
    appinspector --version
    echo ""
    echo "Installation complete!"
    echo "You can now use 'appinspector' command from anywhere."
else
    echo -e "${RED}Error: Application Inspector verification failed${NC}"
    exit 1
fi
