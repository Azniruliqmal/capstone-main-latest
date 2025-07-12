#!/usr/bin/env python3
"""
Database initialization script for Script Analysis API
This script creates all necessary database tables and performs initial setup.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.database import init_database, check_database_connection
from database.models import Base, User, Project, AnalyzedScript

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main initialization function"""
    try:
        logger.info("Starting database initialization...")
        
        # Check database connection first
        if not check_database_connection():
            logger.error("Cannot connect to database")
            return False
        
        # Initialize database (creates tables)
        init_database()
        
        logger.info("✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
