"""
Shared HTTP client with connection limits.
Implements Right-size pools & close clients properly.
"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global singleton client
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """
    Get or create the global HTTP client singleton.
    
    This ensures only one client exists with controlled connection pooling,
    preventing memory leaks from unbounded connections.
    """
    global _http_client
    
    if _http_client is None:
        # Configure limits
        limits = httpx.Limits(
            max_connections=100,        # Total connection pool size
            max_keepalive_connections=20  # Persistent connections
        )
        
        timeout = httpx.Timeout(
            connect=5.0,  # Connection timeout
            read=30.0,    # Read timeout
            write=10.0,   # Write timeout
            pool=5.0      # Pool acquisition timeout
        )
        
        _http_client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            follow_redirects=True
        )
        
        logger.info(
            f"HTTP client initialized: "
            f"max_connections={limits.max_connections}, "
            f"max_keepalive={limits.max_keepalive_connections}"
        )
    
    return _http_client


async def close_http_client():
    """
    Close the global HTTP client.
    Should be called on application shutdown.
    """
    global _http_client
    
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None
        logger.info("HTTP client closed")
