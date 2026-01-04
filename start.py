#!/usr/bin/env python
"""
Railway deployment entry point for the Volta-Optima Reflex App.
Uses uvicorn directly to avoid SSR build issues in reflex run/export.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("volta-optima-railway")

def main():
    """Start the Reflex backend"""
    try:
        # Get port from Railway environment
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting on port: {port}")
        
        # Set environment variables
        os.environ["REFLEX_ENV"] = "production"
        os.environ["REFLEX_DISABLE_SSR"] = "1"
        os.environ["VITE_DISABLE_SSR"] = "1"
        
        logger.info("Environment configured:")
        logger.info(f"- REFLEX_ENV: {os.environ.get('REFLEX_ENV')}")
        logger.info(f"- SSR Disabled: {os.environ.get('REFLEX_DISABLE_SSR')}")
        
        # Import uvicorn and the app
        logger.info("Importing uvicorn and Reflex app...")
        import uvicorn
        from app.app import app as reflex_app
        
        logger.info("Starting Reflex backend via uvicorn...")
        logger.info("Note: This avoids SSR build issues by serving backend only via uvicorn")
        
        # Start uvicorn with the Reflex app object
        # The Reflex app serves its own frontend from .web directory
        uvicorn.run(
            reflex_app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Error starting app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
