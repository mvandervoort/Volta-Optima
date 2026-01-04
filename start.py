#!/usr/bin/env python
"""
Railway deployment entry point for the Volta-Optima Reflex App.
This script handles proper port configuration and provides detailed logging.
Based on the proven Energy App deployment approach.
"""

import os
import sys
import logging
import subprocess

# Configure logging first to capture all startup information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("volta_optima_railway_starter")

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

        # Configure environment for production
        os.environ["REFLEX_ENV"] = "production"
        
        logger.info("Starting Reflex app in production mode...")
        
        # Start the application with explicit port configuration
        # Note: Different versions of Reflex have different API for starting the app
        # Try the old API first
        try:
            logger.info(f"Starting Reflex app with backend_port={port}")
            rx.App.start(
                app,
                backend_port=port,
                frontend_port=port,  # Set both to same port for Railway
                loglevel="info",
                env="prod"
            )
        except (TypeError, AttributeError) as e:
            # If that fails, try the alternative approach
            logger.info(f"First approach failed: {e}, trying subprocess approach")
            # Directly use the environment variables that Reflex will read
            os.environ["REFLEX_BACKEND_PORT"] = str(port)
            os.environ["REFLEX_FRONTEND_PORT"] = str(port)
            # Use subprocess to run reflex
            subprocess.run(["reflex", "run", "--env", "prod", "--backend-port", str(port), "--frontend-port", str(port)])
    except Exception as e:
        logger.error(f"Error starting app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
