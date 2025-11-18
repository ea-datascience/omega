"""
End-to-End Integration Test

Tests that all components work together: Java environment, infrastructure services,
and utility modules for the Omega migration analysis system.
"""

import pytest
from utils.java_utils import require_java, get_java_environment
from utils.service_utils import check_all_services, get_service_config, get_postgres_connection_string


class TestEndToEndIntegration:
    """Test complete environment integration."""
    
    def test_java_environment_available(self):
        """Verify Java 17+ is available."""
        env = require_java()
        
        assert env.is_valid
        assert env.major_version >= 17
        assert env.java_executable.exists()
    
    def test_all_infrastructure_services_available(self):
        """Verify all infrastructure services are operational."""
        status = check_all_services()
        
        # All services must be up
        assert status['postgres'] is True, "PostgreSQL not available"
        assert status['redis'] is True, "Redis not available"
        assert status['minio'] is True, "MinIO not available"
        assert status['clickhouse'] is True, "ClickHouse not available"
        assert status['kafka'] is True, "Kafka not available"
    
    def test_service_configuration_complete(self):
        """Verify service configuration is complete."""
        config = get_service_config()
        
        # Check all required config is present
        assert config.postgres_host == 'postgres'
        assert config.postgres_port == 5432
        assert config.redis_host == 'redis'
        assert config.minio_host == 'minio'
        assert config.clickhouse_host == 'clickhouse'
        assert config.kafka_bootstrap_servers == 'kafka:9092'
    
    def test_database_connection_string_format(self):
        """Verify database connection string is properly formatted."""
        conn_str = get_postgres_connection_string()
        
        assert conn_str.startswith('postgresql://')
        assert 'omega' in conn_str
        assert 'postgres:5432' in conn_str
    
    def test_java_and_postgres_integration(self):
        """Test Java is available for database-driven analysis."""
        # Java environment must be ready
        java_env = get_java_environment()
        assert java_env.is_valid
        
        # Database must be ready
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
        
        # Store Java version in database as metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metadata (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            INSERT INTO system_metadata (key, value)
            VALUES ('java_version', %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
        """, (java_env.version,))
        
        conn.commit()
        
        # Verify data was stored
        cursor.execute("SELECT value FROM system_metadata WHERE key = 'java_version';")
        stored_version = cursor.fetchone()[0]
        
        assert stored_version == java_env.version
        
        cursor.close()
        conn.close()
    
    def test_complete_analysis_workflow_simulation(self):
        """Simulate a complete analysis workflow using all components."""
        import psycopg2
        import redis
        from minio import Minio
        from io import BytesIO
        import json
        
        # 1. Verify Java is available for analysis
        java_env = require_java()
        assert java_env.major_version >= 17
        
        # 2. Get service configuration
        config = get_service_config()
        
        # 3. Store analysis metadata in PostgreSQL
        pg_conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )
        
        cursor = pg_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id SERIAL PRIMARY KEY,
                codebase_name VARCHAR(255),
                java_version VARCHAR(50),
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            INSERT INTO analysis_runs (codebase_name, java_version, status)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, ('spring-modulith', java_env.version, 'completed'))
        
        analysis_id = cursor.fetchone()[0]
        pg_conn.commit()
        cursor.close()
        pg_conn.close()
        
        # 4. Cache analysis result in Redis
        redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True
        )
        
        analysis_result = {
            'analysis_id': analysis_id,
            'codebase': 'spring-modulith',
            'java_version': java_env.version,
            'status': 'completed',
            'findings': {
                'total_classes': 150,
                'services': 12,
                'repositories': 8
            }
        }
        
        redis_client.setex(
            f'analysis:{analysis_id}',
            3600,  # 1 hour TTL
            json.dumps(analysis_result)
        )
        
        # Verify cache
        cached = redis_client.get(f'analysis:{analysis_id}')
        assert cached is not None
        assert json.loads(cached)['analysis_id'] == analysis_id
        
        # 5. Store analysis artifacts in MinIO
        minio_client = Minio(
            f"{config.minio_host}:{config.minio_port}",
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=False
        )
        
        bucket_name = "analysis-artifacts"
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        
        artifact_data = json.dumps(analysis_result, indent=2).encode('utf-8')
        minio_client.put_object(
            bucket_name,
            f"analysis-{analysis_id}.json",
            BytesIO(artifact_data),
            len(artifact_data),
            content_type='application/json'
        )
        
        # Verify artifact
        response = minio_client.get_object(bucket_name, f"analysis-{analysis_id}.json")
        stored_data = json.loads(response.read().decode('utf-8'))
        assert stored_data['analysis_id'] == analysis_id
        
        response.close()
        response.release_conn()
        
        # Cleanup
        redis_client.delete(f'analysis:{analysis_id}')
        minio_client.remove_object(bucket_name, f"analysis-{analysis_id}.json")
        
        # All workflow steps completed successfully
        assert True


class TestDevelopmentReadiness:
    """Verify development environment is production-ready."""
    
    def test_all_required_components_present(self):
        """Verify all required components are present and functional."""
        # Java
        java_env = get_java_environment()
        assert java_env.is_valid
        
        # Services
        services = check_all_services()
        assert all(services.values()), f"Some services down: {services}"
        
        # Configuration
        config = get_service_config()
        assert config.postgres_host is not None
        assert config.redis_host is not None
        assert config.minio_host is not None
        assert config.clickhouse_host is not None
        assert config.kafka_bootstrap_servers is not None
    
    def test_environment_ready_for_static_analysis(self):
        """Verify environment is ready for static analysis tasks."""
        # Java 17+ required for modern Spring Boot analysis
        java_env = require_java()
        assert java_env.major_version >= 17
        
        # PostgreSQL with pg_vector for storing analysis
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
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        assert cursor.fetchone() is not None, "pg_vector extension not installed"
        
        cursor.close()
        conn.close()
        
        # Redis for caching analysis results
        assert check_all_services()['redis'] is True
        
        # MinIO for storing artifacts
        assert check_all_services()['minio'] is True
