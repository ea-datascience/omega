---
agent: agent
---

# Clone Reference Codebase Command

This prompt serves as a wrapper to execute the Spring Modulith reference codebase cloning operation for the Omega agentic migration system.

## Task Definition

Execute the automated cloning of the Spring Modulith reference repository using the dedicated bash script, ensuring proper setup for migration analysis and demonstration purposes.

## Requirements

### Primary Objective
- Execute `/workspace/tools/src/clone-spring-modulith.sh` to clone the Spring Modulith repository
- Ensure idempotent operation that handles existing repositories correctly
- Verify successful completion and repository validation

### Specific Requirements
1. **Script Execution**: Run the clone-spring-modulith.sh script from the tools directory
2. **Idempotent Operation**: Handle existing repositories by removing and re-cloning for freshness
3. **Validation**: Confirm repository structure, remote URL, and basic file integrity
4. **Status Reporting**: Provide clear feedback on operation success/failure
5. **Directory Management**: Ensure proper directory structure creation if needed

### Constraints
- Must use the existing bash script at `/workspace/tools/src/clone-spring-modulith.sh`
- Repository must be cloned to `/workspace/data/codebase/spring-modulith/`
- Source repository: `https://github.com/spring-projects/spring-modulith.git`
- Must respect .gitignore rules (cloned repo should not be tracked)
- Should not modify the source script unless explicitly requested

### Success Criteria
1. **Script Execution**: Successfully runs without errors
2. **Repository Cloned**: Spring Modulith repository exists at target location
3. **Structure Validated**: Required directories and files are present  
4. **Git Status Clean**: Repository properly excluded from version control
5. **Information Display**: Shows repository metadata (size, branch, last commit)

## Expected Workflow

1. **Pre-execution Check**: Verify script exists and is executable
2. **Script Execution**: Run the clone-spring-modulith.sh script
3. **Monitor Output**: Capture and interpret script logging output
4. **Validate Results**: Confirm successful repository setup
5. **Report Status**: Provide summary of operation results

## Error Handling

If the script fails:
- Report specific error messages from the script output
- Check script permissions and existence
- Verify network connectivity for Git operations
- Suggest corrective actions based on failure type

## Usage Context

This prompt is designed for operators who need to:
- Set up the reference codebase for migration analysis
- Refresh the Spring Modulith repository to latest version  
- Troubleshoot repository setup issues
- Verify proper reference codebase configuration

## Integration Notes

- This operation is independent of main project version control
- Cloned repository serves as read-only reference material
- Script includes comprehensive logging and error handling
- Operation can be safely repeated multiple times (idempotent)

## Validation Commands

After script execution, run these commands to ensure proper setup and validate success criteria:

### 1. Repository Structure Validation
```bash
# Verify repository exists and basic structure
ls -la /workspace/data/codebase/spring-modulith/ | head -10

# Check repository size
du -sh /workspace/data/codebase/spring-modulith/
```

### 2. Git Configuration Validation
```bash
# Verify remote URL is correct
cd /workspace/data/codebase/spring-modulith && git remote get-url origin

# Check current branch
cd /workspace/data/codebase/spring-modulith && git branch --show-current

# Get last commit information
cd /workspace/data/codebase/spring-modulith && git log -1 --format='%h - %s (%cr)'
```

### 3. Version Control Exclusion Validation
```bash
# Ensure repository is properly excluded from Omega project tracking
git status --porcelain | grep -c spring-modulith || echo "Repository properly excluded from Git tracking"

# Verify .gitignore is working
git check-ignore /workspace/data/codebase/spring-modulith/ && echo ".gitignore rule active" || echo "WARNING: Repository not ignored"
```

### 4. Repository Integrity Validation
```bash
# Verify it's a valid git repository
cd /workspace/data/codebase/spring-modulith && git status --porcelain

# Check for key Spring Modulith files
ls -1 /workspace/data/codebase/spring-modulith/ | grep -E "(src|pom\.xml|build\.gradle|gradle)" | head -5
```

### 5. Network and Freshness Validation
```bash
# Verify repository is up to date (optional - requires network)
cd /workspace/data/codebase/spring-modulith && git fetch --dry-run origin main 2>&1 | grep -q "up to date" && echo "Repository is current" || echo "Updates available"
```

## Success Validation Checklist

Confirm all these conditions are met:

- [ ] **Script Execution**: Command completed without errors (exit code 0)
- [ ] **Directory Exists**: `/workspace/data/codebase/spring-modulith/` directory is present
- [ ] **Git Repository**: Directory contains `.git` folder and is valid repository
- [ ] **Correct Remote**: Remote URL is `https://github.com/spring-projects/spring-modulith.git`
- [ ] **Current Branch**: Repository is on `main` branch
- [ ] **Recent Commit**: Last commit is recent (within reasonable timeframe)
- [ ] **Proper Size**: Repository size is approximately 12M
- [ ] **Git Ignored**: Repository is excluded from Omega project version control
- [ ] **File Structure**: Basic Spring project structure is present (src/, build files)
- [ ] **Network Fresh**: Repository represents latest version from GitHub

## Execute the Task

Run the Spring Modulith cloning script and execute the validation commands to report comprehensive results: