# Reference Codebase Setup Guide

This guide documents the process of adding reference codebases to the Omega project for migration analysis and demonstration purposes.

## Overview

Reference codebases are external repositories that serve as examples for the agentic migration system. They are cloned locally for analysis but are not tracked in the project's version control to maintain repository cleanliness and avoid licensing issues.

## Spring Modulith Integration

The Spring Modulith project was selected as the primary reference codebase for demonstrating migration capabilities. Spring Modulith is particularly relevant as it focuses on modular monolith architectures, which are stepping stones to microservices.

### Repository Information
- **Source**: https://github.com/spring-projects/spring-modulith.git
- **Local Path**: `/workspace/data/codebase/spring-modulith/`
- **Purpose**: Reference codebase for migration analysis and testing
- **License**: Apache License 2.0 (Spring Projects)

## Setup Process

### Step 1: Create Data Directory Structure

First, establish the directory structure for storing reference data:

```bash
# Create main data directory
mkdir -p /workspace/data

# Create codebase subdirectory for reference repositories
mkdir -p /workspace/data/codebase
```

**Purpose**: Organize reference materials separate from project source code.

### Step 2: Clone Reference Repository

Clone the Spring Modulith repository into the designated location:

```bash
# Navigate to codebase directory
cd /workspace/data/codebase

# Clone the Spring Modulith repository
git clone https://github.com/spring-projects/spring-modulith.git
```

**Result**: 
- 35,254 objects downloaded
- 5.41 MiB of source code and documentation
- Complete Spring Boot modular monolith example

### Step 3: Configure Git Ignore Rules

Create/update `.gitignore` to exclude reference repositories from version control:

```bash
# Create .gitignore in project root
touch /workspace/.gitignore
```

Add the following exclusion rules to `.gitignore`:

```gitignore
# Data directory - reference codebases and datasets
data/codebase/spring-modulith/

# Python virtual environment
.venv/

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
```

**Purpose**: Prevent tracking of reference repositories while maintaining comprehensive ignore rules for development artifacts.

### Step 4: Commit Git Ignore Configuration

Stage and commit the `.gitignore` file:

```bash
# Navigate to project root
cd /workspace

# Stage the .gitignore file
git add .gitignore

# Commit with descriptive message
git commit -m "Add comprehensive .gitignore

- Exclude spring-modulith reference repository from tracking
- Ignore Python virtual environment and cache files
- Exclude IDE settings and system files
- Prevent tracking of build artifacts and logs
- Maintain clean repository focused on Omega project files"

# Push to remote repository
git push
```

**Result**: Clean repository with reference codebase properly excluded from version control.

## Verification

### Confirm Directory Structure
```bash
tree /workspace/data -L 3
```

Expected output:
```
/workspace/data
└── codebase
    └── spring-modulith
        ├── build.gradle
        ├── gradle/
        ├── src/
        └── [additional Spring Modulith files]
```

### Verify Git Ignore Status
```bash
git status
```

Should show clean working directory with no untracked files from the reference repository.

### Test Reference Repository Access
```bash
ls -la /workspace/data/codebase/spring-modulith/
```

Should display the Spring Modulith project structure and files.

## Usage Guidelines

### For Analysis
- Reference repositories are read-only for analysis purposes
- Do not modify files within reference repositories
- Use relative paths when referencing files in analysis scripts

### For Documentation
- Document any insights or findings in separate analysis files
- Create summaries and migration plans in the `/docs` directory
- Reference specific files or patterns using relative paths

### For Updates
To update reference repositories:
```bash
cd /workspace/data/codebase/spring-modulith
git pull origin main
```

## Security Considerations

- Reference repositories maintain their original licensing
- No modifications should be made to reference code
- Exclude reference repositories from any project distributions
- Respect original repository licenses and attribution requirements

## Adding Additional Reference Codebases

To add more reference repositories:

1. Clone into `/workspace/data/codebase/[repository-name]/`
2. Add exclusion rule to `.gitignore`: `data/codebase/[repository-name]/`
3. Update this documentation with new repository details
4. Commit the updated `.gitignore` file

## Troubleshooting

### Repository Not Ignored
If Git is tracking files from reference repositories:
```bash
# Remove from Git cache (doesn't delete files)
git rm -rf --cached data/codebase/spring-modulith/
git commit -m "Remove reference repository from tracking"
```

### Large Repository Size
Reference repositories are stored locally only and do not affect the project repository size on GitHub.

### Access Issues
Ensure you have internet connectivity when cloning reference repositories. Some repositories may require authentication for private access.

---

*This documentation ensures reproducible setup of reference codebases for the Omega agentic migration system.*