#!/bin/bash
#
# Reproducible tree-sitter-java installation script
# 
# This script ensures consistent parser installation across all developers.
# Versions are pinned for reproducibility.
#
# Usage: ./install-tree-sitter-java.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Pinned versions for reproducibility
TREE_SITTER_VERSION="0.23.2"
TREE_SITTER_JAVA_VERSION="0.23.5"

echo "========================================="
echo "tree-sitter-java Installation"
echo "========================================="
echo ""
echo "Versions (pinned for reproducibility):"
echo "  tree-sitter: ${TREE_SITTER_VERSION}"
echo "  tree-sitter-java: ${TREE_SITTER_JAVA_VERSION}"
echo ""

# Check for force flag
FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
    echo "Force reinstallation enabled"
fi

# Check if already installed
if ! $FORCE; then
    if python3 -c "import tree_sitter_java" 2>/dev/null; then
        CURRENT_VERSION=$(python3 -c "import tree_sitter_java; print(getattr(tree_sitter_java, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        if [[ "$CURRENT_VERSION" == "$TREE_SITTER_JAVA_VERSION" ]]; then
            echo "✓ tree-sitter-java v${TREE_SITTER_JAVA_VERSION} already installed"
            exit 0
        else
            echo "Current version: $CURRENT_VERSION"
            echo "Target version: $TREE_SITTER_JAVA_VERSION"
            echo "Upgrading..."
        fi
    fi
fi

# Install tree-sitter core
echo ""
echo "Installing tree-sitter core v${TREE_SITTER_VERSION}..."
python3 -m pip install "tree-sitter==${TREE_SITTER_VERSION}"

# Install tree-sitter-java
echo ""
echo "Installing tree-sitter-java v${TREE_SITTER_JAVA_VERSION}..."
python3 -m pip install "tree-sitter-java==${TREE_SITTER_JAVA_VERSION}"

# Verify installation
echo ""
echo "Verifying installation..."
if python3 -c "import tree_sitter_java; import tree_sitter; print('✓ tree-sitter-java successfully installed')" 2>/dev/null; then
    echo ""
    echo "========================================="
    echo "Installation Complete"
    echo "========================================="
    echo ""
    echo "Parser capabilities:"
    echo "  ✓ Java 17+ syntax support"
    echo "  ✓ Records (Java 14+)"
    echo "  ✓ Pattern matching (Java 16+)"
    echo "  ✓ Sealed classes (Java 17+)"
    echo ""
else
    echo ""
    echo "✗ Installation verification failed"
    exit 1
fi
