"""
Gunicorn configuration for production deployment.
Implements Worker rotation to prevent memory leaks.
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('APP_PORT', '8000')}"

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", 2))  # 1-2 workers for 2GB instance
worker_class = "uvicorn.workers.UvicornWorker"

# Worker lifecycle - CRITICAL for memory leak mitigation
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 800))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 200))

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# Logging
accesslog = "-" if os.getenv("ENVIRONMENT") == "dev" else None  # Disable in production to save memory
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Process naming
proc_name = "pathway-chatbot-backend"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn master process starting")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"Gunicorn is ready. Workers: {workers}, Max requests: {max_requests}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Gunicorn master process exiting")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info(f"Worker {worker.pid} received INT/QUIT signal")

def worker_abort(worker):
    """Called when a worker is killed by timeout."""
    worker.log.warning(f"Worker {worker.pid} aborted (timeout)")
