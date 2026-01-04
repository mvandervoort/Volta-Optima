FROM python:3.11-slim

# Installeer systeemafhankelijkheden
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    build-essential \
    gnupg \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installeer Node.js 20
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Voor WeasyPrint en HTML2Image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Voor Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Kopieer bestanden en installeer Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de applicatiecode
COPY . .

# Kopieer de Reflex configuratie expliciet
COPY reflex.json .

# Maak assets directory en CSS bestand aan
RUN mkdir -p /app/assets/styles && \
    touch /app/assets/styles/global.css

# Railway configuratie
ENV PORT=8000
EXPOSE 8000
ENV HOST=0.0.0.0

# Development mode om SSR build problemen te omzeilen
# Dit is een tijdelijke workaround totdat Reflex's SSR bug is gefixt
ENV REFLEX_ENV=dev
ENV REFLEX_DISABLE_SSR=1
ENV VITE_DISABLE_SSR=1

# Reflex init in development mode (geen production build, omzeilt SSR probleem)
RUN reflex init

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ping || exit 1

# Start command - direct via reflex CLI met minimale configuratie
# Gebruik reflex deployment mode die werkt zonder SSR
CMD ["reflex", "run", "--loglevel", "info"]
