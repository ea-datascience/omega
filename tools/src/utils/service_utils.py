"""
Service Connection Utilities

Provides connection management for Omega infrastructure services:
- PostgreSQL 15+ with pg_vector for analysis artifacts
- ClickHouse for analytics and time-series data
- Redis for caching and session management
- MinIO for file storage (S3-compatible)
- Apache Kafka for event streaming

All services are pre-configured in the dev container environment.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for infrastructure services."""
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    clickhouse_host: str
    clickhouse_port: int
    clickhouse_user: str
    clickhouse_password: str
    redis_host: str
    redis_port: int
    minio_host: str
    minio_port: int
    minio_access_key: str
    minio_secret_key: str
    kafka_bootstrap_servers: str


class ServiceConnectionError(Exception):
    """Raised when service connection fails."""
    pass


def get_service_config() -> ServiceConfig:
    """
    Get service configuration from environment variables.
    
    Returns:
        ServiceConfig with all service connection details
    """
    return ServiceConfig(
        postgres_host=os.getenv('POSTGRES_HOST', 'localhost'),
        postgres_port=int(os.getenv('POSTGRES_PORT', '5432')),
        postgres_db=os.getenv('POSTGRES_DB', 'omega'),
        postgres_user=os.getenv('POSTGRES_USER', 'omega'),
        postgres_password=os.getenv('POSTGRES_PASSWORD', 'omega_dev'),
        clickhouse_host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        clickhouse_port=int(os.getenv('CLICKHOUSE_PORT', '8123')),
        clickhouse_user=os.getenv('CLICKHOUSE_USER', 'omega'),
        clickhouse_password=os.getenv('CLICKHOUSE_PASSWORD', 'omega_dev'),
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', '6379')),
        minio_host=os.getenv('MINIO_HOST', 'localhost'),
        minio_port=int(os.getenv('MINIO_PORT', '9000')),
        minio_access_key=os.getenv('MINIO_ACCESS_KEY', 'omega'),
        minio_secret_key=os.getenv('MINIO_SECRET_KEY', 'omega_dev_secret'),
        kafka_bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    )


def get_postgres_connection_string(config: Optional[ServiceConfig] = None) -> str:
    """
    Get PostgreSQL connection string.
    
    Args:
        config: Optional ServiceConfig, defaults to environment config
        
    Returns:
        PostgreSQL connection string for SQLAlchemy
    """
    if config is None:
        config = get_service_config()
    
    return (
        f"postgresql://{config.postgres_user}:{config.postgres_password}"
        f"@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"
    )


def get_postgres_async_connection_string(config: Optional[ServiceConfig] = None) -> str:
    """
    Get PostgreSQL async connection string for asyncpg.
    
    Args:
        config: Optional ServiceConfig, defaults to environment config
        
    Returns:
        PostgreSQL async connection string
    """
    if config is None:
        config = get_service_config()
    
    return (
        f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password}"
        f"@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"
    )


def check_postgres_connection() -> bool:
    """
    Check if PostgreSQL is accessible.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        import psycopg2
        config = get_service_config()
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )
        conn.close()
        logger.info("PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}")
        return False


def check_redis_connection() -> bool:
    """
    Check if Redis is accessible.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        import redis
        config = get_service_config()
        client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True
        )
        client.ping()
        logger.info("Redis connection successful")
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return False


def check_minio_connection() -> bool:
    """
    Check if MinIO is accessible.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from minio import Minio
        config = get_service_config()
        client = Minio(
            f"{config.minio_host}:{config.minio_port}",
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=False
        )
        # List buckets to verify connection
        list(client.list_buckets())
        logger.info("MinIO connection successful")
        return True
    except Exception as e:
        logger.warning(f"MinIO connection failed: {e}")
        return False


def check_clickhouse_connection() -> bool:
    """
    Check if ClickHouse is accessible.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        config = get_service_config()
        response = requests.get(
            f"http://{config.clickhouse_host}:{config.clickhouse_port}/ping",
            auth=HTTPBasicAuth(config.clickhouse_user, config.clickhouse_password)
        )
        success = response.status_code == 200
        if success:
            logger.info("ClickHouse connection successful")
        return success
    except Exception as e:
        logger.warning(f"ClickHouse connection failed: {e}")
        return False


def check_kafka_connection() -> bool:
    """
    Check if Kafka is accessible.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from kafka import KafkaProducer
        from kafka.errors import KafkaError
        config = get_service_config()
        producer = KafkaProducer(
            bootstrap_servers=config.kafka_bootstrap_servers,
            request_timeout_ms=5000
        )
        producer.close()
        logger.info("Kafka connection successful")
        return True
    except Exception as e:
        logger.warning(f"Kafka connection failed: {e}")
        return False


def check_all_services() -> Dict[str, bool]:
    """
    Check connectivity to all infrastructure services.
    
    Returns:
        Dictionary mapping service names to connection status
    """
    return {
        'postgres': check_postgres_connection(),
        'redis': check_redis_connection(),
        'minio': check_minio_connection(),
        'clickhouse': check_clickhouse_connection(),
        'kafka': check_kafka_connection()
    }


def print_service_status():
    """Print status of all infrastructure services."""
    config = get_service_config()
    
    print("=" * 60)
    print("Omega Infrastructure Services")
    print("=" * 60)
    print(f"PostgreSQL:  {config.postgres_host}:{config.postgres_port}")
    print(f"ClickHouse:  {config.clickhouse_host}:{config.clickhouse_port}")
    print(f"Redis:       {config.redis_host}:{config.redis_port}")
    print(f"MinIO:       {config.minio_host}:{config.minio_port}")
    print(f"Kafka:       {config.kafka_bootstrap_servers}")
    print("=" * 60)
    print("\nChecking service connectivity...")
    print("-" * 60)
    
    status = check_all_services()
    
    for service, is_connected in status.items():
        status_str = "✓ Connected" if is_connected else "✗ Unavailable"
        print(f"{service.capitalize():12} {status_str}")
    
    print("-" * 60)
    
    all_connected = all(status.values())
    if all_connected:
        print("\nAll services are operational!")
    else:
        disconnected = [s for s, connected in status.items() if not connected]
        print(f"\nWarning: {len(disconnected)} service(s) unavailable: {', '.join(disconnected)}")
        print("Make sure docker-compose services are running.")
    
    print("=" * 60)


if __name__ == "__main__":
    # Command-line utility to check service status
    import sys
    
    try:
        print_service_status()
        sys.exit(0)
    except Exception as e:
        print(f"Error checking services: {e}", file=sys.stderr)
        sys.exit(1)
