# flake8: noqa: E402
from dotenv import load_dotenv

from app.config import DATA_DIR

load_dotenv()

import gc
import logging
import os

import uvicorn
from app.api.routers.chat import chat_router
from app.api.routers.chat_config import config_router
from app.api.routers.upload import file_upload_router
from app.observability import init_observability
from app.settings import init_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

init_settings()
init_observability()

# Initialize monitoring
from app.middleware.monitoring_middleware import MonitoringMiddleware
from app.scheduler import get_monitoring_scheduler

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Start monitoring scheduler
monitoring_scheduler = get_monitoring_scheduler()

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set
logger = logging.getLogger("uvicorn")

if environment == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Redirect to documentation page when accessing base URL
    @app.get("/")
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")


def mount_static_files(directory, path):
    if os.path.exists(directory):
        logger.info(f"Mounting static files '{directory}' at '{path}'")
        app.mount(
            path,
            StaticFiles(directory=directory, check_dir=False),
            name=f"{directory}-static",
        )


# Mount the data files to serve the file viewer
mount_static_files(DATA_DIR, "/api/files/data")
# Mount the output files from tools
mount_static_files("output", "/api/files/output")

app.include_router(chat_router, prefix="/api/chat")
app.include_router(config_router, prefix="/api/chat/config")
app.include_router(file_upload_router, prefix="/api/chat/upload")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Configure garbage collection for memory-constrained environment (2GB instance)
    # More aggressive thresholds than default (700, 10, 10)
    gc.set_threshold(700, 10, 5)
    gc.enable()
    logger.info(f"Garbage collection configured with thresholds: {gc.get_threshold()}")

    logger.info("Starting monitoring scheduler...")
    monitoring_scheduler.start()
    
    # Run startup recovery to upload any unsaved reports from previous session
    logger.info("Running monitoring startup recovery...")
    await monitoring_scheduler.monitoring_service.startup_recovery()
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down monitoring scheduler...")
    await monitoring_scheduler.shutdown()
    
    # Close shared HTTP client
    from app.http_client import close_http_client
    await close_http_client()
    
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))
    reload = True if environment == "dev" else False

    uvicorn.run(app="main:app", host=app_host, port=app_port, reload=reload)
