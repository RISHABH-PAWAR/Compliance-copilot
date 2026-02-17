"""Structured Logging Configuration"""
import structlog
import logging
from app.config import get_settings

settings = get_settings()


def setup_logging():
    """Configure structured logging with structlog"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.DEBUG else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """Get a structured logger instance"""
    return structlog.get_logger(name or __name__)


# Initialize logging on import
setup_logging()
logger = get_logger("compliance_copilot")
