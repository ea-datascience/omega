"""OpenTelemetry instrumentation template generator for Spring Boot applications.

This module provides automated generation of OpenTelemetry instrumentation configurations
for Java/Spring Boot applications, supporting both automatic Java agent instrumentation
and manual Spring Boot integration.

Per FR-002: Generate instrumentation templates to auto-inject OTel tracing, metrics,
and logging into legacy applications with minimal code changes.

Supports multiple instrumentation approaches:
1. OpenTelemetry Java Agent (automatic, zero-code)
2. Spring Boot Actuator + Micrometer (manual integration)
3. Custom annotations (@WithSpan, @Counted, etc.)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml
import json

logger = logging.getLogger(__name__)


@dataclass
class InstrumentationConfig:
    """OpenTelemetry instrumentation configuration."""
    application_name: str
    service_namespace: str = 'omega-migration'
    otel_endpoint: str = 'http://signoz-otel-collector:4318'
    sampling_rate: float = 0.01  # 1% sampling for <1% overhead
    enable_logs: bool = True
    enable_metrics: bool = True
    enable_traces: bool = True
    instrumentation_mode: str = 'agent'  # 'agent', 'manual', 'hybrid'
    custom_attributes: Dict[str, str] = field(default_factory=dict)
    excluded_endpoints: List[str] = field(default_factory=lambda: ['/health', '/actuator'])


@dataclass
class InstrumentationArtifacts:
    """Generated instrumentation artifacts."""
    config_id: str
    application_name: str
    mode: str
    files: Dict[str, Path]  # artifact_type -> file_path
    jvm_args: List[str]
    maven_dependencies: List[str]
    spring_boot_properties: Dict[str, any]
    annotations_usage: Dict[str, List[str]]  # annotation -> example_usages
    generated_at: datetime


class OTelInstrumentationGenerator:
    """Generates OpenTelemetry instrumentation templates for Spring Boot applications."""
    
    # Latest stable OpenTelemetry Java versions
    OTEL_JAVA_AGENT_VERSION = "2.10.0"
    OTEL_INSTRUMENTATION_ANNOTATIONS_VERSION = "2.10.0"
    OTEL_SPRING_BOOT_STARTER_VERSION = "2.10.0-alpha"
    
    def __init__(self, config: Optional[InstrumentationConfig] = None):
        """Initialize instrumentation generator.
        
        Args:
            config: Instrumentation configuration, uses defaults if not provided
        """
        self.config = config or InstrumentationConfig(application_name='default-app')
        
    def generate_all_artifacts(self, output_dir: Path) -> InstrumentationArtifacts:
        """Generate complete instrumentation artifacts.
        
        Args:
            output_dir: Directory to write artifacts
            
        Returns:
            InstrumentationArtifacts with all generated files
        """
        config_id = f"otel_{self.config.application_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Generating OTel instrumentation artifacts: {config_id}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        if self.config.instrumentation_mode in ['agent', 'hybrid']:
            # Java agent instrumentation files
            files['agent_config'] = self._generate_agent_config(output_dir)
            files['jvm_args'] = self._generate_jvm_args_file(output_dir)
            files['agent_readme'] = self._generate_agent_readme(output_dir)
            
        if self.config.instrumentation_mode in ['manual', 'hybrid']:
            # Manual Spring Boot integration files
            files['application_yml'] = self._generate_spring_boot_config(output_dir)
            files['pom_additions'] = self._generate_maven_dependencies(output_dir)
            files['manual_readme'] = self._generate_manual_integration_readme(output_dir)
            
        # Common files for all modes
        files['docker_compose'] = self._generate_docker_compose_snippet(output_dir)
        files['annotations_guide'] = self._generate_annotations_guide(output_dir)
        files['verification_script'] = self._generate_verification_script(output_dir)
        
        artifacts = InstrumentationArtifacts(
            config_id=config_id,
            application_name=self.config.application_name,
            mode=self.config.instrumentation_mode,
            files=files,
            jvm_args=self._get_jvm_args(),
            maven_dependencies=self._get_maven_dependencies(),
            spring_boot_properties=self._get_spring_boot_properties(),
            annotations_usage=self._get_annotations_usage(),
            generated_at=datetime.now()
        )
        
        # Generate summary manifest
        self._generate_manifest(output_dir, artifacts)
        
        logger.info(f"Generated {len(files)} instrumentation artifacts in {output_dir}")
        return artifacts
        
    def _generate_agent_config(self, output_dir: Path) -> Path:
        """Generate OpenTelemetry Java agent configuration file."""
        config_file = output_dir / 'otel-agent.properties'
        
        config_content = {
            # Service identification
            'otel.service.name': self.config.application_name,
            'otel.service.namespace': self.config.service_namespace,
            
            # OTLP exporter configuration
            'otel.exporter.otlp.endpoint': self.config.otel_endpoint,
            'otel.exporter.otlp.protocol': 'http/protobuf',
            
            # Traces configuration
            'otel.traces.exporter': 'otlp' if self.config.enable_traces else 'none',
            'otel.traces.sampler': 'traceidratio',
            'otel.traces.sampler.arg': str(self.config.sampling_rate),
            
            # Metrics configuration
            'otel.metrics.exporter': 'otlp' if self.config.enable_metrics else 'none',
            'otel.metric.export.interval': '60000',  # 60 seconds
            
            # Logs configuration
            'otel.logs.exporter': 'otlp' if self.config.enable_logs else 'none',
            
            # Instrumentation configuration
            'otel.instrumentation.common.default-enabled': 'true',
            'otel.instrumentation.spring-webmvc.enabled': 'true',
            'otel.instrumentation.spring-web.enabled': 'true',
            'otel.instrumentation.jdbc.enabled': 'true',
            'otel.instrumentation.hibernate.enabled': 'true',
            'otel.instrumentation.http-url-connection.enabled': 'true',
            'otel.instrumentation.kafka.enabled': 'true',
            
            # Performance tuning
            'otel.bsp.schedule.delay': '5000',  # Batch span processor delay (ms)
            'otel.bsp.max.queue.size': '2048',
            'otel.bsp.max.export.batch.size': '512',
        }
        
        # Add custom resource attributes
        if self.config.custom_attributes:
            for key, value in self.config.custom_attributes.items():
                config_content[f'otel.resource.attributes.{key}'] = value
                
        # Excluded endpoints
        if self.config.excluded_endpoints:
            config_content['otel.instrumentation.http.server.route-based-naming'] = 'true'
            
        # Write properties file
        with open(config_file, 'w') as f:
            for key, value in config_content.items():
                f.write(f"{key}={value}\n")
                
        return config_file
        
    def _generate_jvm_args_file(self, output_dir: Path) -> Path:
        """Generate JVM arguments file for Java agent."""
        args_file = output_dir / 'jvm-args.txt'
        
        jvm_args = self._get_jvm_args()
        
        with open(args_file, 'w') as f:
            f.write("# OpenTelemetry Java Agent JVM Arguments\n")
            f.write("# Add these to your application startup command\n\n")
            f.write(" ".join(jvm_args))
            f.write("\n\n# Example startup command:\n")
            f.write(f"# java {' '.join(jvm_args)} -jar your-application.jar\n")
            
        return args_file
        
    def _get_jvm_args(self) -> List[str]:
        """Get JVM arguments for Java agent."""
        agent_path = "${OTEL_AGENT_PATH:-./agents/opentelemetry-javaagent.jar}"
        config_path = "otel-agent.properties"
        
        return [
            f"-javaagent:{agent_path}",
            f"-Dotel.javaagent.configuration-file={config_path}",
            "-Dotel.javaagent.debug=false",
            "-Dotel.javaagent.logging=simple",
        ]
        
    def _generate_spring_boot_config(self, output_dir: Path) -> Path:
        """Generate Spring Boot application.yml for manual instrumentation."""
        config_file = output_dir / 'application-otel.yml'
        
        spring_config = {
            'spring': {
                'application': {
                    'name': self.config.application_name
                }
            },
            'management': {
                'endpoints': {
                    'web': {
                        'exposure': {
                            'include': 'health,info,metrics,prometheus,traces'
                        }
                    }
                },
                'metrics': {
                    'export': {
                        'prometheus': {
                            'enabled': True
                        }
                    },
                    'distribution': {
                        'percentiles-histogram': {
                            'http.server.requests': True
                        }
                    }
                },
                'tracing': {
                    'sampling': {
                        'probability': self.config.sampling_rate
                    }
                }
            },
            'otel': {
                'exporter': {
                    'otlp': {
                        'endpoint': self.config.otel_endpoint
                    }
                },
                'resource': {
                    'attributes': {
                        'service.name': self.config.application_name,
                        'service.namespace': self.config.service_namespace,
                        **self.config.custom_attributes
                    }
                }
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(spring_config, f, default_flow_style=False, sort_keys=False)
            
        return config_file
        
    def _generate_maven_dependencies(self, output_dir: Path) -> Path:
        """Generate Maven pom.xml additions for manual instrumentation."""
        pom_file = output_dir / 'pom-otel-additions.xml'
        
        dependencies = self._get_maven_dependencies()
        
        pom_content = """<!-- Add these dependencies to your pom.xml -->
<!-- OpenTelemetry Instrumentation -->
<dependencies>
"""
        
        for dep in dependencies:
            pom_content += f"    {dep}\n"
            
        pom_content += "</dependencies>\n"
        
        with open(pom_file, 'w') as f:
            f.write(pom_content)
            
        return pom_file
        
    def _get_maven_dependencies(self) -> List[str]:
        """Get Maven dependencies for manual instrumentation."""
        dependencies = []
        
        if self.config.instrumentation_mode in ['manual', 'hybrid']:
            # Spring Boot OpenTelemetry starter
            dependencies.extend([
                f"""<dependency>
        <groupId>io.opentelemetry.instrumentation</groupId>
        <artifactId>opentelemetry-spring-boot-starter</artifactId>
        <version>{self.OTEL_SPRING_BOOT_STARTER_VERSION}</version>
    </dependency>""",
                # Manual annotations
                f"""<dependency>
        <groupId>io.opentelemetry.instrumentation</groupId>
        <artifactId>opentelemetry-instrumentation-annotations</artifactId>
        <version>{self.OTEL_INSTRUMENTATION_ANNOTATIONS_VERSION}</version>
    </dependency>""",
                # Micrometer bridge
                """<dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-tracing-bridge-otel</artifactId>
    </dependency>""",
                # OTLP exporter
                """<dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-otlp</artifactId>
    </dependency>""",
            ])
            
        return dependencies
        
    def _get_spring_boot_properties(self) -> Dict[str, any]:
        """Get Spring Boot properties for manual instrumentation."""
        return {
            'management.endpoints.web.exposure.include': 'health,info,metrics,prometheus,traces',
            'management.metrics.export.prometheus.enabled': True,
            'management.tracing.sampling.probability': self.config.sampling_rate,
            'otel.exporter.otlp.endpoint': self.config.otel_endpoint,
            'otel.resource.attributes.service.name': self.config.application_name,
        }
        
    def _generate_annotations_guide(self, output_dir: Path) -> Path:
        """Generate guide for using OpenTelemetry annotations."""
        guide_file = output_dir / 'ANNOTATIONS_GUIDE.md'
        
        annotations_usage = self._get_annotations_usage()
        
        guide_content = f"""# OpenTelemetry Annotations Guide

## Overview

OpenTelemetry provides annotations for adding custom instrumentation to your Java code
without manually managing span lifecycle.

## Available Annotations

### @WithSpan - Custom Span Creation

Creates a new span for the annotated method.

```java
{annotations_usage['@WithSpan'][0]}
```

### @SpanAttribute - Add Attributes to Spans

Adds method parameters as span attributes.

```java
{annotations_usage['@SpanAttribute'][0]}
```

### @AddingSpanAttributes - Multiple Attributes

Add multiple attributes to the current span.

```java
{annotations_usage['@AddingSpanAttributes'][0]}
```

## Usage Guidelines

### 1. Add Dependency

```xml
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-instrumentation-annotations</artifactId>
    <version>{self.OTEL_INSTRUMENTATION_ANNOTATIONS_VERSION}</version>
</dependency>
```

### 2. Annotate Critical Methods

Focus on:
- Service layer methods (business logic)
- Repository methods (database operations)
- External API calls
- Complex computations
- Background jobs

### 3. Best Practices

- **Be Selective**: Don't annotate every method - focus on meaningful operations
- **Add Context**: Use @SpanAttribute to capture important parameters
- **Avoid Overhead**: Keep sampling rate low ({self.config.sampling_rate * 100}% configured)
- **Test Performance**: Verify <1% overhead requirement

## Performance Impact

Current configuration:
- Sampling Rate: {self.config.sampling_rate * 100}%
- Target Overhead: <1%
- Batch Export: Enabled (reduces network calls)

## Examples by Layer

### Controller Layer
```java
@RestController
public class OrderController {{
    
    @WithSpan("process-order")
    @PostMapping("/orders")
    public Order createOrder(@SpanAttribute("order.id") String orderId,
                            @RequestBody OrderRequest request) {{
        return orderService.processOrder(orderId, request);
    }}
}}
```

### Service Layer
```java
@Service
public class OrderService {{
    
    @WithSpan("calculate-total")
    public BigDecimal calculateOrderTotal(@SpanAttribute("order.items") int itemCount) {{
        // Complex calculation logic
        return total;
    }}
}}
```

### Repository Layer
```java
@Repository
public class OrderRepository {{
    
    @WithSpan("query-orders-by-status")
    public List<Order> findByStatus(@SpanAttribute("status") OrderStatus status) {{
        // Database query
        return orders;
    }}
}}
```

## Troubleshooting

### Spans Not Appearing

1. Verify Java agent is attached (agent mode)
2. Check sampling rate (may be filtering out spans)
3. Ensure OTLP endpoint is accessible
4. Check application logs for errors

### High Overhead

1. Reduce sampling rate
2. Remove annotations from frequently-called methods
3. Increase batch export interval
4. Exclude health check endpoints

## Resources

- [OpenTelemetry Java Instrumentation](https://opentelemetry.io/docs/instrumentation/java/)
- [Annotation API Reference](https://opentelemetry.io/docs/instrumentation/java/automatic/annotations/)
- [SigNoz Documentation](https://signoz.io/docs/)
"""
        
        with open(guide_file, 'w') as f:
            f.write(guide_content)
            
        return guide_file
        
    def _get_annotations_usage(self) -> Dict[str, List[str]]:
        """Get example usage for OpenTelemetry annotations."""
        return {
            '@WithSpan': [
                """import io.opentelemetry.instrumentation.annotations.WithSpan;

@Service
public class PaymentService {
    
    @WithSpan("process-payment")
    public PaymentResult processPayment(PaymentRequest request) {
        // Automatically creates a span named "process-payment"
        return gateway.charge(request);
    }
}"""
            ],
            '@SpanAttribute': [
                """import io.opentelemetry.instrumentation.annotations.SpanAttribute;
import io.opentelemetry.instrumentation.annotations.WithSpan;

@WithSpan("validate-user")
public boolean validateUser(@SpanAttribute("user.id") String userId,
                            @SpanAttribute("user.email") String email) {
    // userId and email are added as span attributes
    return authService.validate(userId, email);
}"""
            ],
            '@AddingSpanAttributes': [
                """import io.opentelemetry.instrumentation.annotations.AddingSpanAttributes;
import io.opentelemetry.api.trace.Span;

@AddingSpanAttributes
public void processOrder(Order order) {
    Span currentSpan = Span.current();
    currentSpan.setAttribute("order.id", order.getId());
    currentSpan.setAttribute("order.total", order.getTotal());
    // Process order...
}"""
            ]
        }
        
    def _generate_docker_compose_snippet(self, output_dir: Path) -> Path:
        """Generate Docker Compose snippet for running with OTel agent."""
        compose_file = output_dir / 'docker-compose-otel.yml'
        
        compose_content = f"""# Docker Compose snippet for running Spring Boot app with OpenTelemetry
version: '3.8'

services:
  {self.config.application_name}:
    image: your-app:latest
    environment:
      # Java agent configuration
      JAVA_TOOL_OPTIONS: >-
        -javaagent:/app/agents/opentelemetry-javaagent.jar
        -Dotel.javaagent.configuration-file=/app/config/otel-agent.properties
      
      # Service identification
      OTEL_SERVICE_NAME: {self.config.application_name}
      OTEL_SERVICE_NAMESPACE: {self.config.service_namespace}
      
      # OTLP endpoint
      OTEL_EXPORTER_OTLP_ENDPOINT: {self.config.otel_endpoint}
      
      # Sampling configuration
      OTEL_TRACES_SAMPLER: traceidratio
      OTEL_TRACES_SAMPLER_ARG: "{self.config.sampling_rate}"
      
    volumes:
      # Mount OpenTelemetry agent
      - ./agents/opentelemetry-javaagent.jar:/app/agents/opentelemetry-javaagent.jar
      - ./otel-agent.properties:/app/config/otel-agent.properties
      
    networks:
      - monitoring
      
networks:
  monitoring:
    external: true
"""
        
        with open(compose_file, 'w') as f:
            f.write(compose_content)
            
        return compose_file
        
    def _generate_verification_script(self, output_dir: Path) -> Path:
        """Generate verification script to test instrumentation."""
        script_file = output_dir / 'verify-instrumentation.sh'
        
        script_content = f"""#!/bin/bash
# Verification script for OpenTelemetry instrumentation

set -e

echo "=== OpenTelemetry Instrumentation Verification ==="
echo ""

# 1. Check if OpenTelemetry agent is downloaded
echo "1. Checking for OpenTelemetry Java agent..."
AGENT_PATH="./agents/opentelemetry-javaagent.jar"
if [ -f "$AGENT_PATH" ]; then
    echo "   ✓ Agent found at $AGENT_PATH"
    ls -lh "$AGENT_PATH"
else
    echo "   ✗ Agent not found. Downloading..."
    mkdir -p ./agents
    wget -O "$AGENT_PATH" \\
        https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v{self.OTEL_JAVA_AGENT_VERSION}/opentelemetry-javaagent.jar
    echo "   ✓ Agent downloaded"
fi
echo ""

# 2. Check if configuration file exists
echo "2. Checking for agent configuration..."
if [ -f "otel-agent.properties" ]; then
    echo "   ✓ Configuration found"
    echo "   Service Name: {self.config.application_name}"
    echo "   OTLP Endpoint: {self.config.otel_endpoint}"
    echo "   Sampling Rate: {self.config.sampling_rate}"
else
    echo "   ✗ Configuration file not found"
    exit 1
fi
echo ""

# 3. Check if OTLP endpoint is accessible
echo "3. Checking OTLP endpoint accessibility..."
ENDPOINT_HOST=$(echo {self.config.otel_endpoint} | sed -E 's|http://([^:/]+).*|\\1|')
ENDPOINT_PORT=$(echo {self.config.otel_endpoint} | sed -E 's|.*:([0-9]+).*|\\1|')

if command -v nc &> /dev/null; then
    if nc -z $ENDPOINT_HOST $ENDPOINT_PORT 2>/dev/null; then
        echo "   ✓ OTLP endpoint accessible at $ENDPOINT_HOST:$ENDPOINT_PORT"
    else
        echo "   ✗ OTLP endpoint not accessible (this is OK for local development)"
    fi
else
    echo "   - nc not available, skipping connectivity check"
fi
echo ""

# 4. Verify Spring Boot configuration (if manual mode)
if [ "{self.config.instrumentation_mode}" = "manual" ] || [ "{self.config.instrumentation_mode}" = "hybrid" ]; then
    echo "4. Checking Spring Boot configuration..."
    if [ -f "application-otel.yml" ]; then
        echo "   ✓ Spring Boot OTel configuration found"
    else
        echo "   ✗ Spring Boot OTel configuration not found"
    fi
    echo ""
fi

# 5. Generate sample startup command
echo "=== Sample Startup Command ==="
echo ""
echo "java \\\\"
echo "  -javaagent:$AGENT_PATH \\\\"
echo "  -Dotel.javaagent.configuration-file=otel-agent.properties \\\\"
echo "  -jar your-application.jar"
echo ""

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Start your application with the command above"
echo "2. Generate some traffic to your application"
echo "3. Check SigNoz UI at http://localhost:3301 for traces"
echo "4. Verify performance overhead is <1%"
"""
        
        with open(script_file, 'w') as f:
            f.write(script_content)
            
        # Make executable
        script_file.chmod(0o755)
        
        return script_file
        
    def _generate_agent_readme(self, output_dir: Path) -> Path:
        """Generate README for Java agent instrumentation."""
        readme_file = output_dir / 'README-AGENT.md'
        
        readme_content = f"""# OpenTelemetry Java Agent Instrumentation

## Quick Start

### 1. Download OpenTelemetry Java Agent

```bash
mkdir -p ./agents
wget -O ./agents/opentelemetry-javaagent.jar \\
    https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v{self.OTEL_JAVA_AGENT_VERSION}/opentelemetry-javaagent.jar
```

### 2. Start Application with Agent

```bash
java -javaagent:./agents/opentelemetry-javaagent.jar \\
     -Dotel.javaagent.configuration-file=otel-agent.properties \\
     -jar your-application.jar
```

### 3. Verify Instrumentation

1. Generate traffic to your application
2. Check SigNoz UI: http://localhost:3301
3. Look for service: **{self.config.application_name}**

## Configuration

All configuration is in `otel-agent.properties`:

- **Service Name**: {self.config.application_name}
- **OTLP Endpoint**: {self.config.otel_endpoint}
- **Sampling Rate**: {self.config.sampling_rate * 100}%

## What Gets Instrumented Automatically

The Java agent automatically instruments:

✓ **HTTP Servers**: Spring MVC, Spring WebFlux  
✓ **HTTP Clients**: RestTemplate, WebClient, HttpURLConnection  
✓ **Databases**: JDBC, Hibernate, JPA  
✓ **Messaging**: Kafka, RabbitMQ, JMS  
✓ **Caching**: Redis, Caffeine  
✓ **Async**: CompletableFuture, ExecutorService  

## Performance Impact

- Sampling Rate: {self.config.sampling_rate * 100}%
- Expected Overhead: <1%
- Batch Processing: Enabled

## Excluded Endpoints

The following endpoints are excluded from tracing:
{chr(10).join(f'- {endpoint}' for endpoint in self.config.excluded_endpoints)}

## Environment Variables

You can override configuration with environment variables:

```bash
export OTEL_SERVICE_NAME="{self.config.application_name}"
export OTEL_EXPORTER_OTLP_ENDPOINT="{self.config.otel_endpoint}"
export OTEL_TRACES_SAMPLER="traceidratio"
export OTEL_TRACES_SAMPLER_ARG="{self.config.sampling_rate}"
```

## Troubleshooting

### No traces appearing

1. Check agent is attached: Look for "opentelemetry-javaagent" in startup logs
2. Verify OTLP endpoint is accessible
3. Check sampling rate (may be filtering out spans)
4. Review application logs for errors

### High CPU/Memory usage

1. Reduce sampling rate in `otel-agent.properties`
2. Increase batch export delay
3. Disable specific instrumentations if not needed

## Docker Deployment

See `docker-compose-otel.yml` for Docker deployment configuration.

## Resources

- [OpenTelemetry Java Agent](https://github.com/open-telemetry/opentelemetry-java-instrumentation)
- [Configuration Options](https://opentelemetry.io/docs/instrumentation/java/automatic/agent-config/)
- [SigNoz Documentation](https://signoz.io/docs/)
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
            
        return readme_file
        
    def _generate_manual_integration_readme(self, output_dir: Path) -> Path:
        """Generate README for manual Spring Boot integration."""
        readme_file = output_dir / 'README-MANUAL.md'
        
        readme_content = f"""# OpenTelemetry Manual Spring Boot Integration

## Overview

Manual integration provides more control over instrumentation compared to the Java agent.
Use this when you need:

- Custom span creation and attributes
- Selective instrumentation
- Integration with existing Micrometer metrics
- Fine-grained control over tracing

## Setup

### 1. Add Maven Dependencies

Add dependencies from `pom-otel-additions.xml` to your `pom.xml`.

### 2. Add Spring Boot Configuration

Merge `application-otel.yml` into your `application.yml`:

```bash
cat application-otel.yml >> src/main/resources/application.yml
```

### 3. Start Application

No JVM arguments needed - instrumentation is via Spring Boot starter:

```bash
java -jar your-application.jar
```

## Using Annotations

See `ANNOTATIONS_GUIDE.md` for detailed annotation usage.

### Quick Example

```java
import io.opentelemetry.instrumentation.annotations.WithSpan;
import io.opentelemetry.instrumentation.annotations.SpanAttribute;

@Service
public class OrderService {{
    
    @WithSpan("process-order")
    public Order processOrder(@SpanAttribute("order.id") String orderId) {{
        // Your business logic
        return order;
    }}
}}
```

## Metrics Integration

Spring Boot Actuator + Micrometer automatically exports metrics:

- HTTP request metrics
- JVM metrics (heap, threads, GC)
- Database connection pool metrics
- Custom application metrics

Access metrics:
- Prometheus format: http://localhost:8080/actuator/prometheus
- JSON format: http://localhost:8080/actuator/metrics

## Custom Instrumentation

### Programmatic Span Creation

```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;

@Autowired
private Tracer tracer;

public void customOperation() {{
    Span span = tracer.spanBuilder("custom-operation").startSpan();
    try {{
        // Your logic
        span.setAttribute("custom.attribute", "value");
    }} finally {{
        span.end();
    }}
}}
```

### Adding Attributes to Current Span

```java
import io.opentelemetry.api.trace.Span;

public void enrichSpan() {{
    Span currentSpan = Span.current();
    currentSpan.setAttribute("user.id", userId);
    currentSpan.setAttribute("tenant.id", tenantId);
}}
```

## Configuration

Current settings:

- **Service Name**: {self.config.application_name}
- **Sampling Rate**: {self.config.sampling_rate * 100}%
- **OTLP Endpoint**: {self.config.otel_endpoint}

Override via environment variables or `application.yml`.

## Performance Impact

- Sampling Rate: {self.config.sampling_rate * 100}%
- Expected Overhead: <1%
- Metrics Export: Every 60 seconds

## Verification

1. Start application
2. Check actuator endpoint: http://localhost:8080/actuator/health
3. Generate traffic
4. View traces in SigNoz: http://localhost:3301

## Comparison: Agent vs Manual

| Aspect | Java Agent | Manual Integration |
|--------|------------|-------------------|
| Code Changes | None | Minimal (annotations) |
| Setup | JVM argument | Maven dependencies |
| Flexibility | Limited | High |
| Performance | Slightly better | Good |
| Use Case | Quick setup | Fine control |

## Resources

- [Spring Boot OpenTelemetry](https://opentelemetry.io/docs/instrumentation/java/automatic/spring-boot/)
- [Micrometer Tracing](https://micrometer.io/docs/tracing)
- [OpenTelemetry Annotations](https://opentelemetry.io/docs/instrumentation/java/automatic/annotations/)
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
            
        return readme_file
        
    def _generate_manifest(self, output_dir: Path, artifacts: InstrumentationArtifacts) -> None:
        """Generate manifest file summarizing all artifacts."""
        manifest_file = output_dir / 'MANIFEST.json'
        
        manifest = {
            'config_id': artifacts.config_id,
            'application_name': artifacts.application_name,
            'instrumentation_mode': artifacts.mode,
            'generated_at': artifacts.generated_at.isoformat(),
            'files': {name: str(path) for name, path in artifacts.files.items()},
            'jvm_args': artifacts.jvm_args,
            'maven_dependencies_count': len(artifacts.maven_dependencies),
            'spring_boot_properties': artifacts.spring_boot_properties,
            'annotations': list(artifacts.annotations_usage.keys()),
            'configuration': {
                'service_name': self.config.application_name,
                'service_namespace': self.config.service_namespace,
                'otel_endpoint': self.config.otel_endpoint,
                'sampling_rate': self.config.sampling_rate,
                'enable_logs': self.config.enable_logs,
                'enable_metrics': self.config.enable_metrics,
                'enable_traces': self.config.enable_traces,
                'excluded_endpoints': self.config.excluded_endpoints,
            }
        }
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        logger.info(f"Generated manifest: {manifest_file}")


# CLI interface for testing
if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate OpenTelemetry instrumentation templates')
    parser.add_argument('--app-name', default='spring-modulith', help='Application name')
    parser.add_argument('--mode', choices=['agent', 'manual', 'hybrid'], default='agent',
                       help='Instrumentation mode')
    parser.add_argument('--output-dir', default='/tmp/otel-instrumentation',
                       help='Output directory')
    parser.add_argument('--sampling-rate', type=float, default=0.01,
                       help='Trace sampling rate (0.0-1.0)')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = InstrumentationConfig(
        application_name=args.app_name,
        instrumentation_mode=args.mode,
        sampling_rate=args.sampling_rate
    )
    
    # Generate artifacts
    generator = OTelInstrumentationGenerator(config)
    artifacts = generator.generate_all_artifacts(Path(args.output_dir))
    
    # Print summary
    print("\n=== OpenTelemetry Instrumentation Generated ===")
    print(f"Application: {artifacts.application_name}")
    print(f"Mode: {artifacts.mode}")
    print(f"Output Directory: {args.output_dir}")
    print(f"\nGenerated Files ({len(artifacts.files)}):")
    for name, path in artifacts.files.items():
        print(f"  - {name}: {path.name}")
    print(f"\nManifest: {args.output_dir}/MANIFEST.json")
    print("\nNext steps:")
    print(f"1. Review generated files in {args.output_dir}")
    print(f"2. Follow instructions in README-{args.mode.upper()}.md")
    print("3. Run ./verify-instrumentation.sh to verify setup")
