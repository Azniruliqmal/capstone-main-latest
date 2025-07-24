#!/usr/bin/env python3
"""
Start the FastAPI server for the script analysis API
"""

import uvicorn
from api.api import app
from database.database import init_database
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_server():
    """Start the FastAPI server"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
        
        # Start the server
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    start_server()