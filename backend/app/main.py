from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import ErrorHandlerMiddleware, RateLimitMiddleware, SecureHeadersMiddleware
from app.api.v1.api import router as api_v1_router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_db import seed_database

BASE_DIR = Path(__file__).resolve().parent.parent

configure_logging()

app = FastAPI(
    title="College ERP API",
    version="1.0.0",
    description="Production-ready Backend API for the College ERP system.",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Start up DB events
@app.on_event("startup")
def startup_event():
    # Only create tables directly in dev. In prod, we use alembic migrations.
    # Base.metadata.create_all(bind=engine)
    pass

# Middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)
app.add_middleware(SecureHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "version": "1.0.0"}


# Mount v1 REST API
app.include_router(api_v1_router, prefix="/api/v1")

