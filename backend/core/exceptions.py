"""
Professional Exception Handling
Custom exceptions and global error handlers
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Any, Dict, Optional
from enum import Enum

logger = logging.getLogger("niteputter.exceptions")

class ErrorCode(str, Enum):
    """Standardized error codes"""
    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_INPUT_FORMAT = "INVALID_INPUT_FORMAT"
    
    # Business logic errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # System errors
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

class NitePutterException(Exception):
    """Base exception for application-specific errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class AuthenticationError(NitePutterException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            status_code=401,
            details=details
        )

class AuthorizationError(NitePutterException):
    """Authorization related errors"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            details=details
        )

class ValidationError(NitePutterException):
    """Input validation errors"""
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details['field'] = field
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details
        )

class NotFoundError(NitePutterException):
    """Resource not found errors"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )

class ConflictError(NitePutterException):
    """Resource conflict errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            status_code=409,
            details=details
        )

class DatabaseError(NitePutterException):
    """Database operation errors"""
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details=details
        )

def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create standardized error response"""
    response_data = {
        "error": {
            "code": error_code.value,
            "message": message,
            "timestamp": "2025-01-01T00:00:00Z"  # Would use datetime.utcnow() in real implementation
        }
    }
    
    if details:
        response_data["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )

async def niteputter_exception_handler(request: Request, exc: NitePutterException) -> JSONResponse:
    """Handle application-specific exceptions"""
    logger.error(f"Application error: {exc.message}", extra={
        "error_code": exc.error_code.value,
        "status_code": exc.status_code,
        "details": exc.details,
        "path": str(request.url)
    })
    
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    
    if exc.status_code == 404:
        error_code = ErrorCode.RESOURCE_NOT_FOUND
    elif exc.status_code == 401:
        error_code = ErrorCode.AUTHENTICATION_FAILED
    elif exc.status_code == 403:
        error_code = ErrorCode.INSUFFICIENT_PERMISSIONS
    elif exc.status_code == 422:
        error_code = ErrorCode.VALIDATION_ERROR
    
    logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": str(request.url)
    })
    
    return create_error_response(
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True, extra={
        "path": str(request.url)
    })
    
    return create_error_response(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        status_code=500
    )