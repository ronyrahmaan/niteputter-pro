"""
Professional Logging Configuration
Structured logging for production environments
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from config import settings

class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add service info
        log_record['service'] = settings.project_name
        log_record['version'] = settings.version
        log_record['environment'] = settings.environment
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

class HealthFilter(logging.Filter):
    """Filter out health check requests to reduce noise"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Filter out health check endpoints
        message = record.getMessage()
        return '/health' not in message and '/api/' not in message

def setup_logging():
    """Configure application logging"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.log_format.lower() == 'json':
        formatter = CustomJSONFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add health filter in production
    if settings.is_production:
        console_handler.addFilter(HealthFilter())
    
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    
    return root_logger

# Application logger
logger = logging.getLogger("niteputter")

def log_request(request_id: str, method: str, path: str, user_id: str = None):
    """Log incoming requests"""
    extra = {'request_id': request_id}
    if user_id:
        extra['user_id'] = user_id
    
    logger.info(f"{method} {path}", extra=extra)

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log errors with context"""
    extra = context or {}
    logger.error(f"Error: {str(error)}", exc_info=True, extra=extra)