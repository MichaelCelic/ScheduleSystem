import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import logger, set_request_id, log_request

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        
        # Add request ID to response headers
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request started",
            extra={
                "event_type": "request_started",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log successful response
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log error response
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "event_type": "request_failed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise 