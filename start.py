#!/usr/bin/env python
"""
Railway deployment entry point for the Volta-Optima Reflex App.
Exact copy of proven Energy App approach.
"""

import os
import sys
import logging

# Configure logging first to capture all startup information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("railway_starter")

# Print environment information for debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")

try:
    import reflex as rx
    logger.info(f"Reflex imported successfully")
except ImportError as e:
    logger.error(f"Failed to import reflex: {e}")
    sys.exit(1)

try:
    # Import your app - adjust the import path if needed
    from app.app import app
    logger.info("Successfully imported Volta-Optima app")
except ImportError as e:
    logger.error(f"Failed to import Volta-Optima app: {e}")
    logger.error(f"sys.path: {sys.path}")
    sys.exit(1)

def main():
    """Main function to start the Reflex app on Railway."""
    try:
        # Get port from Railway environment
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Using PORT: {port}")
        
        # Print useful environment variables
        env_vars = ["REFLEX_ENV", "PYTHON_VERSION", "NODE_VERSION"]
        for var in env_vars:
            logger.info(f"{var}: {os.environ.get(var, 'Not set')}")

        # Configure environment
        os.environ["REFLEX_ENV"] = "production"
        
        logger.info("Starting Reflex app...")
        
        # Start via subprocess (rx.App.start doesn't exist in this version)
        # NODE_OPTIONS is set in Dockerfile to load polyfills
        logger.info(f"Starting reflex run with port={port}")
        logger.info(f"NODE_OPTIONS active: {os.environ.get('NODE_OPTIONS')}")
        
        # Use subprocess to run reflex
        import subprocess
        subprocess.run(["reflex", "run", "--env", "prod", "--loglevel", "info"])
    except Exception as e:
        logger.error(f"Error starting app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
