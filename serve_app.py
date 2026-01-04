#!/usr/bin/env python
"""
Railway deployment wrapper that serves both backend and frontend.
This script starts uvicorn for the backend and serves frontend static files.
"""

import os
import sys
import logging
import subprocess
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("volta-optima-server")

def serve_frontend():
    """Serve frontend via Node.js in a separate thread"""
    time.sleep(5)  # Wait for backend to start
    try:
        logger.info("Starting frontend server...")
        # Check if .web directory exists
        if os.path.exists("/app/.web"):
            os.chdir("/app/.web")
            # Serve the built frontend
            subprocess.run(["npx", "serve", "-s", ".", "-l", "3000"])
        else:
            logger.warning("No .web directory found, frontend not available")
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")

def main():
    """Start both backend and frontend simultaneously"""
    try:
        # Get port from Railway
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting Volta-Optima on port: {port}")
        
        # Set environment
        os.environ["REFLEX_ENV"] = "production"
        os.environ["REFLEX_DISABLE_SSR"] = "1"
        
        logger.info("Environment: production")
        logger.info("SSR: disabled")
        
        # Start frontend server in background thread
        frontend_thread = threading.Thread(target=serve_frontend, daemon=True)
        frontend_thread.start()
        
        # Import and start backend via uvicorn
        logger.info("Starting Reflex backend via uvicorn...")
        import uvicorn
        from app.app import app as reflex_app
        
        # Start uvicorn on the Railway port
        uvicorn.run(
            reflex_app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
