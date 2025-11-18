"""
Integration Tests for Infrastructure Services

Tests connectivity and basic operations with all infrastructure services
in the dev container environment.
"""

import pytest
from utils.service_utils import (
    get_service_config,
    get_postgres_connection_string,
    check_postgres_connection,
    check_redis_connection,
    check_minio_connection,
    check_clickhouse_connection,
    check_kafka_connection,
    check_all_services
)


class TestServiceConfiguration:
    """Test service configuration detection."""
    
    def test_get_service_config(self):
        """Test service configuration from environment."""
        config = get_service_config()
        
        assert config.postgres_host == 'postgres'
        assert config.postgres_port == 5432
        assert config.postgres_db == 'omega'
        assert config.redis_host == 'redis'
        assert config.redis_port == 6379
        assert config.minio_host == 'minio'
        assert config.minio_port == 9000
        assert config.clickhouse_host == 'clickhouse'
        assert config.clickhouse_port == 8123
        assert config.kafka_bootstrap_servers == 'kafka:9092'
    
    def test_postgres_connection_string(self):
        """Test PostgreSQL connection string generation."""
        conn_str = get_postgres_connection_string()
        
        assert 'postgresql://' in conn_str
        assert 'postgres:5432' in conn_str
        assert 'omega' in conn_str


class TestPostgreSQLConnectivity:
    """Test PostgreSQL connection and operations."""
    
    def test_postgres_connection(self):
        """Test PostgreSQL is accessible."""
        assert check_postgres_connection() is True
    
    def test_postgres_query(self):
        """Test basic PostgreSQL query."""
        import psycopg2
        config = get_service_config()
        
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        assert 'PostgreSQL' in version
        assert '15' in version  # PostgreSQL 15+
        
        cursor.close()
        conn.close()
    
    def test_postgres_pgvector_extension(self):
        """Test that pg_vector extension is available."""
        import psycopg2
        config = get_service_config()
        
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )
        
        cursor = conn.cursor()
        
        # Create extension if not exists
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        # Verify extension is installed
        cursor.execute("""
            SELECT extname FROM pg_extension WHERE extname = 'vector';
        """)
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'vector'
        
        cursor.close()
        conn.close()


class TestRedisConnectivity:
    """Test Redis connection and operations."""
    
    def test_redis_connection(self):
        """Test Redis is accessible."""
        assert check_redis_connection() is True
    
    def test_redis_operations(self):
        """Test basic Redis operations."""
        import redis
        config = get_service_config()
        
        client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True
        )
        
        # Set and get
        client.set('test_key', 'test_value')
        value = client.get('test_key')
        assert value == 'test_value'
        
        # Delete
        client.delete('test_key')
        assert client.get('test_key') is None


class TestMinIOConnectivity:
    """Test MinIO (S3-compatible storage) connection and operations."""
    
    def test_minio_connection(self):
        """Test MinIO is accessible."""
        assert check_minio_connection() is True
    
    def test_minio_bucket_operations(self):
        """Test MinIO bucket operations."""
        from minio import Minio
        from io import BytesIO
        config = get_service_config()
        
        client = Minio(
            f"{config.minio_host}:{config.minio_port}",
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=False
        )
        
        # Create test bucket
        bucket_name = "test-omega-bucket"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        # Upload object
        test_data = b"Test data for Omega"
        client.put_object(
            bucket_name,
            "test-object.txt",
            BytesIO(test_data),
            len(test_data)
        )
        
        # Download object
        response = client.get_object(bucket_name, "test-object.txt")
        data = response.read()
        assert data == test_data
        
        # Cleanup
        client.remove_object(bucket_name, "test-object.txt")
        response.close()
        response.release_conn()


class TestClickHouseConnectivity:
    """Test ClickHouse connection and operations."""
    
    def test_clickhouse_connection(self):
        """Test ClickHouse is accessible."""
        assert check_clickhouse_connection() is True
    
    def test_clickhouse_query(self):
        """Test basic ClickHouse query."""
        import requests
        from requests.auth import HTTPBasicAuth
        config = get_service_config()
        
        # Use HTTP interface with authentication
        response = requests.get(
            f"http://{config.clickhouse_host}:{config.clickhouse_port}",
            params={"query": "SELECT version()"},
            auth=HTTPBasicAuth(config.clickhouse_user, config.clickhouse_password)
        )
        
        assert response.status_code == 200
        assert len(response.text) > 0


class TestKafkaConnectivity:
    """Test Kafka connection and operations."""
    
    def test_kafka_connection(self):
        """Test Kafka is accessible."""
        assert check_kafka_connection() is True
    
    def test_kafka_producer_consumer(self):
        """Test Kafka producer and consumer."""
        from kafka import KafkaProducer, KafkaConsumer
        import json
        import time
        config = get_service_config()
        
        topic_name = "test-omega-topic"
        
        # Producer
        producer = KafkaProducer(
            bootstrap_servers=config.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        test_message = {"test": "data", "timestamp": time.time()}
        producer.send(topic_name, test_message)
        producer.flush()
        producer.close()
        
        # Consumer
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=config.kafka_bootstrap_servers,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        messages = []
        for message in consumer:
            messages.append(message.value)
            break  # Just read one message
        
        consumer.close()
        
        assert len(messages) > 0
        assert messages[0]['test'] == 'data'


class TestAllServices:
    """Test all services together."""
    
    def test_all_services_operational(self):
        """Test that all services are operational."""
        status = check_all_services()
        
        assert status['postgres'] is True
        assert status['redis'] is True
        assert status['minio'] is True
        assert status['clickhouse'] is True
        assert status['kafka'] is True
        
        # All services should be up
        assert all(status.values())
