# Production Dockerfile for Volta-Optima Reflex app on Railway
# Updated: 2026-01-04 19:36 - NODE_OPTIONS BEFORE reflex init + subprocess in start.py
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Additional system dependencies for WeasyPrint, Playwright, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway configuration
ENV PORT=8000
EXPOSE 8000
ENV HOST=0.0.0.0

# Set production environment
ENV REFLEX_ENV=prod

# Set environment variables to disable SSR during build
ENV REFLEX_DISABLE_SSR=1
ENV VITE_DISABLE_SSR=1
ENV NODE_ENV=production

# Use node-globals.js to polyfill browser APIs (set BEFORE init!)
ENV NODE_OPTIONS="--require=/app/node-globals.js"

# Initialize Reflex app WITH polyfills active
RUN reflex init

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Start via start.py
CMD ["python", "/app/start.py"]
