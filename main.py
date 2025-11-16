"""Main FastAPI application for PriceScout API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from db import init_db
from api.endpoints import search_router, track_router
from scheduler.jobs import check_all_product_prices

# Initialize scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up PriceScout API...")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Start background scheduler
    scheduler.add_job(
        check_all_product_prices,
        "interval",
        hours=settings.price_check_interval_hours,
        id="check_prices",
        replace_existing=True
    )
    scheduler.start()
    print(f"Scheduler started (checking prices every {settings.price_check_interval_hours} hours)")
    
    yield
    
    # Shutdown
    print("Shutting down PriceScout API...")
    scheduler.shutdown()
    print("Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Include routers
app.include_router(search_router)
app.include_router(track_router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API information
    """
    return {
        "message": "Welcome to PriceScout API",
        "version": settings.api_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
