"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import init_db, close_db
from app.database.redis_client import get_redis, close_redis
from app.api.v1.router import api_router

# Setup logging
setup_logging()
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}. App will continue without database.")
    
    try:
        await get_redis()
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}. App will continue without Redis.")
    
    yield
    
    # Shutdown
    try:
        await close_redis()
    except:
        pass
    try:
        await close_db()
    except:
        pass

# Create FastAPI app
app = FastAPI(
    title="Unified AI Business Assistant API",
    description="Backend API for Unified AI Business Assistant - CNC Factory Operations Management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirects to API documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
    }

# Include API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )

