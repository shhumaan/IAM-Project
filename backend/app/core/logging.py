"""Logging configuration module for AzureShield IAM."""
import logging
import sys
from typing import Any, Dict

from app.core.config import settings

def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    # Create logger
    logger = logging.getLogger("azureshield")
    logger.setLevel(settings.LOG_LEVEL)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(settings.LOG_LEVEL)
    logging.getLogger("sqlalchemy.engine").setLevel(settings.LOG_LEVEL)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(f"azureshield.{name}")

# Create default logger
logger = setup_logging() 