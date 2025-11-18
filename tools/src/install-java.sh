#!/bin/bash
# Install Java Development Kit in Omega Dev Container
#
# This script installs OpenJDK 17 (Eclipse Temurin distribution)
# for Java analysis and development tasks.

set -e

echo "=========================================="
echo "Installing Java Development Kit"
echo "=========================================="

# Check if Java is already installed
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo "Java is already installed: $JAVA_VERSION"
    echo "To reinstall, uninstall first or run with --force"
    exit 0
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS $VERSION"

# Install OpenJDK 17 based on OS
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Installing OpenJDK 17 via apt..."
    
    sudo apt-get update
    sudo apt-get install -y openjdk-17-jdk openjdk-17-jre
    
elif [ "$OS" = "alpine" ]; then
    echo "Installing OpenJDK 17 via apk..."
    
    sudo apk add --no-cache openjdk17-jdk
    
else
    echo "Unsupported OS: $OS"
    echo "Please install Java 17+ manually from: https://adoptium.net/"
    exit 1
fi

# Set JAVA_HOME
JAVA_PATH=$(readlink -f $(which java))
JAVA_HOME="${JAVA_PATH%/bin/java}"

echo "Java installed successfully!"
echo "Java Home: $JAVA_HOME"

# Configure JAVA_HOME in shell profiles
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "JAVA_HOME" "$HOME/.bashrc"; then
        echo "" >> "$HOME/.bashrc"
        echo "# Java configuration" >> "$HOME/.bashrc"
        echo "export JAVA_HOME=\"$JAVA_HOME\"" >> "$HOME/.bashrc"
        echo "export PATH=\"\$JAVA_HOME/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo "Added JAVA_HOME to ~/.bashrc"
    fi
fi

if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "JAVA_HOME" "$HOME/.zshrc"; then
        echo "" >> "$HOME/.zshrc"
        echo "# Java configuration" >> "$HOME/.zshrc"
        echo "export JAVA_HOME=\"$JAVA_HOME\"" >> "$HOME/.zshrc"
        echo "export PATH=\"\$JAVA_HOME/bin:\$PATH\"" >> "$HOME/.zshrc"
        echo "Added JAVA_HOME to ~/.zshrc"
    fi
fi

# Verify installation
echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
java -version
echo ""
echo "JAVA_HOME: $JAVA_HOME"
echo ""
echo "=========================================="
echo "Java installation complete!"
echo "=========================================="
echo ""
echo "To activate JAVA_HOME in current shell, run:"
echo "  source ~/.bashrc"
echo ""
echo "Or start a new terminal session."
