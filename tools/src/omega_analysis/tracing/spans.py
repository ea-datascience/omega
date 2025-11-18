"""Custom spans and tracing decorators for analysis operations."""
import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Span
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .config import get_tracer


logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class SpanManager:
    """Manager for creating and managing custom spans."""
    
    def __init__(self, tracer_name: str = "omega_analysis"):
        self.tracer = get_tracer(tracer_name)
    
    @contextmanager
    def create_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None,
        links: Optional[list] = None
    ):
        """Create a synchronous span context."""
        with self.tracer.start_as_current_span(name, links=links) as span:
            try:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    @asynccontextmanager
    async def create_async_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None,
        links: Optional[list] = None
    ):
        """Create an asynchronous span context."""
        with self.tracer.start_as_current_span(name, links=links) as span:
            try:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def add_event(
        self,
        span: Span,
        name: str,
        attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Add an event to a span."""
        event_attributes = attributes or {}
        if timestamp:
            # Convert to nanoseconds since epoch
            timestamp_ns = int(timestamp.timestamp() * 1_000_000_000)
            span.add_event(name, event_attributes, timestamp_ns)
        else:
            span.add_event(name, event_attributes)
    
    def set_analysis_attributes(
        self,
        span: Span,
        analysis_id: str,
        analysis_type: str,
        project_path: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> None:
        """Set standard analysis attributes on a span."""
        span.set_attribute("analysis.id", analysis_id)
        span.set_attribute("analysis.type", analysis_type)
        
        if project_path:
            span.set_attribute("analysis.project_path", project_path)
        if language:
            span.set_attribute("analysis.language", language)
        if framework:
            span.set_attribute("analysis.framework", framework)
    
    def set_database_attributes(
        self,
        span: Span,
        operation: str,
        table: Optional[str] = None,
        query: Optional[str] = None
    ) -> None:
        """Set database operation attributes on a span."""
        span.set_attribute("db.operation", operation)
        if table:
            span.set_attribute("db.table", table)
        if query:
            # Truncate long queries
            if len(query) > 1000:
                query = query[:1000] + "..."
            span.set_attribute("db.query", query)
    
    def set_cache_attributes(
        self,
        span: Span,
        operation: str,
        key: str,
        hit: Optional[bool] = None,
        ttl: Optional[int] = None
    ) -> None:
        """Set cache operation attributes on a span."""
        span.set_attribute("cache.operation", operation)
        span.set_attribute("cache.key", key)
        if hit is not None:
            span.set_attribute("cache.hit", hit)
        if ttl is not None:
            span.set_attribute("cache.ttl", ttl)
    
    def set_storage_attributes(
        self,
        span: Span,
        operation: str,
        bucket: str,
        object_name: str,
        size: Optional[int] = None
    ) -> None:
        """Set storage operation attributes on a span."""
        span.set_attribute("storage.operation", operation)
        span.set_attribute("storage.bucket", bucket)
        span.set_attribute("storage.object_name", object_name)
        if size is not None:
            span.set_attribute("storage.size", size)


def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None,
    tracer_name: str = "omega_analysis"
) -> Callable[[F], F]:
    """Decorator to trace function calls."""
    def decorator(func: F) -> F:
        span_name = name or f"{func.__module__}.{func.__name__}"
        span_manager = SpanManager(tracer_name)
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with span_manager.create_async_span(span_name, attributes) as span:
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add arguments as attributes (careful with sensitive data)
                    if args:
                        span.set_attribute("function.args_count", len(args))
                    if kwargs:
                        span.set_attribute("function.kwargs_count", len(kwargs))
                        # Add non-sensitive kwargs
                        safe_kwargs = {k: v for k, v in kwargs.items() 
                                     if k not in ['password', 'token', 'secret', 'key']}
                        for k, v in safe_kwargs.items():
                            if isinstance(v, (str, int, float, bool)):
                                span.set_attribute(f"function.arg.{k}", v)
                    
                    start_time = datetime.utcnow()
                    span_manager.add_event(span, "function.start", {"timestamp": start_time.isoformat()})
                    
                    try:
                        result = await func(*args, **kwargs)
                        
                        end_time = datetime.utcnow()
                        duration = (end_time - start_time).total_seconds()
                        
                        span.set_attribute("function.duration_seconds", duration)
                        span_manager.add_event(span, "function.end", {
                            "timestamp": end_time.isoformat(),
                            "duration_seconds": duration
                        })
                        
                        return result
                        
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with span_manager.create_span(span_name, attributes) as span:
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add arguments as attributes
                    if args:
                        span.set_attribute("function.args_count", len(args))
                    if kwargs:
                        span.set_attribute("function.kwargs_count", len(kwargs))
                    
                    start_time = datetime.utcnow()
                    span_manager.add_event(span, "function.start", {"timestamp": start_time.isoformat()})
                    
                    try:
                        result = func(*args, **kwargs)
                        
                        end_time = datetime.utcnow()
                        duration = (end_time - start_time).total_seconds()
                        
                        span.set_attribute("function.duration_seconds", duration)
                        span_manager.add_event(span, "function.end", {
                            "timestamp": end_time.isoformat(),
                            "duration_seconds": duration
                        })
                        
                        return result
                        
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            
            return sync_wrapper
    
    return decorator


def trace_analysis(
    analysis_type: str,
    attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None
) -> Callable[[F], F]:
    """Decorator specifically for analysis operations."""
    def decorator(func: F) -> F:
        base_attributes = {"analysis.type": analysis_type}
        if attributes:
            base_attributes.update(attributes)
        
        return trace_function(
            name=f"analysis.{analysis_type}.{func.__name__}",
            attributes=base_attributes
        )(func)
    
    return decorator


def trace_database_operation(
    operation: str,
    table: Optional[str] = None
) -> Callable[[F], F]:
    """Decorator for database operations."""
    def decorator(func: F) -> F:
        attributes = {"db.operation": operation}
        if table:
            attributes["db.table"] = table
        
        return trace_function(
            name=f"db.{operation}.{func.__name__}",
            attributes=attributes
        )(func)
    
    return decorator


def trace_cache_operation(operation: str) -> Callable[[F], F]:
    """Decorator for cache operations."""
    def decorator(func: F) -> F:
        return trace_function(
            name=f"cache.{operation}.{func.__name__}",
            attributes={"cache.operation": operation}
        )(func)
    
    return decorator


def trace_storage_operation(operation: str) -> Callable[[F], F]:
    """Decorator for storage operations."""
    def decorator(func: F) -> F:
        return trace_function(
            name=f"storage.{operation}.{func.__name__}",
            attributes={"storage.operation": operation}
        )(func)
    
    return decorator


# Global span manager instance
_span_manager: Optional[SpanManager] = None


def get_span_manager() -> SpanManager:
    """Get global span manager."""
    global _span_manager
    
    if _span_manager is None:
        _span_manager = SpanManager()
    
    return _span_manager