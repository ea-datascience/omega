#!/bin/bash
#
# Maven Installation Script
# Installs Apache Maven in a reproducible way with pinned version
#
# Usage: ./install-maven.sh
#
# Follows Omega Constitution principles:
# - Pinned version (3.9.9)
# - Reproducible installation
# - Verification included
#

set -e  # Exit on error

# Pinned version
MAVEN_VERSION="3.9.9"
MAVEN_HOME="/opt/maven"
MAVEN_ARCHIVE="apache-maven-${MAVEN_VERSION}-bin.tar.gz"
MAVEN_URL="https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/${MAVEN_ARCHIVE}"

echo "Installing Apache Maven ${MAVEN_VERSION}..."

# Check if Maven is already installed with the correct version
if command -v mvn &> /dev/null; then
    CURRENT_VERSION=$(mvn --version | head -n 1 | awk '{print $3}')
    if [ "$CURRENT_VERSION" = "$MAVEN_VERSION" ]; then
        echo "Maven ${MAVEN_VERSION} is already installed."
        exit 0
    else
        echo "Maven ${CURRENT_VERSION} found, but version ${MAVEN_VERSION} is required."
        echo "Proceeding with installation..."
    fi
fi

# Create installation directory
sudo mkdir -p "$MAVEN_HOME"

# Download Maven
echo "Downloading Maven ${MAVEN_VERSION}..."
cd /tmp
wget -q "$MAVEN_URL"

# Verify download
if [ ! -f "$MAVEN_ARCHIVE" ]; then
    echo "ERROR: Failed to download Maven archive"
    exit 1
fi

# Extract Maven
echo "Extracting Maven..."
sudo tar -xzf "$MAVEN_ARCHIVE" -C "$MAVEN_HOME" --strip-components=1

# Clean up
rm "$MAVEN_ARCHIVE"

# Add to PATH (update profile files)
if ! grep -q "MAVEN_HOME" /etc/profile.d/maven.sh 2>/dev/null; then
    echo "Configuring environment variables..."
    sudo tee /etc/profile.d/maven.sh > /dev/null <<EOF
export MAVEN_HOME=$MAVEN_HOME
export PATH=\$MAVEN_HOME/bin:\$PATH
EOF
    sudo chmod +x /etc/profile.d/maven.sh
fi

# Source the profile for current session
export MAVEN_HOME=$MAVEN_HOME
export PATH=$MAVEN_HOME/bin:$PATH

# Verify installation
if command -v mvn &> /dev/null; then
    INSTALLED_VERSION=$(mvn --version | head -n 1 | awk '{print $3}')
    echo "Maven ${INSTALLED_VERSION} installed successfully!"
    mvn --version
else
    echo "ERROR: Maven installation failed"
    exit 1
fi

echo "Maven installation complete."
echo "You may need to start a new shell session or run: source /etc/profile.d/maven.sh"
