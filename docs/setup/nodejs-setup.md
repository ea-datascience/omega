# Node.js Setup for Omega Dashboard

## Overview

The Omega dashboard frontend is built with Angular 17, which requires Node.js 20 LTS and npm for development and build processes.

## Installation

Node.js 20 LTS is automatically installed in the dev container via the Dockerfile configuration.

### Version Requirements

- **Node.js**: 20.x LTS (Long Term Support)
- **npm**: 10.x (bundled with Node.js 20)
- **Angular CLI**: ^17.0.0 (installed via npm)

### Automated Installation

The dev container Dockerfile (`/workspace/.devcontainer/Dockerfile`) includes Node.js installation:

```dockerfile
# Install Node.js 20 LTS from NodeSource
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*
```

This approach follows the Omega constitution requirements:
- Scripted installation (via Dockerfile)
- Version pinning (Node.js 20.x LTS)
- Reproducible across all developer environments
- No ad-hoc manual installations

## Verification

After rebuilding the dev container, verify the installation:

```bash
# Check Node.js version
node --version
# Expected: v20.x.x

# Check npm version
npm --version
# Expected: 10.x.x

# Check Angular CLI (after npm install)
cd /workspace/dashboard
npm install
npx ng version
```

## Dashboard Dependencies

Install dashboard dependencies from package.json:

```bash
cd /workspace/dashboard
npm install
```

This will install:
- Angular 17 framework and CLI
- Angular Material components
- Chart.js and D3.js for visualizations
- Monaco Editor for code viewing
- SignalR for real-time updates
- Development tools (TypeScript, ESLint)

## Development Workflow

### Start Development Server

```bash
cd /workspace/dashboard
npm start
# Dashboard will be available at http://localhost:4200
```

### Build for Production

```bash
cd /workspace/dashboard
npm run build
# Output in /workspace/dashboard/dist/
```

### Run Tests

```bash
cd /workspace/dashboard
npm test
# Runs Jasmine/Karma tests

npm run test:ci
# Runs tests in CI mode (headless Chrome)
```

### Linting

```bash
cd /workspace/dashboard
npm run lint
# Runs ESLint with TypeScript rules
```

## Rebuilding Dev Container

After updating the Dockerfile, rebuild the dev container:

1. In VS Code, press `F1` or `Cmd+Shift+P`
2. Select "Dev Containers: Rebuild Container"
3. Wait for container rebuild to complete
4. Verify Node.js installation: `node --version`

## Troubleshooting

### Node.js not found after rebuild

```bash
# Check if Node.js is installed
which node

# Verify PATH includes Node.js
echo $PATH

# If missing, rebuild container completely
# In VS Code: "Dev Containers: Rebuild Container Without Cache"
```

### npm install fails

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
cd /workspace/dashboard
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Angular CLI not found

```bash
# Install globally (optional, not recommended)
npm install -g @angular/cli

# Use npx instead (recommended)
npx ng version
npx ng serve
```

## Related Files

- `/workspace/.devcontainer/Dockerfile` - Dev container configuration with Node.js installation
- `/workspace/dashboard/package.json` - Dashboard dependencies and scripts
- `/workspace/dashboard/.eslintrc.json` - ESLint configuration for TypeScript
- `/workspace/docs/omega-constitution.md` - Reproducibility standards
