"""NIRMAANDRISHTI AI — FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analytics, dashboard, intelligence, predictions, projects, risks
from app.core.config import get_settings
from app.core.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("nirmaandrishti")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Database ready (%s)", settings.database_url.split("://")[0])
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered infrastructure project intelligence and early warning system.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "NIRMAANDRISHTI API is running"
    }


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(predictions.router)
app.include_router(intelligence.router)
app.include_router(analytics.router)
app.include_router(risks.router)



