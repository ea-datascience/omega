#!/bin/bash

#===============================================================================
# Spec Kit Setup Script for Omega Project
#===============================================================================
#
# DESCRIPTION:
#   This script installs GitHub's Spec Kit globally in the dev container and
#   initializes the Omega project for Spec-Driven Development. It provides
#   automated setup for the complete Spec Kit toolchain integration.
#
# PURPOSE:
#   - Install Spec Kit CLI globally using uv tool manager
#   - Initialize Omega project with GitHub Copilot support
#   - Verify installation and tool availability
#   - Provide post-setup instructions and guidance
#
# FEATURES:
#   - Comprehensive error handling and validation
#   - Color-coded logging with detailed progress reporting
#   - Tool verification and system requirements checking
#   - Integration with existing Omega project structure
#   - Post-installation guidance and documentation links
#
# USAGE:
#   ./setup-speckit.sh              # Full installation and initialization
#   ./setup-speckit.sh --help       # Show help information
#   ./setup-speckit.sh --check      # Check installation status only
#   ./setup-speckit.sh --reinstall  # Force reinstall if already present
#
# REQUIREMENTS:
#   - uv package manager (for Spec Kit CLI installation)
#   - Git (for project initialization)
#   - Python 3.11+ (Spec Kit requirement)
#   - GitHub Copilot or compatible AI agent
#   - Internet connectivity (for GitHub repository access)
#
# INTEGRATION:
#   - Works with existing Omega development container
#   - Respects current project structure and Git repository
#   - Integrates with checkpoint and documentation systems
#   - Enhances GitHub Copilot workflow with slash commands
#
# EXIT CODES:
#   0 - Success
#   1 - General error (installation failed, requirements not met)
#   2 - Tool already installed (when not using --reinstall)
#
# AUTHOR: Omega Project Team
# VERSION: 1.0
# CREATED: 2025-11-14
#
#===============================================================================

set -euo pipefail

# Configuration
SPEC_KIT_REPO="git+https://github.com/github/spec-kit.git"
PROJECT_ROOT="/workspace"
FORCE_REINSTALL=false
CHECK_ONLY=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo
    echo -e "${CYAN}${BOLD}=== $1 ===${NC}"
    echo
}

# Function to show help information
show_help() {
    cat << 'HELP_EOF'
========================================
Spec Kit Setup Script for Omega Project
========================================

DESCRIPTION:
    Installs GitHub's Spec Kit globally and initializes the Omega project
    for Spec-Driven Development with GitHub Copilot integration.

USAGE:
    ./setup-speckit.sh [OPTIONS]

OPTIONS:
    -h, --help         Show this help message
    -c, --check        Check installation status only
    -r, --reinstall    Force reinstall even if already present
    -v, --version      Show version information

EXAMPLES:
    ./setup-speckit.sh                    # Full setup
    ./setup-speckit.sh --check            # Check status
    ./setup-speckit.sh --reinstall        # Force reinstall

POST-INSTALLATION:
    After successful installation, use these slash commands in GitHub Copilot:
    - /speckit.constitution - Create project principles
    - /speckit.specify - Define requirements
    - /speckit.plan - Create implementation plans
    - /speckit.tasks - Generate task lists
    - /speckit.implement - Execute implementation

For complete documentation, see: /workspace/docs/speckit/
========================================
HELP_EOF
}

# Function to show version information
show_version() {
    echo "Spec Kit Setup Script v1.0"
    echo "Part of the Omega agentic migration system"
}

# Function to check prerequisites
check_prerequisites() {
    log_section "Checking Prerequisites"
    
    local missing_tools=()
    
    # Check for uv
    if ! command -v uv &> /dev/null; then
        missing_tools+=("uv (Python package manager)")
    else
        log_success "uv package manager found: $(uv --version)"
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    else
        log_success "Git found: $(git --version | cut -d' ' -f3)"
    fi
    
    # Check for python3
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    else
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python found: $python_version"
        
        # Check Python version (3.11+ required)
        if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            log_warning "Python 3.11+ recommended for Spec Kit (found: $python_version)"
        fi
    fi
    
    # Report missing tools
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        return 1
    fi
    
    log_success "All prerequisites satisfied"
    return 0
}

# Function to check if Spec Kit is already installed
check_spec_kit_installation() {
    if command -v specify &> /dev/null; then
        local version_output=$(specify --version 2>/dev/null || echo "unknown")
        log_info "Spec Kit CLI already installed: $version_output"
        return 0
    else
        log_info "Spec Kit CLI not found - installation needed"
        return 1
    fi
}

# Function to install Spec Kit CLI
install_spec_kit() {
    log_section "Installing Spec Kit CLI"
    
    # Check if already installed and not forcing reinstall
    if check_spec_kit_installation && [ "$FORCE_REINSTALL" = false ]; then
        log_warning "Spec Kit already installed. Use --reinstall to force reinstallation."
        return 2
    fi
    
    log_info "Installing Spec Kit CLI from GitHub repository..."
    log_info "Source: $SPEC_KIT_REPO"
    
    # Install using uv tool
    if [ "$FORCE_REINSTALL" = true ]; then
        log_info "Force reinstalling Spec Kit CLI..."
        if uv tool install specify-cli --force --from "$SPEC_KIT_REPO"; then
            log_success "Spec Kit CLI reinstalled successfully"
        else
            log_error "Failed to reinstall Spec Kit CLI"
            return 1
        fi
    else
        if uv tool install specify-cli --from "$SPEC_KIT_REPO"; then
            log_success "Spec Kit CLI installed successfully"
        else
            log_error "Failed to install Spec Kit CLI"
            return 1
        fi
    fi
    
    # Verify installation
    if command -v specify &> /dev/null; then
        local version_output=$(specify --version 2>/dev/null || echo "installed")
        log_success "Installation verified: $version_output"
    else
        log_error "Installation verification failed - specify command not found"
        return 1
    fi
    
    return 0
}

# Function to initialize Omega project with Spec Kit
initialize_project() {
    log_section "Initializing Omega Project with Spec Kit"
    
    cd "$PROJECT_ROOT"
    
    log_info "Initializing Spec Kit in current directory with GitHub Copilot support..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Initialize with GitHub Copilot support
    if specify init --here --ai copilot --force; then
        log_success "Omega project initialized with Spec Kit"
    else
        log_error "Failed to initialize project with Spec Kit"
        return 1
    fi
    
    # Verify initialization
    if [ -d ".speckit" ]; then
        log_success "Spec Kit configuration directory created"
    else
        log_warning "Spec Kit configuration directory not found"
    fi
    
    return 0
}

# Function to run system check
run_system_check() {
    log_section "Running Spec Kit System Check"
    
    if specify check; then
        log_success "System check completed successfully"
    else
        log_warning "System check completed with warnings"
    fi
}

# Function to show post-installation instructions
show_post_installation_info() {
    log_section "Post-Installation Information"
    
    cat << 'INFO_EOF'
✅ Spec Kit setup completed successfully!

🚀 AVAILABLE SLASH COMMANDS IN GITHUB COPILOT:

Core Workflow Commands:
  /speckit.constitution  - Create project principles and guidelines
  /speckit.specify      - Define what you want to build
  /speckit.plan         - Create technical implementation plans
  /speckit.tasks        - Generate actionable task lists
  /speckit.implement    - Execute implementation

Quality & Analysis Commands:
  /speckit.clarify      - Clarify underspecified areas
  /speckit.analyze      - Cross-artifact consistency analysis
  /speckit.checklist    - Generate quality validation checklists

📋 RECOMMENDED NEXT STEPS:

1. Create project constitution:
   /speckit.constitution Create principles for Omega agentic migration system

2. Specify your first feature:
   /speckit.specify Build migration analysis engine for Spring Boot applications

3. Plan implementation:
   /speckit.plan Use Python, Docker containers, and existing Omega tools

4. Generate tasks and implement:
   /speckit.tasks
   /speckit.implement

📚 DOCUMENTATION:
   Complete guide: /workspace/docs/speckit/
   Official docs: https://github.com/github/spec-kit

🔧 MANAGEMENT COMMANDS:
   List installed tools: uv tool list
   Upgrade Spec Kit:     uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
   Uninstall:           uv tool uninstall specify-cli

INFO_EOF
}

# Function to perform check-only operation
check_only_operation() {
    log_section "Spec Kit Installation Status Check"
    
    check_prerequisites
    
    if check_spec_kit_installation; then
        log_success "Spec Kit CLI is installed and available"
        
        # Check if project is initialized
        if [ -d "$PROJECT_ROOT/.speckit" ]; then
            log_success "Omega project is initialized with Spec Kit"
        else
            log_warning "Omega project not initialized with Spec Kit"
            log_info "Run './setup-speckit.sh' to initialize"
        fi
        
        # Run system check
        run_system_check
    else
        log_warning "Spec Kit CLI not installed"
        log_info "Run './setup-speckit.sh' to install and initialize"
    fi
}

# Main execution function
main() {
    echo "========================================"
    echo "  Spec Kit Setup for Omega Project"
    echo "========================================"
    echo
    
    # Handle check-only mode
    if [ "$CHECK_ONLY" = true ]; then
        check_only_operation
        return 0
    fi
    
    # Full installation process
    if ! check_prerequisites; then
        log_error "Prerequisites not met. Please install missing tools."
        exit 1
    fi
    
    # Install Spec Kit CLI
    local install_result=0
    install_spec_kit || install_result=$?
    
    if [ $install_result -eq 2 ]; then
        # Already installed, continue with initialization
        log_info "Proceeding with project initialization..."
    elif [ $install_result -ne 0 ]; then
        # Installation failed
        exit 1
    fi
    
    # Initialize project
    if ! initialize_project; then
        log_error "Project initialization failed"
        exit 1
    fi
    
    # Run system check
    run_system_check
    
    # Show post-installation information
    show_post_installation_info
    
    log_success "Spec Kit setup completed successfully!"
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        -c|--check)
            CHECK_ONLY=true
            shift
            ;;
        -r|--reinstall)
            FORCE_REINSTALL=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi