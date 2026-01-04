#!/usr/bin/env python
"""
Railway deployment entry point for the Volta-Optima App.
This script handles proper port configuration and provides detailed logging
for troubleshooting Railway deployment issues.
"""

import os
import sys
import logging
import traceback

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
    logger.info(f"Reflex imported successfully, version: {rx.__version__ if hasattr(rx, '__version__') else 'Unknown'}")
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
    traceback.print_exc()
    sys.exit(1)

def main():
    """Main function to start the Reflex app on Railway."""
    try:
        # Get port from Railway environment
        port = int(os.environ.get("PORT", 3000))
        logger.info(f"Using PORT: {port}")
        
        # Print useful environment variables
        env_vars = [
            "REFLEX_ENV", "PYTHON_VERSION", "NODE_VERSION", 
            "DIRECTUS_URL", "QUESTDB_URL", "SUPABASE_URL"  # Add app-specific variables
        ]
        for var in env_vars:
            # Don't log the actual values of sensitive variables, just their presence
            if any(sensitive in var.lower() for sensitive in ["key", "token", "password", "secret"]):
                logger.info(f"{var}: {'Set' if os.environ.get(var) else 'Not set'}")
            else:
                logger.info(f"{var}: {os.environ.get(var, 'Not set')}")

        # Configure environment
        os.environ["REFLEX_ENV"] = "prod"
        
        logger.info("Starting Volta-Optima Reflex app...")
        
        # Try multiple approaches for compatibility with different Reflex versions
        try:
            # Approach 1: Use rx.App.start if available (older Reflex versions)
            logger.info(f"Starting Reflex app with backend_port={port}")
            rx.App.start(
                app,
                backend_port=port,
                frontend_port=port,  # Set both to same port for Railway
                loglevel="info",
                env="prod"
            )
        except (TypeError, AttributeError) as e:
            # Approach 2: Try the Reflex CLI approach
            logger.info(f"First approach failed: {e}, trying CLI approach")
            # Directly use the environment variables that Reflex will read
            os.environ["REFLEX_BACKEND_PORT"] = str(port)
            os.environ["REFLEX_FRONTEND_PORT"] = str(port)
            
            import subprocess
            logger.info(f"Running: reflex run --env prod --backend-port {port} --frontend-port {port}")
            subprocess.run(["reflex", "run", "--env", "prod", "--backend-port", str(port), "--frontend-port", str(port)])
    except Exception as e:
        logger.error(f"Error starting app: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()