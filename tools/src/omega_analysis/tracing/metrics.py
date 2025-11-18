"""Metrics collection and monitoring for analysis operations."""
import time
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from contextlib import contextmanager

from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram, UpDownCounter, Gauge

from .config import get_meter


logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self, meter_name: str = "omega_analysis"):
        self.meter = get_meter(meter_name)
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize metric instruments."""
        # Analysis metrics
        self.analysis_requests_total = self.meter.create_counter(
            name="analysis_requests_total",
            description="Total number of analysis requests",
            unit="1"
        )
        
        self.analysis_duration = self.meter.create_histogram(
            name="analysis_duration_seconds",
            description="Duration of analysis operations",
            unit="s"
        )
        
        self.analysis_active = self.meter.create_up_down_counter(
            name="analysis_active",
            description="Number of active analysis operations",
            unit="1"
        )
        
        self.analysis_errors_total = self.meter.create_counter(
            name="analysis_errors_total",
            description="Total number of analysis errors",
            unit="1"
        )
        
        # Database metrics
        self.db_operations_total = self.meter.create_counter(
            name="db_operations_total",
            description="Total number of database operations",
            unit="1"
        )
        
        self.db_duration = self.meter.create_histogram(
            name="db_duration_seconds",
            description="Duration of database operations",
            unit="s"
        )
        
        self.db_connections_active = self.meter.create_up_down_counter(
            name="db_connections_active",
            description="Number of active database connections",
            unit="1"
        )
        
        # Cache metrics
        self.cache_operations_total = self.meter.create_counter(
            name="cache_operations_total",
            description="Total number of cache operations",
            unit="1"
        )
        
        self.cache_hits_total = self.meter.create_counter(
            name="cache_hits_total",
            description="Total number of cache hits",
            unit="1"
        )
        
        self.cache_misses_total = self.meter.create_counter(
            name="cache_misses_total",
            description="Total number of cache misses",
            unit="1"
        )
        
        # Storage metrics
        self.storage_operations_total = self.meter.create_counter(
            name="storage_operations_total",
            description="Total number of storage operations",
            unit="1"
        )
        
        self.storage_bytes_transferred = self.meter.create_counter(
            name="storage_bytes_transferred_total",
            description="Total bytes transferred to/from storage",
            unit="By"
        )
        
        # API metrics
        self.http_requests_total = self.meter.create_counter(
            name="http_requests_total",
            description="Total number of HTTP requests",
            unit="1"
        )
        
        self.http_request_duration = self.meter.create_histogram(
            name="http_request_duration_seconds",
            description="Duration of HTTP requests",
            unit="s"
        )
        
        # System metrics
        self.memory_usage = self.meter.create_gauge(
            name="memory_usage_bytes",
            description="Memory usage in bytes",
            unit="By"
        )
        
        self.cpu_usage = self.meter.create_gauge(
            name="cpu_usage_percent",
            description="CPU usage percentage",
            unit="%"
        )
    
    def record_analysis_request(
        self,
        analysis_type: str,
        status: str = "success",
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> None:
        """Record an analysis request."""
        attributes = {
            "analysis_type": analysis_type,
            "status": status
        }
        
        if language:
            attributes["language"] = language
        if framework:
            attributes["framework"] = framework
        
        self.analysis_requests_total.add(1, attributes)
        
        if status == "error":
            self.analysis_errors_total.add(1, attributes)
    
    def record_analysis_duration(
        self,
        duration_seconds: float,
        analysis_type: str,
        status: str = "success"
    ) -> None:
        """Record analysis duration."""
        self.analysis_duration.record(
            duration_seconds,
            {"analysis_type": analysis_type, "status": status}
        )
    
    def increment_active_analyses(self, analysis_type: str) -> None:
        """Increment active analysis counter."""
        self.analysis_active.add(1, {"analysis_type": analysis_type})
    
    def decrement_active_analyses(self, analysis_type: str) -> None:
        """Decrement active analysis counter."""
        self.analysis_active.add(-1, {"analysis_type": analysis_type})
    
    @contextmanager
    def track_analysis(self, analysis_type: str, **attributes):
        """Context manager to track analysis operation."""
        start_time = time.time()
        self.increment_active_analyses(analysis_type)
        
        try:
            yield
            
            # Record successful completion
            duration = time.time() - start_time
            self.record_analysis_duration(duration, analysis_type, "success")
            self.record_analysis_request(analysis_type, "success", **attributes)
            
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            self.record_analysis_duration(duration, analysis_type, "error")
            self.record_analysis_request(analysis_type, "error", **attributes)
            raise
        
        finally:
            self.decrement_active_analyses(analysis_type)
    
    def record_db_operation(
        self,
        operation: str,
        duration_seconds: float,
        table: Optional[str] = None,
        status: str = "success"
    ) -> None:
        """Record database operation."""
        attributes = {
            "operation": operation,
            "status": status
        }
        
        if table:
            attributes["table"] = table
        
        self.db_operations_total.add(1, attributes)
        self.db_duration.record(duration_seconds, attributes)
    
    def record_cache_operation(
        self,
        operation: str,
        hit: Optional[bool] = None,
        key_prefix: Optional[str] = None
    ) -> None:
        """Record cache operation."""
        attributes = {"operation": operation}
        
        if key_prefix:
            attributes["key_prefix"] = key_prefix
        
        self.cache_operations_total.add(1, attributes)
        
        if hit is not None:
            if hit:
                self.cache_hits_total.add(1, attributes)
            else:
                self.cache_misses_total.add(1, attributes)
    
    def record_storage_operation(
        self,
        operation: str,
        bytes_transferred: int = 0,
        bucket: Optional[str] = None,
        status: str = "success"
    ) -> None:
        """Record storage operation."""
        attributes = {
            "operation": operation,
            "status": status
        }
        
        if bucket:
            attributes["bucket"] = bucket
        
        self.storage_operations_total.add(1, attributes)
        
        if bytes_transferred > 0:
            self.storage_bytes_transferred.add(bytes_transferred, attributes)
    
    def record_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float
    ) -> None:
        """Record HTTP request."""
        attributes = {
            "method": method,
            "path": path,
            "status_code": str(status_code),
            "status_class": f"{status_code // 100}xx"
        }
        
        self.http_requests_total.add(1, attributes)
        self.http_request_duration.record(duration_seconds, attributes)
    
    def update_system_metrics(
        self,
        memory_usage_bytes: float,
        cpu_usage_percent: float
    ) -> None:
        """Update system metrics."""
        self.memory_usage.set(memory_usage_bytes)
        self.cpu_usage.set(cpu_usage_percent)


class CustomMetrics:
    """Custom metrics for specific analysis operations."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.meter = collector.meter
        
        # Analysis-specific metrics
        self.lines_of_code_analyzed = self.meter.create_counter(
            name="lines_of_code_analyzed_total",
            description="Total lines of code analyzed",
            unit="1"
        )
        
        self.files_analyzed = self.meter.create_counter(
            name="files_analyzed_total",
            description="Total number of files analyzed",
            unit="1"
        )
        
        self.vulnerabilities_found = self.meter.create_counter(
            name="vulnerabilities_found_total",
            description="Total number of vulnerabilities found",
            unit="1"
        )
        
        self.code_smells_found = self.meter.create_counter(
            name="code_smells_found_total",
            description="Total number of code smells found",
            unit="1"
        )
        
        self.dependencies_analyzed = self.meter.create_counter(
            name="dependencies_analyzed_total",
            description="Total number of dependencies analyzed",
            unit="1"
        )
        
        self.microservices_suggested = self.meter.create_counter(
            name="microservices_suggested_total",
            description="Total number of microservices suggested",
            unit="1"
        )
    
    def record_code_analysis(
        self,
        lines_of_code: int,
        files_count: int,
        language: str,
        project_type: str
    ) -> None:
        """Record code analysis metrics."""
        attributes = {
            "language": language,
            "project_type": project_type
        }
        
        self.lines_of_code_analyzed.add(lines_of_code, attributes)
        self.files_analyzed.add(files_count, attributes)
    
    def record_security_findings(
        self,
        vulnerabilities: int,
        severity: str,
        analysis_tool: str
    ) -> None:
        """Record security analysis findings."""
        attributes = {
            "severity": severity,
            "tool": analysis_tool
        }
        
        self.vulnerabilities_found.add(vulnerabilities, attributes)
    
    def record_quality_findings(
        self,
        code_smells: int,
        category: str,
        analysis_tool: str
    ) -> None:
        """Record code quality findings."""
        attributes = {
            "category": category,
            "tool": analysis_tool
        }
        
        self.code_smells_found.add(code_smells, attributes)
    
    def record_dependency_analysis(
        self,
        dependency_count: int,
        language: str,
        package_manager: str
    ) -> None:
        """Record dependency analysis."""
        attributes = {
            "language": language,
            "package_manager": package_manager
        }
        
        self.dependencies_analyzed.add(dependency_count, attributes)
    
    def record_microservice_suggestions(
        self,
        suggestion_count: int,
        decomposition_strategy: str,
        confidence_score: float
    ) -> None:
        """Record microservice decomposition suggestions."""
        attributes = {
            "strategy": decomposition_strategy,
            "confidence_level": "high" if confidence_score > 0.8 else "medium" if confidence_score > 0.6 else "low"
        }
        
        self.microservices_suggested.add(suggestion_count, attributes)


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None
_custom_metrics: Optional[CustomMetrics] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector


def get_custom_metrics() -> CustomMetrics:
    """Get custom metrics instance."""
    global _custom_metrics
    
    if _custom_metrics is None:
        collector = get_metrics_collector()
        _custom_metrics = CustomMetrics(collector)
    
    return _custom_metrics