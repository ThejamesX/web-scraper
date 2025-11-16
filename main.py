"""Main FastAPI application for PriceScout API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router)
app.include_router(track_router)

# Mount static files
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - serves the frontend UI.
    
    Returns:
        FileResponse: Frontend HTML page
    """
    frontend_file = Path(__file__).parent / "frontend" / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    
    return {
        "message": "Welcome to PriceScout API",
        "version": settings.api_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "ui_url": "/static/index.html"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
