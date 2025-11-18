#!/bin/bash

#===============================================================================
# Project Checkpoint Creation Script (JSON Output)
#===============================================================================
#
# DESCRIPTION:
#   Creates comprehensive checkpoints in JSON format for the Omega agentic 
#   migration system. Eliminates interactive mode and accepts context via
#   command-line arguments.
#
# USAGE:
#   ./create-checkpoint.sh [OPTIONS]
#   
# OPTIONS:
#   -e, --epic TEXT        Current epic/feature
#   -t, --task TEXT        Current task/issue  
#   -s, --status TEXT      Task status (in-progress, blocked, testing, etc.)
#   -n, --next TEXT        Next planned tasks
#   -b, --blockers TEXT    Current blockers/issues
#   --notes TEXT           Additional notes/context
#   -h, --help             Show help
#   -l, --list             List existing checkpoints
#   -f, --format FORMAT    Output format: json (default) or markdown
#
# EXAMPLES:
#   ./create-checkpoint.sh -e "Tool Development" -t "Fix script bugs" -s "in-progress"
#   ./create-checkpoint.sh --epic "Migration Analysis" --task "Spring Modulith integration"
#
#===============================================================================

set -euo pipefail

# Configuration
CHECKPOINT_DIR="/workspace/checkpoints"
PROJECT_ROOT="/workspace"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_FORMAT="json"
CHECKPOINT_FILE="$CHECKPOINT_DIR/checkpoint_$TIMESTAMP.json"

# Default context values
CURRENT_EPIC=""
CURRENT_TASK=""
TASK_STATUS=""
NEXT_TASKS=""
BLOCKERS=""
NOTES=""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to escape JSON strings
escape_json() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g; s/\r/\\r/g' | tr '\n' ' ' | sed 's/\x1b\[[0-9;]*m//g'
}

# Function to get Git status as JSON
get_git_status_json() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        local remote_url=$(git remote get-url origin 2>/dev/null || echo "none")
        local last_commit=$(git log -1 --format='%h - %s (%cr)' 2>/dev/null || echo "none")
        local staged_count=$(git diff --cached --name-only | wc -l)
        local unstaged_count=$(git diff --name-only | wc -l)
        local untracked_count=$(git ls-files --others --exclude-standard | wc -l)
        
        cat << JSON
{
  "is_git_repo": true,
  "branch": "$(escape_json "$branch")",
  "remote_url": "$(escape_json "$remote_url")",
  "last_commit": "$(escape_json "$last_commit")",
  "staged_files": $staged_count,
  "unstaged_files": $unstaged_count,
  "untracked_files": $untracked_count
}
JSON
    else
        echo '{"is_git_repo": false}'
    fi
}

# Function to get modified files as JSON
get_modified_files_json() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "{"
        echo '  "staged": ['
        
        local staged_files=($(git diff --cached --name-only 2>/dev/null || true))
        for i in "${!staged_files[@]}"; do
            local file="${staged_files[$i]}"
            local status=$(git diff --cached --name-status "$file" | cut -f1)
            echo -n "    {\"file\": \"$(escape_json "$file")\", \"status\": \"$status\"}"
            [[ $i -lt $((${#staged_files[@]} - 1)) ]] && echo "," || echo
        done
        
        echo '  ],'
        echo '  "unstaged": ['
        
        local unstaged_files=($(git diff --name-only 2>/dev/null || true))
        for i in "${!unstaged_files[@]}"; do
            local file="${unstaged_files[$i]}"
            echo -n "    {\"file\": \"$(escape_json "$file")\", \"status\": \"M\"}"
            [[ $i -lt $((${#unstaged_files[@]} - 1)) ]] && echo "," || echo
        done
        
        echo '  ],'
        echo '  "untracked": ['
        
        local untracked_files=($(git ls-files --others --exclude-standard 2>/dev/null || true))
        for i in "${!untracked_files[@]}"; do
            local file="${untracked_files[$i]}"
            echo -n "    \"$(escape_json "$file")\""
            [[ $i -lt $((${#untracked_files[@]} - 1)) ]] && echo "," || echo
        done
        
        echo '  ]'
        echo "}"
    else
        echo '{"staged": [], "unstaged": [], "untracked": []}'
    fi
}

# Function to get environment info as JSON
get_environment_info_json() {
    local git_version=$(git --version 2>/dev/null | cut -d' ' -f3 || echo "not installed")
    local python_version=""
    if command -v python3 > /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    else
        python_version="not installed"
    fi
    
    cat << JSON
{
  "shell": "$SHELL",
  "pwd": "$(pwd)",
  "git_version": "$(escape_json "$git_version")",
  "python_version": "$(escape_json "$python_version")",
  "user": "$USER",
  "hostname": "$HOSTNAME"
}
JSON
}

# Function to get project structure as JSON
get_project_structure_json() {
    if command -v tree > /dev/null; then
        local tree_output=$(cd "$PROJECT_ROOT" && tree -L 2 -a -I '.git|.venv|__pycache__|*.pyc|data' 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' || echo "tree command failed")
        echo "\"$(escape_json "$tree_output")\""
    else
        local ls_output=$(cd "$PROJECT_ROOT" && ls -la | head -10 | tr '\n' ';')
        echo "\"$(escape_json "$ls_output")\""
    fi
}

# Function to generate resume instructions as JSON
generate_resume_instructions_json() {
    cat << 'JSON'
[
  "Ensure you're in the project root: cd /workspace",
  "Activate virtual environment if available: source .venv/bin/activate",
  "Check Git status: git status",
  "Review modified files listed in this checkpoint",
  "Check recent commits: git log --oneline -5",
  "Review the work context for current tasks and blockers",
  "Check project documentation in /docs directory",
  "Review tools available in /tools directory",
  "Use GitHub Copilot with context from .github/copilot-instructions.md"
]
JSON
}

# Function to create JSON checkpoint
create_checkpoint() {
    mkdir -p "$CHECKPOINT_DIR"
    
    log_info "Creating project checkpoint..."
    
    # Create JSON checkpoint content
    cat > "$CHECKPOINT_FILE" << EOF
{
  "checkpoint": {
    "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
    "created_by": "$0",
    "version": "2.0",
    "format": "json"
  },
  "project": {
    "name": "Omega - Agentic Software Migration System",
    "repository": "ea-datascience/omega",
    "root_path": "$PROJECT_ROOT"
  },
  "git_status": $(get_git_status_json),
  "modified_files": $(get_modified_files_json),
  "work_context": {
    "current_epic": "$(escape_json "$CURRENT_EPIC")",
    "current_task": "$(escape_json "$CURRENT_TASK")",
    "task_status": "$(escape_json "$TASK_STATUS")",
    "next_tasks": "$(escape_json "$NEXT_TASKS")",
    "blockers": "$(escape_json "$BLOCKERS")",
    "notes": "$(escape_json "$NOTES")"
  },
  "environment": $(get_environment_info_json),
  "project_structure": $(get_project_structure_json),
  "resume_instructions": $(generate_resume_instructions_json),
  "copilot_context": {
    "project_goals": [
      "Demonstrate migration workflows from monoliths to microservices",
      "Provide intelligent automation through agentic systems", 
      "Establish best practices for microservices decomposition",
      "Enable practical implementation with real-world tools"
    ],
    "key_directories": {
      "/data/codebase/": "Reference codebases (Spring Modulith)",
      "/docs/": "Project documentation",
      "/tools/": "Migration utilities and scripts",
      "/.github/": "GitHub workflows and prompts"
    },
    "current_phase": "Initial phase focusing on development environment, Git workflow, tools structure, and reference codebase integration"
  }
}
EOF

    log_success "Checkpoint created successfully!"
    log_info "Checkpoint saved to: $CHECKPOINT_FILE"
    
    local file_size=$(du -h "$CHECKPOINT_FILE" | cut -f1)
    log_info "Checkpoint size: $file_size"
    
    # Validate JSON
    if command -v jq > /dev/null; then
        if jq empty "$CHECKPOINT_FILE" 2>/dev/null; then
            log_success "JSON validation passed"
        else
            log_warning "JSON validation failed - file may be malformed"
        fi
    fi
}

# Function to list existing checkpoints
list_checkpoints() {
    if [[ -d "$CHECKPOINT_DIR" ]]; then
        echo "Existing checkpoints:"
        ls -la "$CHECKPOINT_DIR"/checkpoint_*.json 2>/dev/null || echo "No checkpoints found"
    else
        echo "Checkpoint directory does not exist: $CHECKPOINT_DIR"
    fi
}

# Function to show usage
show_usage() {
    cat << 'HELP_EOF'
Usage: create-checkpoint.sh [OPTIONS]

Create comprehensive project checkpoints in JSON format for development continuity.

OPTIONS:
  -e, --epic TEXT        Current epic/feature
  -t, --task TEXT        Current task/issue  
  -s, --status TEXT      Task status (in-progress, blocked, testing, etc.)
  -n, --next TEXT        Next planned tasks
  -b, --blockers TEXT    Current blockers/issues
  --notes TEXT           Additional notes/context
  -h, --help             Show this help message
  -l, --list             List existing checkpoints
  -f, --format FORMAT    Output format: json (default) or markdown

EXAMPLES:
  create-checkpoint.sh -e "Tool Development" -t "Fix script bugs" -s "in-progress"
  create-checkpoint.sh --epic "Migration Analysis" --task "Spring Modulith integration"
  create-checkpoint.sh --list

OUTPUT:
  Checkpoints are saved as JSON files in /workspace/checkpoints/
  Format: checkpoint_YYYYMMDD_HHMMSS.json
HELP_EOF
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--epic)
            CURRENT_EPIC="$2"
            shift 2
            ;;
        -t|--task)
            CURRENT_TASK="$2"
            shift 2
            ;;
        -s|--status)
            TASK_STATUS="$2"
            shift 2
            ;;
        -n|--next)
            NEXT_TASKS="$2"
            shift 2
            ;;
        -b|--blockers)
            BLOCKERS="$2"
            shift 2
            ;;
        --notes)
            NOTES="$2"
            shift 2
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -l|--list)
            list_checkpoints
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set checkpoint file extension based on format
if [[ "$OUTPUT_FORMAT" == "markdown" ]]; then
    CHECKPOINT_FILE="$CHECKPOINT_DIR/checkpoint_$TIMESTAMP.md"
fi

# Main execution
create_checkpoint