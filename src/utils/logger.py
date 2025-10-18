"""
Structured logging setup for Business Planner.

Uses structlog for structured JSON logging in production,
colorful console logging in development (debug mode).

User Preference: Serial output only in debug mode [[memory:7583598]]

Reference: .cursorrules (Logging Strategy section)
"""

import sys
import logging
import structlog
from structlog.types import FilteringBoundLogger


def setup_logging(debug: bool = False) -> None:
    """Setup structured logging.
    
    Args:
        debug: If True, use colorful console output (development)
               If False, use JSON output (production)
    
    User Preference: Serial output only when debug=True [[memory:7583598]]
    """
    
    if debug:
        # Development: Colorful console output
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
                structlog.dev.ConsoleRenderer(colors=True)  # Colorful!
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Production: JSON output (machine-readable)
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer()  # JSON for parsing
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )


# Global logger instance
logger: FilteringBoundLogger = structlog.get_logger()


# Convenience functions
def log_task_created(task_id: int, business_id: int, user_id: int, **kwargs) -> None:
    """Log task creation event."""
    logger.info(
        "task_created",
        task_id=task_id,
        business_id=business_id,
        user_id=user_id,
        **kwargs
    )


def log_task_completed(
    task_id: int,
    business_id: int,
    estimated: int | None,
    actual: int,
    accuracy: float | None,
    **kwargs
) -> None:
    """Log task completion with learning data."""
    logger.info(
        "task_completed_learning",
        task_id=task_id,
        business_id=business_id,
        estimated_duration=estimated,
        actual_duration=actual,
        accuracy=accuracy,
        **kwargs
    )


def log_ai_api_call(
    model: str,
    operation: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    cost_usd: float,
    success: bool = True,
    **kwargs
) -> None:
    """Log AI API call for cost tracking."""
    logger.info(
        "ai_api_call",
        model=model,
        operation=operation,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_ms=duration_ms,
        cost_usd=cost_usd,
        success=success,
        **kwargs
    )


def mask_sensitive(value: str, show_chars: int = 4) -> str:
    """Mask sensitive data in logs.
    
    Args:
        value: Sensitive string (API key, token, etc.)
        show_chars: Number of characters to show at end
    
    Returns:
        Masked string like "***MASKED***abc123"
    
    Example:
        >>> mask_sensitive("sk-proj-1234567890")
        "***MASKED***7890"
    """
    if not value or len(value) <= show_chars:
        return "***MASKED***"
    
    return f"***MASKED***{value[-show_chars:]}"


# Re-export for convenience
__all__ = [
    "setup_logging",
    "logger",
    "log_task_created",
    "log_task_completed",
    "log_ai_api_call",
    "mask_sensitive"
]

