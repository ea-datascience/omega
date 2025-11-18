# Omega Infrastructure Services

The Omega dev container includes a complete infrastructure stack for migration analysis and system discovery. All services are automatically configured and orchestrated via Docker Compose.

## Available Services

### PostgreSQL 15 with pg_vector
- **Purpose**: Primary database for analysis artifacts, system metadata, and vector embeddings
- **Host**: `postgres:5432` (from containers) or `localhost:5432` (from host)
- **Database**: `omega`
- **Credentials**: `omega` / `omega_dev`
- **Extensions**: pg_vector for semantic search and similarity analysis

### ClickHouse
- **Purpose**: Analytics database for time-series data, metrics, and performance analysis
- **Hosts**: 
  - HTTP: `clickhouse:8123` or `localhost:8123`
  - Native: `clickhouse:9000` or `localhost:9000`
- **Use Cases**: Migration metrics, performance tracking, historical analysis

### Redis
- **Purpose**: Caching layer and session management
- **Host**: `redis:6379` (from containers) or `localhost:6379` (from host)
- **Configuration**: Persistence enabled (AOF)
- **Use Cases**: Cache analysis results, job queues, temporary data

### MinIO
- **Purpose**: S3-compatible object storage for files and artifacts
- **Hosts**:
  - API: `minio:9000` or `localhost:9000`
  - Console: `http://localhost:9001`
- **Credentials**: `omega` / `omega_dev_secret`
- **Use Cases**: Store codebases, reports, documentation, build artifacts

### Apache Kafka
- **Purpose**: Event streaming for asynchronous processing
- **Host**: `kafka:9092` (from containers) or `localhost:9092` (from host)
- **Configuration**: Single-node KRaft mode (no Zookeeper)
- **Use Cases**: Migration events, analysis pipelines, system notifications

## Quick Start

### Check Service Status

From the dev container:

```bash
cd /workspace/tools
python -m src.utils.service_utils
```

Expected output:
```
============================================================
Omega Infrastructure Services
============================================================
PostgreSQL:  postgres:5432
ClickHouse:  clickhouse:8123
Redis:       redis:6379
MinIO:       minio:9000
Kafka:       kafka:9092
============================================================

Checking service connectivity...
------------------------------------------------------------
Postgres     ✓ Connected
Redis        ✓ Connected
Minio        ✓ Connected
Clickhouse   ✓ Connected
Kafka        ✓ Connected
------------------------------------------------------------

All services are operational!
============================================================
```

### Use in Python Code

```python
from utils.service_utils import (
    get_service_config,
    get_postgres_connection_string,
    check_all_services
)

# Get service configuration
config = get_service_config()
print(f"PostgreSQL at {config.postgres_host}:{config.postgres_port}")

# Get database connection string
db_url = get_postgres_connection_string()
# Returns: postgresql://omega:omega_dev@postgres:5432/omega

# Check all services
status = check_all_services()
if status['postgres']:
    print("Database is ready!")
```

## Service Connection Examples

### PostgreSQL with SQLAlchemy

```python
from sqlalchemy import create_engine
from utils.service_utils import get_postgres_connection_string

engine = create_engine(get_postgres_connection_string())

with engine.connect() as conn:
    result = conn.execute("SELECT version()")
    print(result.fetchone())
```

### PostgreSQL with asyncpg

```python
import asyncpg
from utils.service_utils import get_service_config

config = get_service_config()

conn = await asyncpg.connect(
    host=config.postgres_host,
    port=config.postgres_port,
    database=config.postgres_db,
    user=config.postgres_user,
    password=config.postgres_password
)
```

### Redis

```python
import redis
from utils.service_utils import get_service_config

config = get_service_config()
client = redis.Redis(
    host=config.redis_host,
    port=config.redis_port,
    decode_responses=True
)

client.set('key', 'value')
print(client.get('key'))
```

### MinIO (S3-compatible)

```python
from minio import Minio
from utils.service_utils import get_service_config

config = get_service_config()
client = Minio(
    f"{config.minio_host}:{config.minio_port}",
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key,
    secure=False
)

# Create bucket
if not client.bucket_exists("analysis-artifacts"):
    client.make_bucket("analysis-artifacts")

# Upload file
client.fput_object(
    "analysis-artifacts",
    "report.json",
    "/path/to/report.json"
)
```

### ClickHouse

```python
import requests
from utils.service_utils import get_service_config

config = get_service_config()
base_url = f"http://{config.clickhouse_host}:{config.clickhouse_port}"

# Execute query
response = requests.post(
    f"{base_url}",
    data="SELECT version()"
)
print(response.text)
```

### Apache Kafka

```python
from kafka import KafkaProducer, KafkaConsumer
from utils.service_utils import get_service_config

config = get_service_config()

# Producer
producer = KafkaProducer(
    bootstrap_servers=config.kafka_bootstrap_servers
)
producer.send('migration-events', b'Event data')
producer.flush()

# Consumer
consumer = KafkaConsumer(
    'migration-events',
    bootstrap_servers=config.kafka_bootstrap_servers
)
for message in consumer:
    print(message.value)
```

## Managing Services

### Start Services

Services start automatically with the dev container. To start manually:

```bash
cd /workspace/.devcontainer
docker-compose up -d
```

### Stop Services

```bash
cd /workspace/.devcontainer
docker-compose down
```

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f kafka
```

### Restart a Service

```bash
docker-compose restart postgres
```

### Access Service Consoles

- **MinIO Console**: http://localhost:9001
  - Username: `omega`
  - Password: `omega_dev_secret`

- **ClickHouse**: http://localhost:8123
  - Query via HTTP: `curl http://localhost:8123/?query=SELECT+1`

## Data Persistence

All services use Docker volumes for data persistence:

- `postgres-data`: PostgreSQL database files
- `clickhouse-data`: ClickHouse data
- `redis-data`: Redis AOF files
- `minio-data`: Object storage files
- `kafka-data`: Kafka topics and logs

Data persists across container restarts but can be cleared:

```bash
# WARNING: This deletes all data
docker-compose down -v
```

## Network Configuration

All services are connected via the `omega-network` bridge network:

- Services can communicate using service names (e.g., `postgres`, `redis`)
- Host machine can access via `localhost` and mapped ports
- Services are isolated from external networks

## Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# Services show "healthy" status when ready
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>

# Recreate service
docker-compose up -d --force-recreate <service-name>
```

### Connection Refused

1. Verify service is running: `docker-compose ps`
2. Check service health: `docker-compose ps | grep healthy`
3. Wait for health check to pass (may take 10-30 seconds)
4. Check logs for errors: `docker-compose logs <service-name>`

### Port Already in Use

If host ports conflict with existing services:

```bash
# Stop conflicting service on host
sudo systemctl stop postgresql  # Example for PostgreSQL

# Or modify ports in docker-compose.yml
```

### Data Corruption

```bash
# Stop services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume rm devcontainer_postgres-data

# Restart
docker-compose up -d
```

## Security Notes

**Development Environment Only**

The provided configuration is for development use only:

- Default credentials are NOT secure
- Services accept connections without encryption
- No authentication on some services
- Open port exposure

**For Production:**

1. Use strong, unique passwords
2. Enable TLS/SSL encryption
3. Restrict network access
4. Use secrets management
5. Enable authentication on all services
6. Follow security best practices for each service

## Required Python Packages

Install client libraries as needed:

```bash
# PostgreSQL
uv add psycopg2-binary asyncpg sqlalchemy

# Redis
uv add redis

# MinIO
uv add minio

# ClickHouse
uv add clickhouse-driver

# Kafka
uv add kafka-python

# Or install all at once
uv add psycopg2-binary asyncpg sqlalchemy redis minio clickhouse-driver kafka-python
```

## Architecture Patterns

### Service Layer Pattern

```python
# services/database.py
from utils.service_utils import get_postgres_connection_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(get_postgres_connection_string())
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Caching Pattern

```python
# Use Redis for caching expensive operations
import redis
from utils.service_utils import get_service_config

config = get_service_config()
cache = redis.Redis(host=config.redis_host, port=config.redis_port)

def get_analysis(codebase_id: str):
    # Check cache first
    cached = cache.get(f"analysis:{codebase_id}")
    if cached:
        return json.loads(cached)
    
    # Perform analysis
    result = perform_expensive_analysis(codebase_id)
    
    # Cache result for 1 hour
    cache.setex(f"analysis:{codebase_id}", 3600, json.dumps(result))
    
    return result
```

### Event-Driven Pattern

```python
# Publish migration events to Kafka
from kafka import KafkaProducer
from utils.service_utils import get_service_config

config = get_service_config()
producer = KafkaProducer(
    bootstrap_servers=config.kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_migration_event(event_type: str, data: dict):
    producer.send('migration-events', {
        'type': event_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    })
    producer.flush()
```

## Next Steps

1. Install required Python packages for services you'll use
2. Run `python -m src.utils.service_utils` to verify connectivity
3. Review service-specific documentation for advanced features
4. Implement service layer patterns in your application code
5. Configure backup strategies for production deployments
