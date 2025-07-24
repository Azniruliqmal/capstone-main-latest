#!/usr/bin/env python3
"""
Database migration script to create the User table
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import create_tables
from database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run database migration"""
    try:
        logger.info("Starting database migration...")
        
        # Create all tables
        create_tables()
        
        logger.info("Database migration completed successfully!")
        logger.info("Created tables: User, AnalyzedScript")
        
    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
