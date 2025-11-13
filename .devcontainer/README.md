# Development Container Setup

This dev container provides a minimal, extensible development environment optimized for modern Python development workflows.

## Architecture & Design Philosophy

### **Container Orchestration Strategy**
- **Docker Compose**: Used for service orchestration, providing flexibility to add supporting services (databases, caches, etc.) without rebuilding the main container
- **Single Development Container**: GitHub Copilot and VS Code operate within the `app` service container
- **Scalable Foundation**: Easy to extend with additional services while maintaining development environment isolation

### **Why Docker Compose Over Single Dockerfile?**
- **Service Isolation**: Supporting services run in parallel containers
- **Environment Consistency**: Reproducible multi-service environments across team members
- **Development Flexibility**: Can start/stop individual services independently
- **Production Similarity**: Mirrors deployment architecture patterns
- **Alternative to Docker-in-Docker**: Provides orchestrated services without complex nested Docker setups

## What's Included

### **Base Environment**
- **Ubuntu 22.04** - Stable, well-supported base image
- **Basic System Utilities**: curl, wget, jq, vim, nano, tree, git
- **Minimal Resource Footprint**: Only essential tools included

### **Python Development Stack**
- **uv Package Manager** - Ultra-fast Rust-based Python package manager
  - **Standalone installation** - No system Python required
  - **Python version management** - Installs and manages Python versions
  - **10-100x faster** than traditional pip
  - **Modern pyproject.toml** workflow support
  - **Lockfile generation** for reproducible environments
  - **Virtual environment management** built-in

### **Development Tools**
- **VS Code Integration**: Pre-configured with essential extensions
  - JSON/YAML support for configuration files
  - GitLens for enhanced Git workflows
- **Git & GitHub CLI**: Version control and repository management
- **Extensible Configuration**: Easy to add language-specific tools

## Container Architecture

```
┌─────────────────────────────────────┐
│           VS Code + Copilot         │
│              (Host)                 │
│                                     │
│  omega/ (current directory)         │
└─────────────┬───────────────────────┘
              │ mounted to
┌─────────────▼───────────────────────┐
│        app container                │
│      (Ubuntu + uv)                  │
│                                     │
│  /workspace ← omega/ mounted here   │
│  /workspaces ← full workspace tree  │
└─────────────────────────────────────┘
              │ can orchestrate
┌─────────────▼───────────────────────┐
│       Future Services               │
│   (databases, caches, etc.)         │
│     via Docker Compose              │
└─────────────────────────────────────┘
```

## Getting Started

1. **Prerequisites**: Install VS Code Dev Containers extension
2. **Open Container**: VS Code will prompt to reopen in container
3. **Initial Build**: First run builds the container (1-2 minutes)
4. **Development Ready**: Clean Python environment with uv available

## Current Configuration

### **Container Lifecycle Hooks**
- **`postCreateCommand`** - Installs Python 3.12 and creates `.venv` virtual environment (runs once)
- **`postAttachCommand`** - Checks virtual environment status and provides feedback (runs on each VS Code attach)
- **Automatic Environment Activation** - Multi-layered strategy ensures Python environment is always available

### **Services & Dependencies**
- **Single container setup** - Only the `app` service runs
- **No external services** - Databases, caches, etc. can be added via docker-compose
- **Minimal system footprint** - Ubuntu base with essential utilities only

### **Volume Mounts**
- **Primary Workspace** - Current directory (`omega/`) mounted to `/workspace` via `devcontainer.json`
- **Parent Workspaces** - Full workspace tree mounted to `/workspaces` via `docker-compose.yml`
- **Mount Configuration**:
  - **devcontainer.json**: `${localWorkspaceFolder}` → `/workspace` (bind mount, cached)
  - **docker-compose.yml**: `../..` → `/workspaces` (volume mount, cached)
- **Performance Optimization** - Cached consistency for improved file operations on macOS/Windows

## Python Development with uv

### **Automatic Environment Activation**
The container is configured to automatically activate the Python 3.12 virtual environment in all new terminals through:

1. **Shell Profile Integration** - `.bashrc` and `.zshrc` automatically source `.venv/bin/activate`
2. **VS Code Python Settings** - Configured to use `/workspace/.venv/bin/python` as default interpreter
3. **Terminal Activation** - VS Code terminals automatically activate the environment
4. **Status Feedback** - `postAttachCommand` provides environment status on each connection

### **uv Commands**
```bash
# The environment is automatically activated, but you can also use:

# Add dependencies (environment auto-activated)
uv add requests pandas fastapi

# Add development dependencies  
uv add --dev pytest black pylint

# Install from existing pyproject.toml
uv sync

# Run with uv-managed Python environment
uv run python your_script.py

# Manual activation (if needed)
source .venv/bin/activate

# Check available Python versions
uv python list
```

## Extending the Environment

### **Adding System Packages**
Edit `Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y \
    your-package-here \
    && apt-get clean
```

### **Adding Supporting Services**
Edit `docker-compose.yml`:
```yaml
services:
  app:
    # existing config
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: dev
```

### **Adding VS Code Extensions**
Edit `devcontainer.json`:
```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

### **Adding Additional Mounts**
Edit `devcontainer.json`:
```json
"mounts": [
  "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
  "source=${localWorkspaceFolder}/data,target=/app/data,type=bind"
]
```

## Design Decisions & Rationale

### **Minimal Base Approach**
- **Started Comprehensive**: Initially included full database stack, Python packages, multiple extensions
- **Stripped to Essentials**: Removed databases, heavy Python installations, complex tooling
- **Added Back Selectively**: Only uv package manager for modern Python workflow
- **Reasoning**: Provides clean foundation while enabling rapid iteration and customization

### **uv Package Manager Choice**
- **Standalone Architecture**: No system Python required - uv manages everything
- **Python Version Management**: Installs and switches between Python versions
- **Performance**: Significantly faster than pip for package operations
- **Modern Workflow**: Native pyproject.toml support, lockfiles, virtual environment management
- **Future-Proof**: Rust-based tool gaining widespread adoption in Python ecosystem
- **Complete Toolchain**: Replaces pip, virtualenv, pyenv, and pip-tools

### **Container vs Compose Trade-offs**
- **Could Use Single Container**: Simpler for truly standalone development
- **Chose Compose**: Anticipates need for supporting services in migration projects
- **Flexibility**: Easy to add databases, queues, APIs without container rebuilds
- **Team Consistency**: Reproducible multi-service environments

### **Mount Strategy**
- **Separation of Concerns**: Project-specific mounts in `devcontainer.json`, infrastructure mounts in `docker-compose.yml`
- **VS Code Integration**: `${localWorkspaceFolder}` variable ensures proper workspace detection
- **Performance**: Bind mounts with cached consistency for optimal file system performance
- **Flexibility**: Easy to add additional mounts for specific project needs

### **Python Environment Strategy**
- **Triple-Layer Activation**: Shell profiles + VS Code settings + lifecycle hooks ensure environment is always available
- **Automatic Detection**: Smart activation only occurs when `.venv` exists
- **GitHub Copilot Integration**: New terminals automatically have the Python environment active
- **Fallback Support**: Multiple activation methods provide redundancy and reliability

This setup provides a clean, fast, and extensible foundation for Python development while maintaining the flexibility to scale complexity as project needs evolve.̉