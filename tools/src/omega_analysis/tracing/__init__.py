"""OpenTelemetry tracing infrastructure for Omega Analysis system."""
import os
from .config import TracingManager
from ..config.settings import ObservabilitySettings

# Global tracing manager instance
_tracing_manager = None


def setup_tracing(
    service_name: str = "omega-analysis",
    service_version: str = "0.1.0",
    environment: str = None,
    otlp_endpoint: str = None
) -> None:
    """Set up OpenTelemetry tracing."""
    global _tracing_manager
    
    if _tracing_manager is not None:
        return  # Already initialized
    
    # Use environment variables if not provided
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    if otlp_endpoint is None:
        otlp_endpoint = os.getenv("OTLP_ENDPOINT")
    
    # Create observability settings
    settings = ObservabilitySettings(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        otlp_endpoint=otlp_endpoint,
        trace_sample_rate=float(os.getenv("TRACE_SAMPLE_RATE", "1.0")),
        metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
        logging_enabled=os.getenv("LOGGING_ENABLED", "true").lower() == "true"
    )
    
    # Initialize tracing manager
    _tracing_manager = TracingManager(settings)
    _tracing_manager.initialize()


def get_tracing_manager() -> TracingManager:
    """Get the global tracing manager instance."""
    return _tracing_manager