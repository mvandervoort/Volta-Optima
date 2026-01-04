FROM python:3.11-slim

# 1. Update en installeer Node.js uit Debian repo en systeempakketten
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm \
    # Grafische rendering dependencies (weasyprint/reportlab)
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    # Playwright/Browser dependencies
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    # Compilatie dependencies en tools
    build-essential libffi-dev shared-mime-info git vim nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer requirements eerst, voor betere layer caching
COPY requirements.txt .

# Installeer dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir reflex

# Bij ontwikkelomgeving wordt de code gemount via volume
# We kopiëren dus niet de code in de image

# Initialiseer Reflex
RUN reflex init

# Exposing Reflex ports
EXPOSE 3000 8000

# Standaard kommando (overridable via docker-compose)
CMD ["reflex", "run", "--env", "dev", "--loglevel", "debug"]
