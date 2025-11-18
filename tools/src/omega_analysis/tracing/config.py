"""OpenTelemetry configuration and initialization."""
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import os

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
# Note: Some instrumentation packages are not available
# from opentelemetry.instrumentation.requests import RequestsInstrumentor
# from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.propagate import set_global_textmap
# from opentelemetry.propagators.b3 import B3MultiFormat  # Not available

from ..config.settings import ObservabilitySettings


logger = logging.getLogger(__name__)


class TracingManager:
    """Manages OpenTelemetry tracing configuration and lifecycle."""
    
    def __init__(self, settings: ObservabilitySettings):
        self.settings = settings
        self._tracer_provider: Optional[TracerProvider] = None
        self._meter_provider: Optional[MeterProvider] = None
        self._initialized = False
        self._instrumentors = []
    
    def initialize(self) -> None:
        """Initialize OpenTelemetry tracing."""
        try:
            # Create resource
            resource = Resource.create({
                SERVICE_NAME: self.settings.service_name,
                SERVICE_VERSION: self.settings.service_version,
                DEPLOYMENT_ENVIRONMENT: self.settings.environment,
                "service.namespace": "omega-analysis",
                "service.instance.id": os.getenv("HOSTNAME", "unknown")
            })
            
            # Initialize tracing
            self._setup_tracing(resource)
            
            # Initialize metrics
            self._setup_metrics(resource)
            
            # Set up propagators (B3MultiFormat not available)
            # set_global_textmap(B3MultiFormat())
            
            # Auto-instrument libraries
            self._setup_auto_instrumentation()
            
            self._initialized = True
            logger.info("OpenTelemetry tracing initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry tracing: {e}")
            raise
    
    def _setup_tracing(self, resource: Resource) -> None:
        """Set up tracing provider and exporters."""
        # Create tracer provider
        self._tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self._tracer_provider)
        
        # Add span processors
        if self.settings.otlp_endpoint:
            # OTLP exporter for SigNoz
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.settings.otlp_endpoint,
                insecure=not self.settings.otlp_endpoint.startswith("https://")
            )
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            self._tracer_provider.add_span_processor(otlp_processor)
            logger.info(f"Added OTLP span exporter: {self.settings.otlp_endpoint}")
        else:
            # Console exporter for development
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            self._tracer_provider.add_span_processor(console_processor)
            logger.info("Added console span exporter")
    
    def _setup_metrics(self, resource: Resource) -> None:
        """Set up metrics provider and exporters."""
        # Create metric readers
        readers = []
        
        if self.settings.otlp_endpoint:
            # OTLP metric exporter
            otlp_metric_exporter = OTLPMetricExporter(
                endpoint=self.settings.otlp_endpoint,
                insecure=not self.settings.otlp_endpoint.startswith("https://")
            )
            readers.append(PeriodicExportingMetricReader(otlp_metric_exporter))
            logger.info("Added OTLP metric exporter")
        else:
            # Console metric exporter for development
            console_metric_exporter = ConsoleMetricExporter()
            readers.append(PeriodicExportingMetricReader(console_metric_exporter))
            logger.info("Added console metric exporter")
        
        # Create meter provider
        self._meter_provider = MeterProvider(
            resource=resource,
            metric_readers=readers
        )
        metrics.set_meter_provider(self._meter_provider)
    
    def _setup_auto_instrumentation(self) -> None:
        """Set up automatic instrumentation for common libraries."""
        try:
            # FastAPI instrumentation
            fastapi_instrumentor = FastAPIInstrumentor()
            fastapi_instrumentor.instrument()
            self._instrumentors.append(fastapi_instrumentor)
            logger.debug("Enabled FastAPI instrumentation")
            
            # SQLAlchemy instrumentation
            sqlalchemy_instrumentor = SQLAlchemyInstrumentor()
            sqlalchemy_instrumentor.instrument()
            self._instrumentors.append(sqlalchemy_instrumentor)
            logger.debug("Enabled SQLAlchemy instrumentation")
            
            # Redis instrumentation
            redis_instrumentor = RedisInstrumentor()
            redis_instrumentor.instrument()
            self._instrumentors.append(redis_instrumentor)
            logger.debug("Enabled Redis instrumentation")
            
            # Note: HTTP requests and AsyncPG instrumentation packages not available
            # Would add requests and asyncpg instrumentation here if packages were available
            logger.debug("Skipped requests and AsyncPG instrumentation (packages not available)")
            
        except Exception as e:
            logger.warning(f"Some instrumentations may not be available: {e}")
    
    def shutdown(self) -> None:
        """Shutdown tracing and clean up resources."""
        try:
            # Uninstall instrumentors
            for instrumentor in self._instrumentors:
                try:
                    instrumentor.uninstrument()
                except Exception as e:
                    logger.warning(f"Failed to uninstall instrumentor: {e}")
            
            # Shutdown tracer provider
            if self._tracer_provider:
                self._tracer_provider.shutdown()
            
            # Shutdown meter provider
            if self._meter_provider:
                self._meter_provider.shutdown()
            
            self._initialized = False
            logger.info("OpenTelemetry tracing shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during tracing shutdown: {e}")
    
    def get_tracer(self, name: str, version: Optional[str] = None) -> trace.Tracer:
        """Get a tracer instance."""
        if not self._initialized:
            raise RuntimeError("Tracing not initialized")
        
        return trace.get_tracer(name, version or self.settings.service_version)
    
    def get_meter(self, name: str, version: Optional[str] = None) -> metrics.Meter:
        """Get a meter instance."""
        if not self._initialized:
            raise RuntimeError("Tracing not initialized")
        
        return metrics.get_meter(name, version or self.settings.service_version)
    
    @property
    def is_initialized(self) -> bool:
        """Check if tracing is initialized."""
        return self._initialized
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracing statistics."""
        return {
            "initialized": self._initialized,
            "service_name": self.settings.service_name,
            "service_version": self.settings.service_version,
            "environment": self.settings.environment,
            "otlp_endpoint": self.settings.otlp_endpoint,
            "instrumentors_count": len(self._instrumentors),
            "instrumentors": [type(i).__name__ for i in self._instrumentors]
        }


# Global tracing manager
_tracing_manager: Optional[TracingManager] = None


def initialize_tracing(settings: Optional[ObservabilitySettings] = None) -> TracingManager:
    """Initialize global tracing manager."""
    global _tracing_manager
    
    if _tracing_manager is None:
        if settings is None:
            from ..config import get_settings
            settings = get_settings().observability
        
        _tracing_manager = TracingManager(settings)
        _tracing_manager.initialize()
    
    return _tracing_manager


def get_tracing_manager() -> Optional[TracingManager]:
    """Get global tracing manager."""
    return _tracing_manager


def shutdown_tracing() -> None:
    """Shutdown global tracing manager."""
    global _tracing_manager
    
    if _tracing_manager:
        _tracing_manager.shutdown()
        _tracing_manager = None


def get_tracer(name: str, version: Optional[str] = None) -> trace.Tracer:
    """Get a tracer instance."""
    manager = get_tracing_manager()
    if manager:
        return manager.get_tracer(name, version)
    else:
        # Return no-op tracer if tracing not initialized
        return trace.NoOpTracer()


def get_meter(name: str, version: Optional[str] = None) -> metrics.Meter:
    """Get a meter instance."""
    manager = get_tracing_manager()
    if manager:
        return manager.get_meter(name, version)
    else:
        # Return no-op meter if tracing not initialized
        from opentelemetry.metrics import NoOpMeter
        return NoOpMeter(name)