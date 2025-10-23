"""
Enhanced chat router with monitoring integration.
Tracks detailed metrics for each chat request including security validation results.
"""

# Add monitoring tracking to the existing chat endpoint
from app.monitoring import get_monitoring_service

# This can be imported and used in the chat router to add detailed tracking
def track_chat_metrics(
    request_id: str,
    user_language: str,
    security_blocked: bool,
    risk_level: str,
    retrieved_nodes_count: int,
    trace_id: str = None
):
    """
    Track detailed chat-specific metrics.
    Call this from chat.py to add chat-specific metadata.
    """
    monitoring_service = get_monitoring_service()
    
    # This will be combined with the middleware metrics
    # The middleware already tracks basic request metrics
    # This adds chat-specific details
    metadata = {
        "user_language": user_language,
        "security_blocked": security_blocked,
        "risk_level": risk_level,
        "retrieved_nodes_count": retrieved_nodes_count,
        "has_trace_id": trace_id is not None,
    }
    
    return metadata
