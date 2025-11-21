"""
Database connection management for Demo Copilot
Handles PostgreSQL connections via SQLAlchemy
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

from .models import Base

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_U3cV2pwZqOGA@ep-bitter-math-ahpxc9am-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Create engine
# For serverless (Neon), use NullPool to avoid connection pooling issues
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Recommended for serverless
    echo=False,  # Set to True for SQL query logging
    future=True,
    connect_args={
        "connect_timeout": 10,
        "application_name": "demo_copilot"
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions
    Use with FastAPI Depends()

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a new database session
    Must be closed manually

    Usage:
        db = get_db_session()
        try:
            # do something
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    return SessionLocal()


def check_db_connection() -> bool:
    """
    Check if database connection is working
    Returns True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def close_db_connection():
    """
    Close all database connections
    Call this on application shutdown
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Test connection on module import (optional)
if __name__ == "__main__":
    print("Testing database connection...")
    if check_db_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
