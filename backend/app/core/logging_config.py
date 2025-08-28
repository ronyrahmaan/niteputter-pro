"""
Centralized Logging Configuration for NitePutter Pro
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> None:
    """
    Setup application logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        json_format: Use JSON formatting for logs
    """
    
    # Use settings if not provided
    if log_level is None:
        log_level = settings.log_level
    if log_file is None and settings.log_file:
        log_file = settings.log_file
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create formatters
    if json_format and settings.is_production:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        f"Logging configured - Level: {log_level}, "
        f"Environment: {settings.app_env}, "
        f"File: {log_file or 'None'}"
    )


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter to add context to logs"""
    
    def process(self, msg, kwargs):
        """Add extra context to log records"""
        extra = kwargs.get("extra", {})
        
        # Add request context if available
        if hasattr(self, "request_id"):
            extra["request_id"] = self.request_id
        if hasattr(self, "user_id"):
            extra["user_id"] = self.user_id
        if hasattr(self, "ip_address"):
            extra["ip_address"] = self.ip_address
        
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with optional context
    
    Args:
        name: Logger name (usually __name__)
        **context: Additional context to add to logs
    
    Returns:
        Logger adapter with context
    """
    logger = logging.getLogger(name)
    adapter = LoggerAdapter(logger, context)
    
    # Add context attributes
    for key, value in context.items():
        setattr(adapter, key, value)
    
    return adapter


# Predefined loggers for different components
def get_api_logger(**context) -> LoggerAdapter:
    """Get logger for API endpoints"""
    return get_logger("api", **context)


def get_db_logger(**context) -> LoggerAdapter:
    """Get logger for database operations"""
    return get_logger("database", **context)


def get_payment_logger(**context) -> LoggerAdapter:
    """Get logger for payment operations"""
    return get_logger("payment", **context)


def get_security_logger(**context) -> LoggerAdapter:
    """Get logger for security events"""
    return get_logger("security", **context)


def get_task_logger(**context) -> LoggerAdapter:
    """Get logger for background tasks"""
    return get_logger("task", **context)


# Audit logging for critical operations
class AuditLogger:
    """Logger for audit trail"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Ensure audit logs are always written to file
        if settings.log_file:
            audit_file = Path(settings.log_file).parent / "audit.log"
            handler = logging.handlers.RotatingFileHandler(
                audit_file,
                maxBytes=settings.log_max_bytes,
                backupCount=settings.log_backup_count
            )
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
    
    def log_login(self, user_id: str, ip_address: str, success: bool):
        """Log login attempt"""
        self.logger.info(
            f"Login {'successful' if success else 'failed'} for user {user_id}",
            extra={
                "event": "login",
                "user_id": user_id,
                "ip_address": ip_address,
                "success": success
            }
        )
    
    def log_payment(
        self, 
        user_id: str, 
        order_id: str, 
        amount: float, 
        status: str
    ):
        """Log payment transaction"""
        self.logger.info(
            f"Payment {status} for order {order_id}",
            extra={
                "event": "payment",
                "user_id": user_id,
                "order_id": order_id,
                "amount": amount,
                "status": status
            }
        )
    
    def log_data_access(
        self, 
        user_id: str, 
        resource: str, 
        action: str, 
        success: bool
    ):
        """Log data access"""
        self.logger.info(
            f"Data access: {action} on {resource}",
            extra={
                "event": "data_access",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "success": success
            }
        )
    
    def log_admin_action(
        self, 
        admin_id: str, 
        action: str, 
        target: str, 
        details: dict
    ):
        """Log admin action"""
        self.logger.warning(
            f"Admin action: {action} on {target}",
            extra={
                "event": "admin_action",
                "admin_id": admin_id,
                "action": action,
                "target": target,
                "details": details
            }
        )


# Create singleton audit logger
audit_logger = AuditLogger()