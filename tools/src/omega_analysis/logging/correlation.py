"""Correlation ID management for distributed tracing."""
import uuid
from contextvars import ContextVar
from typing import Optional


# Context variable to store correlation ID across async calls
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    return correlation_id.get()


def set_correlation_id(cid: str) -> None:
    """Set the correlation ID in context."""
    correlation_id.set(cid)


def ensure_correlation_id() -> str:
    """Ensure a correlation ID exists, creating one if necessary."""
    cid = get_correlation_id()
    if cid is None:
        cid = generate_correlation_id()
        set_correlation_id(cid)
    return cid


class CorrelationIDFilter:
    """Logging filter to add correlation ID to log records."""
    
    def filter(self, record):
        """Add correlation ID to the log record."""
        record.correlation_id = get_correlation_id() or "none"
        return True