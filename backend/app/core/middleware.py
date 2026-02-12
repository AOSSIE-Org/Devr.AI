"""
Error handling middleware for comprehensive error tracking and standardized responses.
"""
import json
import logging
import time
import traceback
import uuid
from typing import Any, Dict, Optional

from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and logging requests/responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        # Log incoming request
        start_time = time.time()
        await self._log_request(request, correlation_id)
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Log successful response
            await self._log_response(request, response, process_time, correlation_id)
            
            return response
            
        except BaseAPIException as exc:
            # Handle custom API exceptions
            return await self._handle_api_exception(exc, correlation_id, request)
            
        except RequestValidationError as exc:
            # Handle request validation errors
            return await self._handle_validation_error(exc, correlation_id, request)
            
        except Exception as exc:
            # Handle unexpected errors
            return await self._handle_unexpected_error(exc, correlation_id, request)
    
    async def _log_request(self, request: Request, correlation_id: str):
        """Log incoming request details."""
        try:
            body = await request.body()
            body_str = body.decode('utf-8') if body else None
            
            # Don't log sensitive data
            if body_str and any(field in body_str.lower() for field in ['password', 'token', 'key']):
                body_str = "[REDACTED]"
            
            logger.info(
                f"Incoming request - Method: {request.method}, "
                f"URL: {request.url}, "
                f"Headers: {dict(request.headers)}, "
                f"Body: {body_str}, "
                f"Correlation-ID: {correlation_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to log request: {e}")
    
    async def _log_response(self, request: Request, response: Response, process_time: float, correlation_id: str):
        """Log response details."""
        logger.info(
            f"Response sent - Status: {response.status_code}, "
            f"Process-Time: {process_time:.4f}s, "
            f"Correlation-ID: {correlation_id}"
        )
    
    async def _handle_api_exception(self, exc: BaseAPIException, correlation_id: str, request: Request) -> JSONResponse:
        """Handle custom API exceptions."""
        error_response = {
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path),
                "context": exc.context
            }
        }
        
        # Log error with appropriate level
        if exc.status_code >= 500:
            logger.error(
                f"Server error - {exc.error_code}: {exc.detail}, "
                f"Correlation-ID: {correlation_id}, "
                f"Context: {exc.context}"
            )
        else:
            logger.warning(
                f"Client error - {exc.error_code}: {exc.detail}, "
                f"Correlation-ID: {correlation_id}, "
                f"Context: {exc.context}"
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_validation_error(self, exc: RequestValidationError, correlation_id: str, request: Request) -> JSONResponse:
        """Handle request validation errors."""
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path),
                "details": error_details
            }
        }
        
        logger.warning(
            f"Validation error - Correlation-ID: {correlation_id}, "
            f"Errors: {error_details}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_unexpected_error(self, exc: Exception, correlation_id: str, request: Request) -> JSONResponse:
        """Handle unexpected errors."""
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path)
            }
        }
        
        # Log full traceback for debugging
        logger.error(
            f"Unexpected error - {type(exc).__name__}: {str(exc)}, "
            f"Correlation-ID: {correlation_id}, "
            f"Traceback: {traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Lightweight middleware for request/response logging without error handling."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Calculate and log response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            f"Response: {response.status_code} - {process_time:.4f}s"
        )
        
        return response


def setup_error_handlers(app):
    """Setup custom error handlers for the FastAPI app."""
    
    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        """Handle custom API exceptions."""
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        error_response = {
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path),
                "context": exc.context
            }
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path),
                "details": error_details
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}, "
            f"Correlation-ID: {correlation_id}, "
            f"Traceback: {traceback.format_exc()}"
        )
        
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "timestamp": time.time(),
                "path": str(request.url.path)
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )