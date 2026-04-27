"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import logger
from app.routers import api, web

# Validate configuration
settings.validate()
logger.info("Application starting...")

# Create FastAPI app
app = FastAPI(title="Mini GitHub LAN", version="1.0.0")

# Include routers
app.include_router(api.router, prefix="/api")
app.include_router(web.router)

# Mount static files
static_path = settings.base_dir / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

logger.info(f"App initialized - {settings.host}:{settings.port}")


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    from app.utils.path_security import ensure_temp_local_dir

    ensure_temp_local_dir()
    logger.info("Application startup complete")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
