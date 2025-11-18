"""Logging configuration and setup for Omega Analysis system."""
import logging
import logging.config
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from .formatters import JSONFormatter, StructuredLogger
from .correlation import CorrelationIDFilter


def setup_logging(
    level: str = "INFO",
    service_name: str = "omega-analysis",
    service_version: str = "1.0.0",
    environment: str = "development",
    log_file: Optional[str] = None,
    json_format: bool = True,
    include_trace: bool = True
) -> None:
    """Set up structured logging configuration."""
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    if json_format:
        formatter = JSONFormatter(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            include_trace=include_trace
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Create correlation ID filter
    correlation_filter = CorrelationIDFilter()
    
    # Configure handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(correlation_filter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "service_name": service_name,
            "service_version": service_version,
            "environment": environment,
            "log_level": level,
            "json_format": json_format,
            "log_file": log_file
        }
    )


def get_logging_config(
    level: str = "INFO",
    service_name: str = "omega-analysis",
    service_version: str = "1.0.0",
    environment: str = "development",
    log_file: Optional[str] = None
) -> Dict[str, Any]:
    """Get logging configuration dictionary."""
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
                "service_name": service_name,
                "service_version": service_version,
                "environment": environment,
                "include_trace": True
            },
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "filters": {
            "correlation": {
                "()": CorrelationIDFilter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "json",
                "filters": ["correlation"],
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "omega_analysis": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "alembic": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add file handler if specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": level,
            "formatter": "json",
            "filters": ["correlation"],
            "filename": log_file
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "file" not in logger_config["handlers"]:
                logger_config["handlers"].append("file")
    
    return config


class LoggingMiddleware:
    """ASGI middleware for request/response logging."""
    
    def __init__(self, app, logger_name: str = "omega_analysis.middleware"):
        self.app = app
        self.logger = StructuredLogger(logger_name)
    
    async def __call__(self, scope, receive, send):
        """Process ASGI request with logging."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request information
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        client = scope.get("client")
        
        request_info = {
            "method": method,
            "path": path,
            "query_string": query_string,
            "client_ip": client[0] if client else None,
            "client_port": client[1] if client else None
        }
        
        self.logger.info("Request started", **request_info)
        
        # Wrap send to capture response
        response_info = {"status_code": None, "response_size": 0}
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_info["status_code"] = message["status"]
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_info["response_size"] += len(body)
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
            
            self.logger.info(
                "Request completed",
                **request_info,
                **response_info
            )
            
        except Exception as e:
            self.logger.error(
                "Request failed",
                **request_info,
                error=str(e),
                error_type=type(e).__name__
            )
            raise