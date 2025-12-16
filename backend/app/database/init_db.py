"""
Initialize database tables
"""
from app.database.connection import Base, engine
from app.database.models import *  # noqa: F401, F403
from app.core.logging import logger

def init_database():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    init_database()




