# CodeQL CLI Setup Guide

## Platform Limitation

**IMPORTANT:** CodeQL CLI is not currently supported in the Omega project's ARM64 development container environment.

### Issue

- **CodeQL Availability**: GitHub only provides x86-64 binaries for Linux systems
- **Dev Container**: Omega runs on ARM64 architecture
- **Emulation**: x86-64 binaries cannot run on ARM64 without full emulation (not available in our container)
- **Generic Package**: The 700MB+ generic package exceeds available disk space in dev container

### Affected Components

- **T025a**: CodeQL CLI installation task
- **Epic 1.1**: System Discovery Baseline

### Alternative Solutions

#### Option 1: Use GitHub Actions (Recommended)

Run CodeQL analysis via GitHub Actions on x86-64 runners:

```yaml
name: CodeQL Analysis
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest  # x86-64 runner
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: java
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

#### Option 2: Cloud-Based Analysis

Use GitHub Advanced Security with built-in CodeQL scanning:

- Enable in repository settings → Security → Code scanning
- Automatic analysis without local installation
- Results integrated into Security tab

#### Option 3: x86-64 Development Machine

For local CodeQL development:

- Use x86-64 Linux machine or VM
- Install CodeQL CLI following official documentation
- Download from: https://github.com/github/codeql-cli-binaries/releases

## CodeQL Installation (x86-64 Only)

For reference, here's the installation process for x86-64 systems:

### Prerequisites

- Java 17+ (required for CodeQL CLI)
- x86-64 Linux system
- ~510MB disk space for linux64 binary

### Installation Script

```bash
#!/bin/bash
# CodeQL CLI Installation for x86-64 Linux
# Source: /workspace/tools/src/utils/install-codeql.sh

CODEQL_VERSION="2.23.5"
CODEQL_URL="https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip"
INSTALL_DIR="/opt/codeql"

# Download
curl -LO "$CODEQL_URL"

# Extract
unzip codeql-linux64.zip -d /opt

# Add to PATH
export PATH="/opt/codeql:$PATH"

# Verify
codeql version
```

### Expected Output

```
CodeQL command-line toolchain release 2.23.5.
Copyright (C) 2019-2024 GitHub, Inc.
...
```

## CodeQL Usage (When Available)

### Create Database

```bash
codeql database create my-db \
  --language=java \
  --source-root=/path/to/source
```

### Run Queries

```bash
codeql database analyze my-db \
  --format=sarif-latest \
  --output=results.sarif \
  -- java-code-scanning.qls
```

### Query Packs

```bash
# Download standard queries
codeql pack download codeql/java-queries

# List available packs
codeql resolve packs
```

## Python Wrapper API (Planned)

When CodeQL is available, the Python wrapper will provide:

```python
from src.utils.codeql_cli import CodeQLCLI

codeql = CodeQLCLI()

# Create database
db_path = codeql.create_database(
    source_root="/path/to/source",
    language="java",
    output_dir="/tmp/codeql-db"
)

# Analyze database
results = codeql.analyze_database(
    database=db_path,
    queries="java-code-scanning.qls",
    format="sarif"
)

# Download query packs
codeql.download_queries(language="java")
```

## Development Status

- ✅ Installation script created
- ❌ Cannot install on ARM64 dev container
- ⏸️ Python wrapper deferred
- ⏸️ Tests deferred
- ✅ Documentation provided

## Tracking

- **Task**: T025a - CodeQL CLI Installation
- **Epic**: 1.1 - System Discovery Baseline
- **Status**: Blocked by ARM64 platform limitation
- **PRD**: `prds/epic-1.1-system-discovery-baseline-assessment.md`

## References

- [CodeQL CLI Documentation](https://codeql.github.com/docs/codeql-cli/)
- [CodeQL CLI Binaries](https://github.com/github/codeql-cli-binaries/releases)
- [GitHub CodeQL Action](https://github.com/github/codeql-action)
- [ARM64 Support Issue](https://github.com/github/codeql-cli-binaries/issues/136)

## Recommendation

For the Omega project migration system:

1. **Use GitHub Actions for CodeQL analysis** - Most practical approach
2. **Document requirement** - Note x86-64 requirement in architecture docs
3. **Defer local CLI** - Wait for ARM64 support or use CI/CD pipeline
4. **Continue with T026a** - Move to AppCAT CLI installation next

This ensures migration analysis capabilities without blocking on platform limitations.
