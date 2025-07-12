#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""

import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server():
    """Start the uvicorn server"""
    try:
        # Change to backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(backend_dir)
        
        logger.info("Starting FastAPI backend server...")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Start uvicorn server
        uvicorn.run(
            "api.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    start_server()

if __name__ == "__main__":
    print("Starting FastAPI server with chat endpoint...")
    try:
        uvicorn.run(
            "api.api:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
