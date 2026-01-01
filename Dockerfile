FROM python:3.11-slim

# Installeer Node.js (Reflex heeft dit nodig)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer je code
COPY . .

# Installeer dependencies
RUN pip install --no-cache-dir reflex
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

# Initialiseer Reflex
RUN reflex init

EXPOSE 3000 8000

# Start Reflex
CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]
