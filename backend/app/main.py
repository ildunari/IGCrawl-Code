from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .database import init_db
from .api import accounts, scrapes, export, health, settings as settings_api
from .workers.scheduler import start_scheduler
from .utils.rate_limiter import SlidingWindowRateLimiter, RateLimitMiddleware
from .utils.dirs import ensure_directories

settings = get_settings()
rate_limiter = SlidingWindowRateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    ensure_directories()  # Create required directories first
    init_db()
    start_scheduler()
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan
)

# IMPORTANT: Add CORS middleware FIRST (executes last) - before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add expose_headers to ensure all headers are exposed
)

# Rate limiting middleware must be added AFTER CORS
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(accounts.router, prefix=f"{settings.api_v1_prefix}/accounts", tags=["accounts"])
app.include_router(scrapes.router, prefix=f"{settings.api_v1_prefix}/scrapes", tags=["scrapes"])
app.include_router(export.router, prefix=f"{settings.api_v1_prefix}/export", tags=["export"])
app.include_router(settings_api.router, prefix=f"{settings.api_v1_prefix}/settings", tags=["settings"])


@app.get("/")
async def root():
    return {"message": "Instagram Intelligence Dashboard API", "version": "2.0.0"}