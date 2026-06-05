import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.redis_client import close_redis
from app.api.routes import triage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — Sentry initialized in Phase 5 when DSN is configured
    pass
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title="Medical Triage API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return full traceback in development — remove in production."""
    if settings.environment == "development":
        return JSONResponse(status_code=500, content={"detail": traceback.format_exc()})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
