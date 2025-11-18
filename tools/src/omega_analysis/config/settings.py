"""Configuration settings models with validation."""
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from pydantic.networks import AnyHttpUrl
from pathlib import Path
import secrets


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    user: str = Field(default="omega", env="DB_USER")
    password: str = Field(env="DB_PASSWORD")
    name: str = Field(default="omega_analysis", env="DB_NAME")
    
    # Connection pool settings
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # SSL settings
    ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")
    ssl_cert: Optional[str] = Field(default=None, env="DB_SSL_CERT")
    ssl_key: Optional[str] = Field(default=None, env="DB_SSL_KEY")
    ssl_ca: Optional[str] = Field(default=None, env="DB_SSL_CA")
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """Get async database URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    # Connection pool settings
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    
    # Cluster settings
    cluster_mode: bool = Field(default=False, env="REDIS_CLUSTER_MODE")
    cluster_nodes: List[str] = Field(default=[], env="REDIS_CLUSTER_NODES")
    
    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"


class MinIOSettings(BaseSettings):
    """MinIO object storage settings."""
    
    endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    access_key: str = Field(env="MINIO_ACCESS_KEY")
    secret_key: str = Field(env="MINIO_SECRET_KEY")
    secure: bool = Field(default=False, env="MINIO_SECURE")
    region: str = Field(default="us-east-1", env="MINIO_REGION")
    
    # Bucket settings
    default_bucket: str = Field(default="omega-analysis", env="MINIO_DEFAULT_BUCKET")
    presigned_url_expiry: int = Field(default=3600, env="MINIO_PRESIGNED_URL_EXPIRY")
    
    class Config:
        env_prefix = "MINIO_"


class ObservabilitySettings(BaseSettings):
    """Observability and monitoring settings."""
    
    # OpenTelemetry settings
    otlp_endpoint: Optional[str] = Field(default=None, env="OTLP_ENDPOINT")
    service_name: str = Field(default="omega-analysis", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Metrics settings
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=8001, env="METRICS_PORT")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    logging_enabled: bool = Field(default=True, env="LOGGING_ENABLED")
    
    # Tracing settings
    trace_sample_rate: float = Field(default=1.0, env="TRACE_SAMPLE_RATE")
    
    # Health check settings
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ["json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()
    
    class Config:
        env_prefix = "OBSERVABILITY_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    # JWT settings
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["http://localhost:4200"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # API key settings
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    api_keys: List[str] = Field(default=[], env="API_KEYS")
    
    class Config:
        env_prefix = "SECURITY_"


class AnalysisSettings(BaseSettings):
    """Analysis engine configuration settings."""
    
    # Worker settings
    max_concurrent_analyses: int = Field(default=5, env="MAX_CONCURRENT_ANALYSES")
    analysis_timeout: int = Field(default=3600, env="ANALYSIS_TIMEOUT")  # 1 hour
    worker_threads: int = Field(default=4, env="WORKER_THREADS")
    
    # Tool settings
    java_home: Optional[str] = Field(default=None, env="JAVA_HOME")
    maven_home: Optional[str] = Field(default=None, env="MAVEN_HOME")
    gradle_home: Optional[str] = Field(default=None, env="GRADLE_HOME")
    
    # Analysis tool paths
    sonarqube_url: Optional[str] = Field(default=None, env="SONARQUBE_URL")
    sonarqube_token: Optional[str] = Field(default=None, env="SONARQUBE_TOKEN")
    codeql_path: Optional[str] = Field(default=None, env="CODEQL_PATH")
    
    # File processing
    max_file_size: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    allowed_extensions: List[str] = Field(
        default=[".java", ".kt", ".scala", ".groovy", ".xml", ".yml", ".yaml", ".properties", ".json"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Temporary storage
    temp_dir: str = Field(default="/tmp/omega-analysis", env="TEMP_DIR")
    cleanup_temp_files: bool = Field(default=True, env="CLEANUP_TEMP_FILES")
    
    class Config:
        env_prefix = "ANALYSIS_"


class APISettings(BaseSettings):
    """API server configuration settings."""
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    
    # Request settings
    max_request_size: int = Field(default=100 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 100MB
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    
    # Documentation
    docs_enabled: bool = Field(default=True, env="DOCS_ENABLED")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")
    
    class Config:
        env_prefix = "API_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    api: APISettings = Field(default_factory=APISettings)
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            """Customize settings sources priority."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )