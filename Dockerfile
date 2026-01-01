# Gebruik Python als basis
FROM python:3.11-slim

# Installeer de noodzakelijke systeem-pakketten (unzip is de ontbrekende schakel!)
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer requirements en installeer ze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de bestanden
COPY . .

# Initialiseer de app (dit zal nu wel lukken omdat unzip aanwezig is)
RUN reflex init --template blank

# Bouw de frontend
RUN reflex export --frontend-only --no-zip

# Start de app
CMD ["reflex", "run", "--env", "prod"]
