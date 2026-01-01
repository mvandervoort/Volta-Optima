# Gebruik Python als basis
FROM python:3.11-slim

# Installeer Node.js en Curl (nodig voor de Reflex frontend)
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer requirements en installeer ze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de bestanden
COPY . .

# INITIALISATIE FIX:
# We gebruiken --template blank om vragen te voorkomen en zorgen dat 
# het in een niet-interactieve shell draait.
RUN reflex init --template blank

# Bouw de frontend
RUN reflex export --frontend-only --no-zip

# Start de app
CMD ["reflex", "run", "--env", "prod"]
