# Quickstart Guide: System Discovery and Baseline Assessment

**Feature**: Epic 1.1 - System Discovery and Baseline Assessment  
**Date**: November 17, 2025  
**Phase**: Phase 1 - Design & Contracts

## Overview

This quickstart guide provides developers and operators with step-by-step instructions to deploy, configure, and use the System Discovery and Baseline Assessment platform for analyzing Spring Boot monoliths and preparing for microservices migration.

## Prerequisites

### System Requirements

- **Docker**: Version 20.10+ with Docker Compose v2
- **Git**: Version 2.30+ for source code access
- **Python**: Version 3.12+ (for development and CLI tools)
- **Node.js**: Version 18+ (for dashboard frontend)
- **Minimum Hardware**: 8GB RAM, 4 CPU cores, 100GB storage
- **Recommended Hardware**: 16GB RAM, 8 CPU cores, 500GB SSD storage

### Access Requirements

- **Git Repository Access**: Read access to target monolith repositories
- **Network Access**: Ability to deploy observability agents (if runtime analysis required)
- **Authentication**: OAuth 2.0/OIDC provider configuration (for enterprise deployment)
- **Permissions**: Docker container execution, port binding (8000-8010 range)

### Analysis Target Requirements

- **Supported Systems**: Spring Boot 2.0+, Spring MVC, Java EE applications
- **Build System**: Maven or Gradle with accessible POM/build files
- **Source Code**: Git repository with main/master branch access
- **Documentation**: Optional but recommended (README, architecture docs)

## Quick Start (5 Minutes)

### Step 1: Clone and Start the Platform

```bash
# Clone the Omega analysis platform
git clone https://github.com/ea-datascience/omega.git
cd omega

# Start the platform services
docker-compose up -d

# Verify services are running
docker-compose ps
```

Expected services:
- `analysis-engine`: Core analysis orchestration service
- `postgres`: Analysis metadata and results database
- `redis`: Caching and session management
- `signoz`: Observability and monitoring stack
- `dashboard`: Web-based user interface

### Step 2: Access the Dashboard

1. Open your browser to `http://localhost:3000`
2. Log in with default credentials (development only):
   - Username: `admin@omega.local`
   - Password: `admin123`
3. You should see the Analysis Projects dashboard

### Step 3: Create Your First Analysis Project

1. Click **"New Analysis Project"**
2. Fill in the project details:
   - **Name**: `My Spring Boot Analysis`
   - **Repository URL**: `https://github.com/spring-projects/spring-petclinic.git`
   - **Target System**: `Spring Boot`
   - **Description**: `Analysis of Pet Clinic reference application`
3. Click **"Create Project"**

### Step 4: Start Analysis

1. Click **"Start Analysis"** on your newly created project
2. Select analysis types:
   - ✅ **Static Analysis** (Context Mapper, Structurizr, CodeQL)
   - ✅ **Runtime Analysis** (SigNoz observability - synthetic load testing)
   - ✅ **Gap Analysis** (Compare static vs runtime findings)
   - ✅ **Risk Assessment** (Migration readiness scoring)
3. Click **"Begin Analysis"**

### Step 5: Monitor Progress and Review Results

1. Watch the progress indicator update in real-time
2. Expected completion time: 15-30 minutes for Pet Clinic
3. Review results in the **Analysis Results** tab:
   - **System Architecture**: C4 diagrams and domain boundaries
   - **Dependencies**: Static and runtime dependency graphs
   - **Performance**: Baseline metrics and bottleneck analysis
   - **Risks**: Migration complexity and readiness assessment
   - **Boundaries**: Recommended service extraction points

## Detailed Setup Guide

### Development Environment Setup

#### 1. Local Development with Hot Reload

```bash
# Install development dependencies
pip install -r requirements-dev.txt
npm install -g @angular/cli

# Start backend in development mode
cd tools/
python -m uvicorn src.api.main:app --reload --port 8000

# Start frontend in development mode
cd dashboard/
ng serve --port 3000

# Start supporting services
docker-compose -f docker-compose.dev.yml up -d postgres redis signoz
```

#### 2. IDE Configuration

**VS Code Extensions**:
- Python
- Docker
- REST Client
- GraphQL

**IntelliJ IDEA Plugins**:
- Python
- Docker
- GraphQL
- OpenAPI

### Production Deployment

#### 1. Environment Configuration

Create `.env` file with production settings:

```bash
# Database Configuration
POSTGRES_HOST=postgres.prod.internal
POSTGRES_DB=omega_analysis
POSTGRES_USER=omega_user
POSTGRES_PASSWORD=secure_password_here

# Redis Configuration
REDIS_URL=redis://redis.prod.internal:6379

# Authentication
OAUTH_PROVIDER_URL=https://auth.company.com
OAUTH_CLIENT_ID=omega-analysis-platform
OAUTH_CLIENT_SECRET=oauth_secret_here

# Analysis Configuration
MAX_CONCURRENT_ANALYSES=5
ANALYSIS_TIMEOUT_HOURS=4
ENABLE_RUNTIME_ANALYSIS=true

# Monitoring
SIGNOZ_ENDPOINT=https://signoz.prod.internal
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

#### 2. Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace omega-analysis

# Apply configurations
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress/

# Verify deployment
kubectl get pods -n omega-analysis
kubectl get services -n omega-analysis
```

#### 3. Database Migration

```bash
# Run database migrations
docker run --rm \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  omega/analysis-engine:latest \
  python -m alembic upgrade head

# Verify schema
docker run --rm \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  omega/analysis-engine:latest \
  python -c "from src.models import Base; print('Schema verified')"
```

## API Usage Examples

### REST API Examples

#### Create Analysis Project

```bash
curl -X POST http://localhost:8000/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "E-commerce Platform Analysis",
    "description": "Migration readiness assessment for legacy e-commerce system",
    "repository_url": "https://github.com/company/ecommerce-monolith.git",
    "repository_branch": "main",
    "target_system_type": "spring_boot",
    "analysis_configuration": {
      "enable_appcat": true,
      "enable_copilot": false,
      "static_analysis_depth": "comprehensive",
      "runtime_analysis_duration_hours": 48
    }
  }'
```

#### Start Analysis

```bash
curl -X POST http://localhost:8000/v1/projects/{PROJECT_ID}/analysis \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "analysis_types": ["static", "runtime", "gap_analysis", "risk_assessment"],
    "static_analysis_config": {
      "tools": ["context_mapper", "structurizr", "codeql", "appcat"],
      "depth": "comprehensive"
    },
    "runtime_analysis_config": {
      "environment_type": "development",
      "collection_duration_hours": 48,
      "instrumentation_level": "detailed"
    }
  }'
```

#### Get Analysis Results

```bash
curl -X GET http://localhost:8000/v1/projects/{PROJECT_ID}/analysis/architecture \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

curl -X GET http://localhost:8000/v1/projects/{PROJECT_ID}/analysis/dependencies?graph_type=combined \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

curl -X GET http://localhost:8000/v1/projects/{PROJECT_ID}/assessments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### GraphQL Examples

#### Query Analysis Results

```graphql
query GetProjectAnalysis($projectId: UUID!) {
  project(id: $projectId) {
    id
    name
    status
    progressPercentage
    overallHealthScore
    migrationReadinessScore
    
    systemArchitecture {
      architectureStyle
      qualityMetrics {
        maintainabilityIndex
        technicalDebtHours
      }
      c4Model {
        contextDiagram {
          systems {
            name
            type
            responsibilities
          }
        }
      }
    }
    
    dependencyGraphs(graphType: COMBINED) {
      confidenceScore
      couplingMetrics {
        averageCoupling
        highlyTiedComponents
      }
      stronglyConnectedComponents {
        componentCount
        cyclomaticComplexity
      }
    }
    
    riskAssessments {
      overallRiskScore
      migrationComplexityScore
      goNoGoRecommendation
      highRiskAreas {
        area
        riskLevel
        mitigationStrategy
      }
    }
    
    serviceBoundaries {
      boundaryName
      extractionComplexity
      effortEstimateDays
      confidenceLevel
      architectApproval
    }
  }
}
```

#### Query Cross-Project Comparisons

```graphql
query MigrationReadinessComparison($projectIds: [UUID!]!) {
  migrationReadinessComparison(projectIds: $projectIds) {
    projectName
    overallScore
    technicalReadiness
    organizationalReadiness
    riskLevel
    estimatedDuration
    recommendedApproach
  }
}
```

### CLI Usage

#### Install CLI Tool

```bash
pip install omega-analysis-cli

# Configure authentication
omega auth configure --provider oauth2 --client-id YOUR_CLIENT_ID

# Verify installation
omega --version
omega projects list
```

#### CLI Commands

```bash
# Create project
omega projects create \
  --name "My Analysis Project" \
  --repo https://github.com/company/monolith.git \
  --type spring_boot

# Start analysis
omega analyze start PROJECT_ID \
  --static-analysis \
  --runtime-analysis \
  --duration 48h

# Monitor progress
omega analyze status PROJECT_ID --follow

# Get results
omega results architecture PROJECT_ID --format json
omega results dependencies PROJECT_ID --graph-type combined
omega results boundaries PROJECT_ID --approved-only

# Generate reports
omega reports generate PROJECT_ID \
  --type technical_detailed \
  --format pdf \
  --output ./analysis-report.pdf
```

## Configuration Reference

### Analysis Configuration Options

```yaml
# Static Analysis Configuration
static_analysis:
  tools:
    context_mapper:
      enabled: true
      ddd_patterns: ["bounded_context", "aggregate", "domain_service"]
      analysis_depth: "comprehensive"
    
    structurizr:
      enabled: true
      c4_levels: ["context", "container", "component"]
      diagram_formats: ["plantuml", "mermaid"]
    
    codeql:
      enabled: true
      security_queries: true
      compliance_queries: true
      custom_queries_path: "./custom-queries/"
    
    microsoft_appcat:
      enabled: true
      azure_optimization: true
      migration_patterns: ["app_service", "container_apps", "aks"]

# Runtime Analysis Configuration
runtime_analysis:
  signoz:
    enabled: true
    sampling_rate: 0.1  # 10% sampling for performance
    trace_retention_days: 30
    metrics_retention_days: 90
  
  instrumentation:
    auto_instrument: true
    custom_spans: true
    database_tracing: true
    external_service_tracing: true
  
  load_generation:
    enabled: true  # for development/staging environments
    scenario_file: "./load-scenarios.yml"
    duration_minutes: 120

# Gap Analysis Configuration
gap_analysis:
  enabled: true
  coupling_threshold: 7.0  # 0-10 scale
  confidence_threshold: 0.8  # 0-1 scale
  ignore_test_dependencies: true

# Risk Assessment Configuration
risk_assessment:
  enabled: true
  risk_tolerance: "medium"  # low, medium, high
  business_impact_weight: 0.3
  technical_risk_weight: 0.4
  organizational_risk_weight: 0.3
  
# Human-in-the-Loop Configuration
validation:
  require_architect_approval: true
  auto_approve_low_risk: false
  approval_timeout_days: 7
  notification_channels: ["email", "slack"]
```

### Environment Variables Reference

```bash
# Core Platform
OMEGA_ENV=production
OMEGA_DEBUG=false
OMEGA_LOG_LEVEL=INFO
OMEGA_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/omega
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Cache
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Authentication
OAUTH_PROVIDER_URL=https://auth.company.com
OAUTH_CLIENT_ID=omega-platform
OAUTH_CLIENT_SECRET=secret
JWT_SECRET_KEY=jwt-signing-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Analysis Limits
MAX_CONCURRENT_ANALYSES=10
ANALYSIS_TIMEOUT_HOURS=6
MAX_CODEBASE_SIZE_MB=2048
ENABLE_LARGE_CODEBASE_ANALYSIS=false

# Monitoring
SIGNOZ_ENDPOINT=http://signoz:3301
ENABLE_OPENTELEMETRY=true
METRICS_PORT=9090
HEALTH_CHECK_PORT=8080

# Storage
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
ANALYSIS_ARTIFACTS_BUCKET=omega-analysis-artifacts

# External Integrations
ENABLE_GITHUB_COPILOT=false
GITHUB_COPILOT_LICENSE_TYPE=enterprise
ENABLE_MICROSOFT_APPCAT=true
APPCAT_BINARY_PATH=/usr/local/bin/appcat

# Feature Flags
ENABLE_RUNTIME_ANALYSIS=true
ENABLE_GAP_ANALYSIS=true
ENABLE_RISK_ASSESSMENT=true
ENABLE_COMPLIANCE_SCANNING=true
ENABLE_HUMAN_VALIDATION=true
```

## Troubleshooting

### Common Issues

#### 1. Analysis Fails to Start

**Symptoms**: Project status remains "queued" or fails immediately

**Solutions**:
```bash
# Check service logs
docker-compose logs analysis-engine
docker-compose logs postgres

# Verify repository access
git clone YOUR_REPOSITORY_URL --depth 1

# Check configuration
curl http://localhost:8000/health
```

#### 2. Runtime Analysis No Data

**Symptoms**: Performance baselines show no metrics

**Solutions**:
```bash
# Verify SigNoz is running
curl http://localhost:3301/api/v1/version

# Check instrumentation
docker-compose logs signoz

# Verify synthetic load generation
curl http://localhost:8000/v1/projects/PROJECT_ID/baselines
```

#### 3. Memory Issues During Analysis

**Symptoms**: Analysis fails with out-of-memory errors

**Solutions**:
```bash
# Increase Docker memory limits
# In docker-compose.yml:
services:
  analysis-engine:
    mem_limit: 8g
    
# Configure Java heap for analysis tools
export JAVA_OPTS="-Xmx4g -Xms2g"

# Enable incremental analysis
# In analysis configuration:
incremental_analysis: true
chunk_size_mb: 100
```

#### 4. Permission Denied Errors

**Symptoms**: Cannot access repositories or write analysis results

**Solutions**:
```bash
# Check file permissions
ls -la /path/to/analysis/workspace

# Fix Docker volume permissions
sudo chown -R $USER:$USER ./analysis-workspace

# Configure Git credentials
git config --global credential.helper store
```

### Performance Tuning

#### 1. Analysis Performance

```yaml
# Optimize for speed
performance_mode: "fast"
parallel_analysis: true
max_parallel_tools: 4
skip_non_critical_scans: true

# Optimize for accuracy
performance_mode: "comprehensive"
deep_analysis: true
extended_runtime_collection: true
manual_validation_required: true
```

#### 2. Resource Management

```bash
# Monitor resource usage
docker stats

# Scale horizontally
docker-compose up --scale analysis-engine=3

# Configure resource limits
docker-compose exec analysis-engine htop
```

### Getting Help

#### 1. Log Analysis

```bash
# Collect comprehensive logs
docker-compose logs --tail=1000 > omega-logs.txt

# Enable debug logging
export OMEGA_LOG_LEVEL=DEBUG
docker-compose restart analysis-engine

# Analysis-specific logs
curl http://localhost:8000/v1/projects/PROJECT_ID/logs
```

#### 2. Health Checks

```bash
# System health
curl http://localhost:8000/health | jq

# Service dependencies
curl http://localhost:8000/health/dependencies | jq

# Analysis engine status
curl http://localhost:8000/health/analysis-engine | jq
```

#### 3. Support Channels

- **Documentation**: https://omega-migration.readthedocs.io
- **GitHub Issues**: https://github.com/ea-datascience/omega/issues
- **Community Forum**: https://discuss.omega-migration.io
- **Enterprise Support**: support@omega-migration.com

## Next Steps

After completing your first analysis:

1. **Review Results**: Examine architecture diagrams, dependency graphs, and risk assessments
2. **Validate Findings**: Use human-in-the-loop validation for critical boundaries
3. **Plan Migration**: Use service boundary recommendations to plan extraction sequence
4. **Iterate**: Re-run analysis after code changes to track improvement
5. **Scale Up**: Analyze additional monoliths in your portfolio

For advanced usage, refer to the [Complete Documentation](../plan.md) and [API Reference](./contracts/).

---

**Need Help?** This quickstart covers the essentials. For production deployments, advanced configuration, and enterprise features, consult the full documentation or contact our support team.