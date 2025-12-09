"""
Logging Configuration
"""
import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    """Setup application logging"""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Ensure logs directory exists
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="7 days",
        enqueue=True,  # Use queue for thread safety
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/combined.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        enqueue=True,  # Use queue for thread safety
    )
    
    return logger

