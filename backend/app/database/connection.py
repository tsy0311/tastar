"""
Database Connection and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Import logger - will be initialized by main.py
try:
    from app.core.logging import logger
except ImportError:
    # Fallback if logging not initialized
    import logging
    logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

async def init_db():
    """Initialize database connection"""
    try:
        # Test connection (async wrapper for sync operation)
        from sqlalchemy import text
        import asyncio
        import concurrent.futures
        
        def test_connection():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        
        # Run sync operation in thread pool
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, test_connection)
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Don't raise in development - allow app to start without DB
        from app.core.config import settings
        if settings.DEBUG:
            logger.warning("Continuing without database connection (DEBUG mode)")
        else:
            raise

async def close_db():
    """Close database connection"""
    engine.dispose()
    logger.info("Database connection closed")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

