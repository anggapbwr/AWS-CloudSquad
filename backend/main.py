"""
AWS CloudSquad — Backend Entry Point
Autonomous DevOps & Cloud Engineering Platform Control Plane
"""
from contextlib import asynccontextmanager
from datetime import datetime
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config import settings
from database.session import init_db
from services.event_bus import event_bus
from api.missions import router as missions_router
from api.events import router as events_router
from api.artifacts import router as artifacts_router
from api.ws import router as ws_router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up AWS CloudSquad Control Plane...")
    try:
        await init_db()
        log.info("PostgreSQL database tables initialized.")
    except Exception as e:
        log.warning("Database initialization skipped or deferred", error=str(e))

    await event_bus.connect()
    yield
    log.info("Shutting down AWS CloudSquad Control Plane...")
    await event_bus.disconnect()


app = FastAPI(
    title="AWS CloudSquad API",
    description="Autonomous DevOps & Cloud Engineering Control Plane",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(missions_router, prefix="/api/missions", tags=["missions"])
app.include_router(events_router, prefix="/api/events", tags=["events"])
app.include_router(artifacts_router, prefix="/api/artifacts", tags=["artifacts"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    return {
        "name": "AWS CloudSquad",
        "positioning": "Autonomous DevOps & Cloud Engineering Platform",
        "tagline": "From Requirement to Running Infrastructure.",
        "version": "2.0.0",
        "status": "operational",
        "mode": settings.DEPLOYMENT_MODE,
        "demo_mode": settings.DEMO_MODE,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "cloudsquad-core",
        "deployment_mode": settings.DEPLOYMENT_MODE,
        "timestamp": datetime.utcnow().isoformat(),
    }
