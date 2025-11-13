#!/bin/bash

# Spring Modulith Repository Cloning Script
# This script provides idempotent cloning of the Spring Modulith reference repository
# for the Omega agentic migration system.

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
REPO_URL="https://github.com/spring-projects/spring-modulith.git"
TARGET_DIR="/workspace/data/codebase/spring-modulith"
CODEBASE_DIR="/workspace/data/codebase"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if directory exists and is a git repository
is_git_repo() {
    local dir="$1"
    [[ -d "$dir" && -d "$dir/.git" ]]
}

# Function to get remote URL of existing repository
get_remote_url() {
    local dir="$1"
    if is_git_repo "$dir"; then
        cd "$dir"
        git remote get-url origin 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Function to create directory structure
create_directories() {
    log_info "Creating directory structure..."
    mkdir -p "$CODEBASE_DIR"
    log_success "Directory structure created: $CODEBASE_DIR"
}

# Function to remove existing repository
remove_existing() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        log_warning "Existing directory found at $dir"
        log_info "Removing existing directory..."
        rm -rf "$dir"
        log_success "Existing directory removed"
    fi
}

# Function to clone repository
clone_repository() {
    log_info "Cloning Spring Modulith repository..."
    log_info "Source: $REPO_URL"
    log_info "Target: $TARGET_DIR"
    
    cd "$CODEBASE_DIR"
    
    if git clone "$REPO_URL" "$(basename "$TARGET_DIR")"; then
        log_success "Repository cloned successfully"
        return 0
    else
        log_error "Failed to clone repository"
        return 1
    fi
}

# Function to verify repository
verify_repository() {
    local dir="$1"
    
    if ! is_git_repo "$dir"; then
        log_error "Directory is not a valid git repository: $dir"
        return 1
    fi
    
    local remote_url
    remote_url=$(get_remote_url "$dir")
    
    if [[ "$remote_url" != "$REPO_URL" ]]; then
        log_error "Repository URL mismatch. Expected: $REPO_URL, Found: $remote_url"
        return 1
    fi
    
    # Check if basic Spring Modulith files exist
    local required_files=(
        "$dir/build.gradle"
        "$dir/src"
        "$dir/README.adoc"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -e "$file" ]]; then
            log_warning "Expected file/directory not found: $file"
        fi
    done
    
    log_success "Repository verification completed"
    return 0
}

# Function to display repository information
show_repo_info() {
    local dir="$1"
    
    if [[ -d "$dir" ]]; then
        log_info "Repository Information:"
        echo "  Location: $dir"
        echo "  Size: $(du -sh "$dir" 2>/dev/null | cut -f1 || echo 'Unknown')"
        
        if is_git_repo "$dir"; then
            cd "$dir"
            echo "  Remote URL: $(git remote get-url origin 2>/dev/null || echo 'Unknown')"
            echo "  Current Branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"
            echo "  Last Commit: $(git log -1 --format='%h - %s (%cr)' 2>/dev/null || echo 'Unknown')"
        fi
    fi
}

# Main execution function
main() {
    echo "========================================"
    echo "Spring Modulith Repository Setup Script"
    echo "========================================"
    
    log_info "Starting idempotent repository setup..."
    
    # Create directory structure
    create_directories
    
    # Check if target directory exists
    if [[ -d "$TARGET_DIR" ]]; then
        local existing_url
        existing_url=$(get_remote_url "$TARGET_DIR")
        
        if [[ "$existing_url" == "$REPO_URL" ]]; then
            log_warning "Spring Modulith repository already exists with correct URL"
            log_info "Removing and re-cloning to ensure latest version..."
        else
            log_warning "Directory exists but contains different repository or is not a git repo"
            log_info "Removing existing content..."
        fi
        
        remove_existing "$TARGET_DIR"
    fi
    
    # Clone repository
    if clone_repository; then
        log_success "Clone operation completed successfully"
    else
        log_error "Clone operation failed"
        exit 1
    fi
    
    # Verify repository
    if verify_repository "$TARGET_DIR"; then
        log_success "Repository verification passed"
    else
        log_error "Repository verification failed"
        exit 1
    fi
    
    # Show repository information
    show_repo_info "$TARGET_DIR"
    
    echo "========================================"
    log_success "Spring Modulith repository setup completed successfully!"
    echo "========================================"
    
    log_info "Repository is ready for analysis at: $TARGET_DIR"
    log_info "This repository is excluded from version control via .gitignore"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi