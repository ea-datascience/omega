#!/bin/bash

#===============================================================================
# Project Checkpoint Creation Script
#===============================================================================
#
# DESCRIPTION:
#   This script creates comprehensive checkpoints for the Omega agentic migration
#   system to facilitate resuming development sessions with GitHub Copilot.
#   It captures complete project state including Git status, modified files,
#   work context, and provides detailed resume instructions.
#
# PURPOSE:
#   - Capture complete project state for development session continuity
#   - Provide comprehensive context for GitHub Copilot integration
#   - Enable seamless work resumption after breaks or handoffs
#   - Document current tasks, blockers, and next steps
#   - Preserve Git status and modified file information
#
# FEATURES:
#   - Interactive Context Capture: Prompts for current work details
#   - Comprehensive Git Analysis: Staged, unstaged, and untracked file tracking
#   - Environment Documentation: Development environment and tool version capture
#   - Recent Activity Summary: Last commits and file changes overview
#   - Project Structure Snapshot: Directory tree and organization overview
#   - Resume Instructions: Step-by-step guidance for continuing work
#   - Timestamped Storage: Organized checkpoint files with date/time naming
#   - Multiple Output Modes: Create, list, or help functionality
#
# USAGE:
#   ./create-checkpoint.sh              # Create new checkpoint (interactive)
#   ./create-checkpoint.sh --create     # Create new checkpoint
#   ./create-checkpoint.sh --list       # List existing checkpoints
#   ./create-checkpoint.sh --help       # Show help information
#
# INTERACTIVE PROMPTS:
#   When creating a checkpoint, prompts for:
#   - Current Epic/Feature: High-level work area
#   - Current Task/Issue: Specific task or issue being addressed
#   - Task Status: Current progress (in-progress, blocked, testing, etc.)
#   - Next Planned Tasks: Upcoming work items
#   - Blockers/Issues: Current obstacles or dependencies
#   - Notes/Context: Additional relevant information
#
# CHECKPOINT CONTENT:
#   Each checkpoint includes:
#   1. Overview with timestamp and project info
#   2. Git status information (branch, commits, file states)
#   3. Modified files analysis with detailed tables
#   4. Work context from interactive prompts
#   5. Recent activity summary
#   6. Development environment details
#   7. Project structure overview
#   8. Resume instructions
#   9. GitHub Copilot context
#
# FILE ORGANIZATION:
#   - Storage Location: /workspace/checkpoints/
#   - Naming Convention: checkpoint_YYYYMMDD_HHMMSS.md
#   - Format: Markdown for easy reading and GitHub integration
#   - File Size: Typically 3-8KB depending on project state
#
# INTEGRATION BENEFITS:
#   - GitHub Copilot Enhancement: Provides rich context for AI assistance
#   - Team Collaboration: Enables seamless handoffs between developers
#   - Progress Tracking: Maintains historical record of development progression
#   - Issue Resolution: Documents blockers and their resolution over time
#   - Development Continuity: Reduces context switching overhead
#
# REQUIREMENTS:
#   - Git (for repository status and history)
#   - Write permissions to /workspace/checkpoints/ directory
#   - Optional: tree command for enhanced directory display
#
# EXIT CODES:
#   0 - Success
#   1 - Error (invalid arguments, file creation failure, etc.)
#
# BEST PRACTICES:
#   - Create checkpoints at natural stopping points
#   - Use descriptive context when prompted
#   - Review previous checkpoints when resuming work
#   - Clean up old checkpoints periodically
#   - Include blockers and dependencies for prioritization
#
# AUTHOR: Omega Project Team
# VERSION: 1.0
# CREATED: 2025-11-13
#
#===============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
CHECKPOINT_DIR="/workspace/checkpoints"
PROJECT_ROOT="/workspace"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
CHECKPOINT_FILE="$CHECKPOINT_DIR/checkpoint_$TIMESTAMP.md"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_section() {
    echo -e "${CYAN}[SECTION]${NC} $1"
}

# Function to create checkpoint directory if it doesn't exist
ensure_checkpoint_dir() {
    if [[ ! -d "$CHECKPOINT_DIR" ]]; then
        mkdir -p "$CHECKPOINT_DIR"
        log_info "Created checkpoint directory: $CHECKPOINT_DIR"
    fi
}

# Function to get Git status information
get_git_status() {
    local git_info=""
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git_info+="**Current Branch**: $(git branch --show-current 2>/dev/null || echo 'detached HEAD')\n"
        git_info+="**Latest Commit**: $(git log -1 --format='%h - %s (%cr by %an)' 2>/dev/null || echo 'No commits')\n"
        git_info+="**Remote URL**: $(git remote get-url origin 2>/dev/null || echo 'No remote configured')\n"
        git_info+="**Repository Status**: $(git status --porcelain | wc -l) modified files\n"
        
        # Check if there are staged changes
        if git diff --cached --quiet; then
            git_info+="**Staged Changes**: None\n"
        else
            git_info+="**Staged Changes**: $(git diff --cached --name-only | wc -l) files staged\n"
        fi
        
        # Check if there are unstaged changes
        if git diff --quiet; then
            git_info+="**Unstaged Changes**: None\n"
        else
            git_info+="**Unstaged Changes**: $(git diff --name-only | wc -l) files modified\n"
        fi
        
        # Check for untracked files
        local untracked_count=$(git ls-files --others --exclude-standard | wc -l)
        git_info+="**Untracked Files**: $untracked_count files\n"
        
    else
        git_info+="**Git Status**: Not a git repository or git not available\n"
    fi
    
    echo -e "$git_info"
}

# Function to get modified files with details
get_modified_files() {
    local modified_info=""
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Get staged files
        if ! git diff --cached --quiet; then
            modified_info+="### Staged Files\n\n"
            modified_info+="| File | Status |\n"
            modified_info+="|------|--------|\n"
            git diff --cached --name-status | while read -r status file; do
                case $status in
                    A) status_desc="Added" ;;
                    M) status_desc="Modified" ;;
                    D) status_desc="Deleted" ;;
                    R*) status_desc="Renamed" ;;
                    C*) status_desc="Copied" ;;
                    *) status_desc="$status" ;;
                esac
                modified_info+="| \`$file\` | $status_desc |\n"
            done
            modified_info+="\n"
        fi
        
        # Get unstaged files
        if ! git diff --quiet; then
            modified_info+="### Unstaged Files\n\n"
            modified_info+="| File | Status |\n"
            modified_info+="|------|--------|\n"
            git diff --name-status | while read -r status file; do
                case $status in
                    M) status_desc="Modified" ;;
                    D) status_desc="Deleted" ;;
                    *) status_desc="$status" ;;
                esac
                modified_info+="| \`$file\` | $status_desc |\n"
            done
            modified_info+="\n"
        fi
        
        # Get untracked files
        local untracked_files=$(git ls-files --others --exclude-standard)
        if [[ -n "$untracked_files" ]]; then
            modified_info+="### Untracked Files\n\n"
            echo "$untracked_files" | while read -r file; do
                modified_info+="- \`$file\`\n"
            done
            modified_info+="\n"
        fi
        
        if [[ -z "$modified_info" ]]; then
            modified_info="No modified files detected.\n"
        fi
    else
        modified_info="Git not available - cannot determine modified files.\n"
    fi
    
    echo -e "$modified_info"
}

# Function to get project structure overview
get_project_structure() {
    local structure=""
    
    if command -v tree >/dev/null 2>&1; then
        structure+="$(tree -L 3 -I 'node_modules|.git|__pycache__|*.pyc|.venv|spring-modulith' "$PROJECT_ROOT" 2>/dev/null || echo 'Tree command failed')\n"
    else
        structure+="Tree command not available. Using ls instead:\n\n"
        structure+="$(ls -la "$PROJECT_ROOT" 2>/dev/null | head -20 || echo 'ls command failed')\n"
    fi
    
    echo -e "$structure"
}

# Function to get recent activity summary
get_recent_activity() {
    local activity=""
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        activity+="### Recent Commits (Last 5)\n\n"
        git log --oneline -5 2>/dev/null | while read -r commit; do
            activity+="- $commit\n"
        done || activity+="No recent commits available\n"
        activity+="\n"
        
        activity+="### Recent File Changes\n\n"
        git log --name-only --pretty=format:"**%h** - %s (%cr)" -3 2>/dev/null | head -20 | while read -r line; do
            if [[ $line == **/* ]]; then
                activity+="$line\n"
            elif [[ -n $line ]]; then
                activity+="  - \`$line\`\n"
            fi
        done || activity+="No recent file changes available\n"
    else
        activity+="Git not available - cannot determine recent activity.\n"
    fi
    
    echo -e "$activity"
}

# Function to get development environment info
get_environment_info() {
    local env_info=""
    
    env_info+="**Operating System**: $(uname -s) $(uname -r)\n"
    env_info+="**Shell**: $SHELL\n"
    env_info+="**Python Version**: $(python3 --version 2>/dev/null || echo 'Python not available')\n"
    env_info+="**Git Version**: $(git --version 2>/dev/null || echo 'Git not available')\n"
    env_info+="**Docker Status**: $(docker --version 2>/dev/null || echo 'Docker not available')\n"
    
    # Check for virtual environment
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        env_info+="**Virtual Environment**: Active at $VIRTUAL_ENV\n"
    elif [[ -d "$PROJECT_ROOT/.venv" ]]; then
        env_info+="**Virtual Environment**: Available at $PROJECT_ROOT/.venv (not activated)\n"
    else
        env_info+="**Virtual Environment**: Not detected\n"
    fi
    
    # Check workspace type
    if [[ -f "$PROJECT_ROOT/.devcontainer/devcontainer.json" ]]; then
        env_info+="**Development Environment**: Dev Container\n"
    else
        env_info+="**Development Environment**: Local\n"
    fi
    
    echo -e "$env_info"
}

# Function to prompt for current work context
get_work_context() {
    local context=""
    
    echo
    log_section "Capturing Current Work Context"
    echo "Please provide information about your current work (press Enter to skip any field):"
    echo
    
    read -p "Current Epic/Feature: " current_epic
    read -p "Current Task/Issue: " current_task
    read -p "Task Status (e.g., in-progress, blocked, testing): " task_status
    read -p "Next Planned Tasks: " next_tasks
    read -p "Blockers/Issues: " blockers
    read -p "Notes/Context: " notes
    
    context+="**Current Epic/Feature**: ${current_epic:-Not specified}\n"
    context+="**Current Task**: ${current_task:-Not specified}\n"
    context+="**Task Status**: ${task_status:-Not specified}\n"
    context+="**Next Planned Tasks**: ${next_tasks:-Not specified}\n"
    context+="**Blockers/Issues**: ${blockers:-None reported}\n"
    context+="**Additional Notes**: ${notes:-None}\n"
    
    echo -e "$context"
}

# Function to generate resume instructions
generate_resume_instructions() {
    local instructions=""
    
    instructions+="1. **Environment Setup**\n"
    instructions+="   - Ensure you're in the project root: \`cd $PROJECT_ROOT\`\n"
    instructions+="   - Activate virtual environment if available: \`source .venv/bin/activate\`\n"
    instructions+="   - Check Git status: \`git status\`\n\n"
    
    instructions+="2. **Review Changes**\n"
    instructions+="   - Review modified files listed above\n"
    instructions+="   - Check recent commits: \`git log --oneline -5\`\n"
    instructions+="   - Examine current branch status\n\n"
    
    instructions+="3. **Context Recovery**\n"
    instructions+="   - Review the work context section above\n"
    instructions+="   - Check project documentation in \`/docs\` directory\n"
    instructions+="   - Review tools available in \`/tools\` directory\n\n"
    
    instructions+="4. **Continue Development**\n"
    instructions+="   - Address any blockers mentioned above\n"
    instructions+="   - Continue with next planned tasks\n"
    instructions+="   - Use GitHub Copilot with project context from \`.github/copilot-instructions.md\`\n\n"
    
    instructions+="5. **Reference Resources**\n"
    instructions+="   - Project README: \`/workspace/README.md\`\n"
    instructions+="   - Documentation: \`/workspace/docs/\`\n"
    instructions+="   - Tools: \`/workspace/tools/\`\n"
    instructions+="   - GitHub Prompts: \`/workspace/.github/prompts/\`\n"
    
    echo -e "$instructions"
}

# Main checkpoint creation function
create_checkpoint() {
    log_info "Creating project checkpoint..."
    
    # Ensure checkpoint directory exists
    ensure_checkpoint_dir
    
    # Get work context from user
    local work_context=$(get_work_context)
    
    # Create checkpoint file
    cat > "$CHECKPOINT_FILE" << EOF
# Omega Project Checkpoint - $(date '+%Y-%m-%d %H:%M:%S')

## Overview
This checkpoint captures the current state of the Omega agentic migration system project for resuming development work with GitHub Copilot.

**Checkpoint Created**: $(date '+%Y-%m-%d %H:%M:%S %Z')
**Project**: Omega - Agentic Software Migration System
**Repository**: ea-datascience/omega

## Git Status Information

$(get_git_status)

## Modified Files

$(get_modified_files)

## Work Context

$(echo -e "$work_context")

## Recent Activity

$(get_recent_activity)

## Development Environment

$(get_environment_info)

## Project Structure

\`\`\`
$(get_project_structure)
\`\`\`

## Resume Instructions

$(generate_resume_instructions)

## Additional Context for GitHub Copilot

### Project Goals
- Demonstrate migration workflows from monoliths to microservices
- Provide intelligent automation through agentic systems
- Establish best practices for microservices decomposition
- Enable practical implementation with real-world tools

### Key Directories
- \`/data/codebase/\` - Reference codebases (Spring Modulith)
- \`/docs/\` - Project documentation
- \`/tools/\` - Migration utilities and scripts
- \`/.github/\` - GitHub workflows and prompts

### Current Development Phase
The project is in its initial phase focusing on:
- Development container environment
- Git workflow and documentation framework
- Tools directory structure for migration utilities
- Reference codebase integration

---

*Generated by: $0 at $(date '+%Y-%m-%d %H:%M:%S')*
*Next checkpoint recommended after significant progress or before extended breaks*
EOF

    log_success "Checkpoint created successfully!"
    log_info "Checkpoint saved to: $CHECKPOINT_FILE"
    
    # Show file size and preview
    local file_size=$(du -h "$CHECKPOINT_FILE" | cut -f1)
    log_info "Checkpoint size: $file_size"
    
    echo
    log_section "Checkpoint Preview (first 10 lines):"
    head -10 "$CHECKPOINT_FILE" | sed 's/^/  /'
    echo "  ..."
    echo
    
    log_info "To view full checkpoint: cat $CHECKPOINT_FILE"
    log_info "To list all checkpoints: ls -la $CHECKPOINT_DIR"
}

# Function to list existing checkpoints
list_checkpoints() {
    if [[ -d "$CHECKPOINT_DIR" ]] && [[ -n "$(ls -A "$CHECKPOINT_DIR" 2>/dev/null)" ]]; then
        log_section "Existing Checkpoints:"
        ls -la "$CHECKPOINT_DIR"/*.md 2>/dev/null | while read -r line; do
            echo "  $line"
        done
    else
        log_info "No existing checkpoints found."
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -l, --list     List existing checkpoints"
    echo "  -c, --create   Create new checkpoint (default)"
    echo
    echo "Examples:"
    echo "  $0                    # Create new checkpoint"
    echo "  $0 --create          # Create new checkpoint"
    echo "  $0 --list            # List existing checkpoints"
    echo
    echo "Checkpoint files are saved to: $CHECKPOINT_DIR"
}

# Main execution
main() {
    echo "========================================"
    echo "Omega Project Checkpoint Script"
    echo "========================================"
    
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -l|--list)
            list_checkpoints
            exit 0
            ;;
        -c|--create|"")
            create_checkpoint
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo "========================================"
    log_success "Checkpoint operation completed!"
    echo "========================================"
}

# Script entry point

# Function to show comprehensive help information
show_comprehensive_help() {
    cat << 'HELP_EOF'
=============================================================================
Project Checkpoint Creation Script - Comprehensive Help
=============================================================================

DESCRIPTION:
    This script creates comprehensive checkpoints for the Omega agentic migration
    system to facilitate resuming development sessions with GitHub Copilot.

USAGE:
    ./create-checkpoint.sh [OPTIONS]

OPTIONS:
    -h, --help              Show basic help message and exit
    --comprehensive-help    Show this comprehensive help information
    -c, --create            Create new checkpoint (default)
    -l, --list              List existing checkpoints

CHECKPOINT CONTENT STRUCTURE:
    Each checkpoint file includes:
    1. Overview Section       - Timestamp and project identification
    2. Git Status Information - Branch, commits, file states
    3. Modified Files Analysis - Detailed tables with status
    4. Work Context          - Interactive prompt responses
    5. Recent Activity       - Last commits and file changes
    6. Environment Details   - Development tools and versions
    7. Project Structure     - Directory overview
    8. Resume Instructions   - Step-by-step continuation guide
    9. Copilot Context       - AI assistance information

FILE ORGANIZATION:
    • Storage Location       - /workspace/checkpoints/
    • Naming Convention      - checkpoint_YYYYMMDD_HHMMSS.md
    • Format                 - Markdown for easy reading and GitHub integration

FOR MORE INFORMATION:
    • Project Documentation: /workspace/docs/
    • Tools Documentation: /workspace/tools/README.md
    • GitHub Repository: https://github.com/ea-datascience/omega

=============================================================================
HELP_EOF
}

# Script entry point with proper argument parsing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        --comprehensive-help)
            show_comprehensive_help
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -l|--list)
            list_checkpoints
            exit 0
            ;;
        -c|--create|"")
            create_checkpoint
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
fi
