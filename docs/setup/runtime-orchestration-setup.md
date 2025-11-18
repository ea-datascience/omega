# Runtime Analysis Orchestration

Complete orchestration service for coordinating runtime analysis components.

## Overview

The `RuntimeAnalysisOrchestrator` coordinates SigNoz deployment, OpenTelemetry instrumentation generation, and synthetic load testing to establish performance baselines and runtime behavior analysis per FR-002 and FR-004.

## Architecture

```
RuntimeAnalysisOrchestrator
├── Phase 1: SigNoz Deployment
│   ├── Check for live deployment
│   ├── Deploy stack or use mock
│   └── Validate <1% overhead (FR-002)
├── Phase 2: OTel Instrumentation
│   ├── Generate agent configuration
│   ├── Create JVM arguments
│   ├── Generate Spring Boot config
│   └── Provide annotation examples
├── Phase 3: Synthetic Load Testing
│   ├── Generate load scenarios
│   ├── Execute constant load
│   ├── Execute stepped load
│   └── Collect performance data
├── Phase 4: Baseline Collection
│   ├── Aggregate metrics
│   ├── Calculate percentiles (P50/P95/P99)
│   ├── Compute confidence intervals
│   └── Assess data quality
├── Phase 5: Summary Generation
│   ├── Deployment status
│   ├── Load test metrics
│   ├── Baseline statistics
│   └── Quality scores
└── Phase 6: Validation
    ├── Verify <1% overhead (FR-002)
    ├── Verify 95% confidence (FR-004)
    ├── Check sample sizes
    └── Validate data quality
```

## Components Coordinated

### 1. SigNoz Deployer
- **Purpose**: Deploy observability stack
- **Modes**: Live deployment or mock fallback
- **Validation**: Performance overhead <1%

### 2. OTel Instrumentation Generator
- **Purpose**: Generate instrumentation templates
- **Artifacts**: 9 file types (agent config, JVM args, Spring config, etc.)
- **Modes**: Agent-based, manual, hybrid

### 3. Synthetic Load Generator
- **Purpose**: Execute load tests for baselines
- **Patterns**: Constant, stepped, spike, wave
- **Metrics**: Response times, throughput, error rates

## Data Models

### RuntimeAnalysisTask
Task tracking for orchestration phases:
- `task_id`: Unique identifier
- `task_type`: deploy, instrument, load_test, collect_baseline
- `status`: pending, running, completed, failed
- `start_time/end_time`: Execution timestamps
- `error_message`: Failure diagnostics

### PerformanceBaseline
Performance baseline with statistical confidence:
- **Response Time Metrics**: min, mean, median, p95, p99, max (milliseconds)
- **Throughput**: requests per second
- **Errors**: error rate, errors by type
- **Statistics**: 95% confidence intervals, sample size
- **Quality**: data quality score (0.0-1.0)

### RuntimeAnalysisResults
Comprehensive analysis results:
- **Deployment**: SigNoz deployment status
- **Instrumentation**: Generated artifacts
- **Load Tests**: Results from all scenarios
- **Baseline**: Aggregated performance baseline
- **Metadata**: Execution context, timestamps
- **Validation**: Requirements compliance, error list

## Usage

### Programmatic API

```python
from pathlib import Path
from omega_analysis.services.orchestration.runtime_analyzer import (
    RuntimeAnalysisOrchestrator
)

# Initialize orchestrator
orchestrator = RuntimeAnalysisOrchestrator(
    base_output_dir=Path("/tmp/runtime-analysis")
)

# Run full analysis
results = await orchestrator.orchestrate_full_runtime_analysis(
    application_name="spring-modulith",
    base_url="http://localhost:8080",
    config={
        "signoz": {
            "environment": "docker-compose"
        },
        "load_testing": {
            "sequential": True,
            "scenarios": [
                {
                    "name": "baseline-constant",
                    "pattern": "constant",
                    "duration": 5,
                    "users": 10
                }
            ]
        },
        "baseline": {
            "primary_scenario": "baseline-constant",
            "environment_type": "synthetic"
        }
    }
)

# Check results
print(f"Analysis ID: {results.analysis_id}")
print(f"Meets Requirements: {results.meets_requirements}")
print(f"P95 Response Time: {results.baseline.response_time_p95}ms")
```

### Command-Line Interface

```bash
# Basic usage
python -m src.omega_analysis.services.orchestration.runtime_analyzer \
  --app-name spring-modulith \
  --base-url http://localhost:8080 \
  --output-dir /tmp/runtime-analysis

# Custom duration
python -m src.omega_analysis.services.orchestration.runtime_analyzer \
  --app-name my-app \
  --base-url http://localhost:8080 \
  --duration 10 \
  --output-dir ./analysis-results
```

**CLI Options**:
- `--app-name`: Application name (default: spring-modulith)
- `--base-url`: Base URL of running application (default: http://localhost:8080)
- `--output-dir`: Output directory (default: /tmp/runtime-analysis)
- `--duration`: Load test duration in minutes (default: 5)

## Configuration

### Default Configuration

```python
{
    "signoz": {
        "environment": "docker-compose"
    },
    "instrumentation": {
        "mode": "hybrid",
        "namespace": "omega-migration",
        "otel_endpoint": "http://signoz-otel-collector:4318",
        "sampling_rate": 0.01
    },
    "load_testing": {
        "sequential": True,
        "scenarios": [
            {
                "name": "baseline-constant",
                "pattern": "constant",
                "duration": 5,
                "users": 10
            },
            {
                "name": "baseline-stepped",
                "pattern": "stepped",
                "duration": 10,
                "base_users": 10,
                "peak_users": 50,
                "step_duration": 2,
                "step_increment": 10
            }
        ]
    },
    "baseline": {
        "primary_scenario": "baseline-stepped",
        "environment_type": "synthetic",
        "concurrent_users": 50
    }
}
```

### Custom Scenarios

```python
config = {
    "load_testing": {
        "scenarios": [
            {
                "name": "peak-load",
                "pattern": "constant",
                "duration": 10,
                "users": 100,
                "endpoints": [
                    {
                        "path": "/api/v1/users",
                        "method": "GET",
                        "weight": 5,
                        "expected_status": 200
                    },
                    {
                        "path": "/api/v1/orders",
                        "method": "GET",
                        "weight": 3,
                        "expected_status": 200
                    }
                ],
                "think_time_ms": [500, 2000],
                "timeout": 30
            }
        ]
    }
}
```

## Output Structure

```
/tmp/runtime-analysis/
└── runtime_spring-modulith_20251118_220000/
    ├── runtime_analysis_results.json      # Complete results
    ├── instrumentation/                    # OTel artifacts
    │   ├── otel-agent-config.conf
    │   ├── otel-jvm-args.txt
    │   ├── otel-spring-boot-config.yml
    │   ├── otel-maven-dependencies.xml
    │   ├── docker-compose-otel.yml
    │   ├── otel-verification.sh
    │   ├── MANIFEST.json
    │   ├── README-agent-mode.md
    │   ├── README-manual-mode.md
    │   └── README-hybrid-mode.md
    └── load-tests/                         # (if exported)
        ├── baseline-constant.json
        └── baseline-stepped.json
```

## Results File Format

```json
{
  "analysis_id": "runtime_spring-modulith_20251118_220000",
  "application_name": "spring-modulith",
  "output_directory": "/tmp/runtime-analysis/...",
  "execution_metadata": {
    "start_time": "2025-11-18T22:00:00Z",
    "config": {...},
    "orchestrator_version": "1.0.0"
  },
  "signoz_deployment": {
    "deployment_id": "signoz_20251118_220000",
    "status": "healthy",
    "performance_overhead": 0.8,
    "health_checks": {...},
    "endpoints": {...}
  },
  "instrumentation": {
    "config_id": "otel_spring-modulith_20251118_220000",
    "mode": "hybrid",
    "files": {...}
  },
  "load_tests": {
    "baseline-constant": {
      "scenario_name": "baseline-constant",
      "total_requests": 1000,
      "success_rate": 0.95,
      "response_time_p95": 120.5,
      "throughput": 16.67
    }
  },
  "baseline": {
    "baseline_id": "baseline_spring-modulith_20251118_220000",
    "application_name": "spring-modulith",
    "environment_type": "synthetic",
    "response_time_mean": 50.0,
    "response_time_p95": 120.5,
    "response_time_p99": 200.0,
    "requests_per_second": 16.67,
    "statistical_confidence": 0.95,
    "data_quality_score": 0.85
  },
  "summary_metrics": {
    "signoz_status": "healthy",
    "performance_overhead": 0.8,
    "instrumentation_mode": "hybrid",
    "load_test_scenarios": 2,
    "baseline_collected": true,
    "baseline_p95_ms": 120.5,
    "data_quality_score": 0.85
  },
  "meets_requirements": true,
  "validation_errors": []
}
```

## Validation Rules

The orchestrator validates results against functional requirements:

### FR-002: Performance Overhead
- **Rule**: SigNoz deployment overhead must be <1%
- **Validation**: `deployment.performance_overhead < 1.0`
- **Failure Message**: "Performance overhead X% exceeds 1% limit (FR-002)"

### FR-004: Statistical Confidence
- **Rule**: Performance baselines must have 95% confidence intervals
- **Validation**: `baseline.statistical_confidence >= 0.95`
- **Failure Message**: "Statistical confidence X below 95% requirement (FR-004)"

### Data Quality
- **Rule**: Sample size must be sufficient (>100 requests)
- **Validation**: `baseline.sample_size >= 100`
- **Failure Message**: "Sample size X too small for reliable statistics (FR-004)"

- **Rule**: Data quality score must be acceptable (>0.7)
- **Validation**: `baseline.data_quality_score >= 0.7`
- **Failure Message**: "Data quality score X below 0.7 threshold"

## Quality Metrics

### Data Quality Score Calculation

```python
def calculate_quality_score(results):
    sample_score = min(sample_size / 1000, 1.0)  # 1000+ = perfect
    error_score = 1.0 - error_rate
    confidence_score = statistical_confidence
    
    return (
        sample_score * 0.3 +
        error_score * 0.4 +
        confidence_score * 0.3
    )
```

**Quality Levels**:
- **High (≥0.9)**: Large sample, low errors, high confidence
- **Good (0.7-0.9)**: Adequate sample, moderate errors, good confidence
- **Fair (0.5-0.7)**: Small sample or higher errors or lower confidence
- **Poor (<0.5)**: Insufficient data quality for reliable analysis

## Error Handling

The orchestrator uses robust error handling:

1. **Task-Level Failures**: Individual tasks track errors without stopping workflow
2. **Validation Failures**: Collected in `validation_errors` list
3. **Component Fallbacks**: SigNoz uses mock mode if live deployment unavailable
4. **Graceful Degradation**: Analysis completes even with component failures

## Integration Points

### With Static Analysis Orchestrator
```python
from omega_analysis.services.orchestration.static_analyzer import StaticAnalysisOrchestrator
from omega_analysis.services.orchestration.runtime_analyzer import RuntimeAnalysisOrchestrator

# Run static analysis first
static_orchestrator = StaticAnalysisOrchestrator(...)
static_results = await static_orchestrator.orchestrate_full_analysis(...)

# Use static analysis to inform runtime scenarios
endpoints = extract_endpoints_from_java_analysis(static_results.java_analysis)

# Run runtime analysis with discovered endpoints
runtime_orchestrator = RuntimeAnalysisOrchestrator(...)
runtime_results = await runtime_orchestrator.orchestrate_full_runtime_analysis(
    application_name="spring-modulith",
    base_url="http://localhost:8080",
    config={
        "load_testing": {
            "scenarios": [{
                "endpoints": endpoints
            }]
        }
    }
)
```

### With Infrastructure Services
All infrastructure services must be accessible:
- **PostgreSQL**: Results persistence (optional)
- **ClickHouse**: Time-series metrics (optional)
- **Redis**: Caching (optional)
- **SigNoz**: Observability stack (falls back to mock)

Use `service_utils.py` to verify connections before runtime analysis.

## Testing

### Unit Tests
```bash
# Test orchestrator components
pytest tests/integration/test_runtime_orchestrator.py::test_orchestrator_initialization -v
pytest tests/integration/test_runtime_orchestrator.py::test_task_creation -v
```

### Integration Tests
```bash
# Test full workflow
pytest tests/integration/test_runtime_orchestrator.py::test_full_orchestration_workflow -v
```

### Live Testing
```bash
# Against httpbin.org
python -m src.omega_analysis.services.orchestration.runtime_analyzer \
  --app-name httpbin-test \
  --base-url https://httpbin.org \
  --duration 5 \
  --output-dir /tmp/test-runtime
```

## Performance Characteristics

**Execution Time**:
- SigNoz deployment: 5-30 seconds (or instant for mock)
- Instrumentation generation: 1-2 seconds
- Load testing: Duration dependent (5-10 minutes typical)
- Baseline collection: 1-2 seconds
- Total: 5-12 minutes for standard analysis

**Resource Usage**:
- Memory: ~200MB for orchestrator
- CPU: Low (mostly I/O bound during load tests)
- Disk: ~50MB per analysis (artifacts + results)

## Best Practices

1. **Use appropriate load durations**: 5-10 minutes for reliable baselines
2. **Configure realistic endpoints**: Mirror production traffic patterns
3. **Validate infrastructure first**: Use `service_utils.py` to check services
4. **Review validation errors**: Address all failed requirements
5. **Preserve results**: Export to persistent storage for historical analysis
6. **Monitor quality scores**: Aim for >0.8 data quality
7. **Run multiple scenarios**: Use constant, stepped, and spike patterns

## Troubleshooting

### Issue: Low Data Quality Score
**Symptoms**: `data_quality_score < 0.7`
**Solutions**:
- Increase load test duration
- Reduce error rate (check endpoint availability)
- Increase concurrent users for larger sample

### Issue: Validation Failures
**Symptoms**: `meets_requirements = false`
**Solutions**:
- Review `validation_errors` list
- Check SigNoz deployment overhead
- Verify statistical confidence intervals
- Ensure adequate sample sizes

### Issue: Load Test Failures
**Symptoms**: High error rates, timeouts
**Solutions**:
- Verify application is running and accessible
- Check endpoint paths and methods
- Increase timeout values
- Reduce concurrent users

## References

- **SigNoz Deployer**: `/workspace/tools/src/omega_analysis/analysis/runtime/signoz_deployer.py`
- **OTel Instrumentation**: `/workspace/tools/src/omega_analysis/analysis/runtime/otel_instrumentation.py`
- **Load Generator**: `/workspace/tools/src/omega_analysis/analysis/runtime/load_generator.py`
- **Static Orchestrator**: `/workspace/tools/src/omega_analysis/services/orchestration/static_analyzer.py`
- **Service Utilities**: `/workspace/tools/src/utils/service_utils.py`
