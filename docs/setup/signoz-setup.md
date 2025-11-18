# SigNoz Setup Instructions

## Overview

SigNoz observability stack is configured in the Omega project for runtime analysis with <1% performance overhead. Services are defined in `.devcontainer/docker-compose.yml` but require manual startup.

## Current Status

Run this command inside the dev container to check service status:

```bash
python3 -c "
import socket

services = [
    ('signoz-otel-collector', 4317, 'OTel Collector gRPC'),
    ('signoz-query-service', 8080, 'Query Service'),
    ('signoz-frontend', 3301, 'Frontend'),
]

for host, port, name in services:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        print(f'{"UP" if result == 0 else "DOWN":6} {name}')
    except:
        print(f'DOWN   {name}')
"
```

## Starting SigNoz Services

**IMPORTANT**: SigNoz services must be started from the HOST machine (outside the dev container), not from inside the container.

### From Host Machine

```bash
# Navigate to project directory
cd /path/to/omega

# Start SigNoz services
docker-compose -f .devcontainer/docker-compose.yml up -d signoz-otel-collector signoz-query-service signoz-frontend

# Verify services are running
docker-compose -f .devcontainer/docker-compose.yml ps | grep signoz
```

### Stopping SigNoz Services

```bash
docker-compose -f .devcontainer/docker-compose.yml stop signoz-otel-collector signoz-query-service signoz-frontend
```

## Services Configuration

### SigNoz OTel Collector
- **Ports**: 4317 (gRPC), 4318 (HTTP)
- **Config**: `.devcontainer/signoz-config.yaml`
- **Sampling Rate**: 1% (configurable for <1% overhead)
- **Exporters**: ClickHouse for traces, metrics, logs

### SigNoz Query Service
- **Port**: 8080
- **Storage**: ClickHouse
- **API**: REST API for querying telemetry data

### SigNoz Frontend
- **Port**: 3301
- **URL**: http://localhost:3301
- **Features**: Traces, metrics, logs visualization

## Using the SigNoz Deployer

The `signoz_deployer.py` module provides automation for:

1. **Health Checking**: Detects if SigNoz services are running
2. **Configuration Generation**: Creates OTel collector configs
3. **Spring Boot Instrumentation**: Generates application.yml and JVM args
4. **Validation**: Ensures <1% performance overhead

### Example Usage

```python
from src.omega_analysis.analysis.runtime.signoz_deployer import SigNozDeployer
import asyncio

async def deploy():
    deployer = SigNozDeployer()
    
    # Check deployment status
    status = await deployer.deploy_stack(target_environment='docker-compose')
    
    # Generate Spring Boot instrumentation
    configs = deployer.generate_spring_boot_instrumentation(
        'my-app',
        Path('/tmp/instrumentation')
    )
    
    return status, configs

# Run
status, configs = asyncio.run(deploy())
```

## Mock Mode

When SigNoz services are not running, the deployer automatically falls back to **mock mode**:
- Simulates healthy deployment
- Generates valid configuration files
- Provides endpoint information
- Validates <1% overhead target

This allows development and testing without requiring all services to be running.

## Troubleshooting

### Services Not Starting

1. Check Docker Compose logs:
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml logs signoz-otel-collector
   ```

2. Verify ClickHouse is running (SigNoz dependency):
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml ps clickhouse
   ```

3. Check configuration file exists:
   ```bash
   ls -la .devcontainer/signoz-config.yaml
   ```

### Port Conflicts

If ports 4317, 4318, 8080, or 3301 are already in use:

1. Modify port mappings in `.devcontainer/docker-compose.yml`
2. Update `signoz_deployer.py` endpoint configuration accordingly

### Performance Impact

Monitor SigNoz overhead:
- Default sampling: 1% (target <1% overhead)
- Adjust in `.devcontainer/signoz-config.yaml`:
  ```yaml
  processors:
    probabilistic_sampler:
      sampling_percentage: 1.0  # Adjust this value
  ```

## Integration with Analysis Engine

SigNoz integrates with:
- **Static Analysis**: Compare intended vs actual architecture
- **Load Testing**: Capture performance baselines under load
- **Gap Analysis**: Identify architectural drift

See `tools/src/omega_analysis/services/orchestration/runtime_analyzer.py` for orchestration logic.
