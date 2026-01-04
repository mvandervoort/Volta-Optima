#!/usr/bin/env python
"""
Eenvoudige starter voor Reflex op Railway deployment.
Dit script handelt de port configuratie af en start Reflex in productiemodus.
"""

import os
import sys
import logging
import subprocess

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("reflex-railway")

def main():
    """Start de Reflex applicatie in productie modus met de juiste port configuratie."""
    try:
        # Haal PORT uit omgevingsvariabele (Railway zet dit automatisch)
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Startend op poort: {port}")
        
        # Zet SSR-gerelateerde variabelen
        os.environ["REFLEX_DISABLE_SSR"] = "1"
        os.environ["VITE_DISABLE_SSR"] = "1"
        # Development mode om SSR build problemen te omzeilen
        os.environ["REFLEX_ENV"] = "dev"
        
        # Maak een flag bestand om SSR uit te schakelen (indien directory bestaat)
        flag_path = "/app/.web/node_modules/.no-ssr"
        if os.path.exists("/app/.web/node_modules"):
            with open(flag_path, "w") as f:
                f.write("SSR disabled by start.py")
        else:
            logger.warning(f"Directory /app/.web/node_modules bestaat niet (nog), flag bestand niet aangemaakt")
        
        # Log belangrijke opties
        logger.info("Reflex configuratie:")
        logger.info(f"- REFLEX_ENV: {os.environ.get('REFLEX_ENV')}")
        logger.info(f"- SSR uitgeschakeld: {os.environ.get('REFLEX_DISABLE_SSR')}")
        logger.info(f"- No-SSR flag bestand: {flag_path}")
        logger.info(f"- Werkdirectory: {os.getcwd()}")
        
        # Zet ports in environment voor Reflex
        os.environ["REFLEX_BACKEND_PORT"] = str(port)
        os.environ["REFLEX_FRONTEND_PORT"] = str(port)
        os.environ["REFLEX_BACKEND_HOST"] = "0.0.0.0"

        # Start de Reflex app in development mode met eenvoudiger command
        # Dit voorkomt de "list index out of range" error
        cmd = ["reflex", "run", "--backend-host", "0.0.0.0"]
        
        logger.info(f"Opdracht uitvoeren: {' '.join(cmd)}")
        logger.warning("App draait in development mode - dit is een tijdelijke workaround voor Reflex SSR bug")
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"Fout bij starten app: {e}")
        raise

if __name__ == "__main__":
    main()