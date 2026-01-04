#!/usr/bin/env python
"""
Railway deployment entry point for the Volta-Optima Reflex App.
Uses reflex run with Node.js polyfills to avoid SSR issues.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("volta-optima-railway")

def main():
    """Start the Reflex app via reflex run with polyfills active"""
    try:
        # Get port from Railway environment
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting on port: {port}")
        
        # Set environment variables
        os.environ["REFLEX_ENV"] = "production"
        os.environ["REFLEX_DISABLE_SSR"] = "1"
        os.environ["VITE_DISABLE_SSR"] = "1"
        os.environ["REFLEX_BACKEND_PORT"] = str(port)
        os.environ["REFLEX_FRONTEND_PORT"] = str(port)
        
        logger.info("Environment configured:")
        logger.info(f"- REFLEX_ENV: production")
        logger.info(f"- SSR Disabled: 1")
        logger.info(f"- NODE_OPTIONS: {os.environ.get('NODE_OPTIONS', 'Not set')}")
        logger.info(f"- Port: {port}")
        
        # Start reflex run
        # NODE_OPTIONS is already set in Dockerfile to load node-globals.js
        logger.info("Starting app via reflex run...")
        
        cmd = ["reflex", "run", "--loglevel", "info"]
        logger.info(f"Command: {' '.join(cmd)}")
        
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
