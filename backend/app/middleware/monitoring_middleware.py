"""
Middleware for automatic request monitoring.
Captures all requests and sends metrics to the monitoring service.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from app.monitoring import get_monitoring_service

logger = logging.getLogger("uvicorn")


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically tracks all HTTP requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.monitoring_service = get_monitoring_service()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Extract request info
        endpoint = request.url.path
        method = request.method
        
        # Record request start
        start_time = self.monitoring_service.metrics_collector.record_request_start(
            request_id=request_id,
            endpoint=endpoint,
            method=method
        )
        
        # Initialize metadata
        metadata = {
            "user_agent": request.headers.get("user-agent", "unknown"),
            "client_ip": self._get_client_ip(request),
        }
        
        error = None
        status_code = 500  # Default to error
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
            # Add response headers for tracing
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            error = str(e)
            logger.error(f"Request {request_id} failed: {e}", exc_info=True)
            raise
            
        finally:
            # Record request end
            self.monitoring_service.metrics_collector.record_request_end(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                start_time=start_time,
                status_code=status_code,
                error=error,
                metadata=metadata
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP from headers (handles proxies/load balancers)."""
        # Check X-Forwarded-For header first (set by proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, get the first (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Fallback to direct client host
        return request.client.host if request.client else "unknown"
