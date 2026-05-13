import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from asta_brain.api.analytics import router as analytics_router
from asta_brain.api.monitoring import router as monitoring_router
from prometheus_client import make_asgi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Project Asta Trading Brain starting up...")
    yield
    # Shutdown logic
    logger.info("Project Asta Trading Brain shutting down...")

app = FastAPI(
    title="Project Asta Trading Brain",
    description="Central intelligence and orchestration for Project Asta",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(analytics_router)
app.include_router(monitoring_router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "asta-brain"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
