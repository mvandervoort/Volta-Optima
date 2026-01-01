FROM python:3.11-slim

# Voorkom interactieve vragen tijdens installatie
ENV DEBIAN_FRONTEND=noninteractive

# Installeer systeem dependencies voor Node.js, WeasyPrint en Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer je code
COPY . .

# Installeer dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir reflex
RUN pip install --no-cache-dir -r requirements.txt

# Installeer Playwright browsers
RUN playwright install chromium --with-deps

# Initialiseer Reflex
RUN reflex init

EXPOSE 3000 8000

# Start Reflex
CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]
