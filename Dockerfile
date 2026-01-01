# Gebruik een officiële Python image
FROM python:3.11-slim

# Zet de werkmap in de container
WORKDIR /app

# Kopieer je requirements en installeer ze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van je code
COPY . .

# Initialiseer Reflex en exporteer de frontend
# Dit bouwt de Next.js bestanden die nodig zijn voor de browser
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Stel de poort in (Reflex gebruikt standaard 8000 voor de backend)
EXPOSE 8000
EXPOSE 3000

# Start de applicatie in productie-modus
CMD ["reflex", "run", "--env", "prod"]
