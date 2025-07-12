import os
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import time
from urllib.parse import quote_plus

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

# Connection pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Determine database URL based on configuration
if USE_SQLITE or not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    # Use SQLite for development/testing when PostgreSQL is not available
    logger.info("Using SQLite database for development")
    DATABASE_URL = "sqlite:///./script_analysis.db"
    
    # SQLite Engine with simpler configuration
    engine = create_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    # Use PostgreSQL for production
    logger.info("Using PostgreSQL database")
    # URL encode the password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Enhanced SQLAlchemy Engine with optimized connection pooling
    engine = create_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        poolclass=QueuePool,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
        pool_pre_ping=True,  # Validate connections before use
        connect_args={
            "connect_timeout": 10,
            "application_name": "script_analysis_api"
        }
)

# Connection event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection parameters on connect"""
    logger.debug("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout"""
    logger.debug("Connection checked out from pool")

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Enhanced dependency injection for database sessions
def get_db():
    """Enhanced database session with error handling"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Database health check utilities
def check_database_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def get_database_info() -> dict:
    """Get database connection information"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            pool = engine.pool
            return {
                "database_version": version,
                "pool_size": getattr(pool, 'size', lambda: 0)(),
                "checked_in": getattr(pool, 'checkedin', lambda: 0)(),
                "checked_out": getattr(pool, 'checkedout', lambda: 0)(),
                "overflow": getattr(pool, 'overflow', lambda: 0)(),
                "invalid": getattr(pool, 'invalid', lambda: 0)()
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {"error": str(e)}

# Function to create tables with error handling
def create_tables():
    """Create database tables with enhanced error handling"""
    try:
        # Import all models to ensure they're registered
        from database.models import User, Project, AnalyzedScript
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

# Database initialization and migration utilities
def init_database():
    """Initialize database with tables and basic setup"""
    try:
        # Check connection first
        if not check_database_connection():
            raise Exception("Cannot connect to database")
        
        # Create tables
        create_tables()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Connection pool monitoring
def get_pool_status() -> dict:
    """Get detailed connection pool status"""
    try:
        pool = engine.pool
        return {
            "pool_size": getattr(pool, 'size', lambda: 0)(),
            "checked_in_connections": getattr(pool, 'checkedin', lambda: 0)(),
            "checked_out_connections": getattr(pool, 'checkedout', lambda: 0)(),
            "overflow_connections": getattr(pool, 'overflow', lambda: 0)(),
            "invalid_connections": getattr(pool, 'invalid', lambda: 0)(),
            "total_connections": getattr(pool, 'size', lambda: 0)() + getattr(pool, 'overflow', lambda: 0)(),
            "available_connections": getattr(pool, 'checkedin', lambda: 0)()
        }
    except Exception as e:
        logger.error(f"Failed to get pool status: {str(e)}")
        return {"error": str(e)}