# Railway Deployment Guide voor Volta-Optima

Dit document beschrijft het proces voor het deployen van de Volta-Optima Reflex applicatie naar Railway.

## Vereisten

- Een Railway account
- Git repository met de codebase
- Railway CLI (optioneel, voor lokale tests)

## Deployment Stappen

### 1. Voorbereiden van je Repository

Zorg ervoor dat je repository de volgende bestanden bevat:
- `Dockerfile.railway` (hernoem naar `Dockerfile` voor Railway)
- `railway_start.py` (Python startscript voor robuuste Railway deployment)
- `fix_ssr.js` (Oplossing voor "document is not defined" fouten in SSR)
- `.env` (gebruik deze NIET in je repository, maar configureer de variabelen in Railway)

### 2. Project Aanmaken in Railway

1. Log in op [Railway Dashboard](https://railway.app/dashboard)
2. Klik op "New Project"
3. Selecteer "Deploy from GitHub repo"
4. Selecteer je repository
5. Railway detecteert automatisch de `Dockerfile`

### 3. Omgevingsvariabelen Configureren

Je moet dezelfde omgevingsvariabelen configureren als in je lokale `.env` bestand:

| Variabele | Beschrijving | Verplicht |
|-----------|-------------|-----------|
| `ADVICE_LIMIT_LOGGED_IN_MULTIPLIER` | Multiplier voor ingelogde gebruikers | Ja |
| `ADVICE_LIMIT_PER_DAY` | Limiet per dag | Ja |
| `ADVICE_LIMIT_TOTAL` | Totaal limiet | Ja |
| `DIRECTUS_API_KEY` | API key voor Directus CMS | Ja |
| `DIRECTUS_URL` | URL voor Directus CMS | Ja |
| `GITHUB_TOKEN` | GitHub toegangs token | Ja |
| `GOOGLE_ANALYTICS_ID` | Google Analytics ID | Ja |
| `GOOGLE_API_KEY` | Google API Key | Ja |
| `QUESTDB_PASSWORD` | QuestDB wachtwoord | Ja |
| `QUESTDB_URL` | QuestDB URL | Ja |
| `QUESTDB_USERNAME` | QuestDB gebruikersnaam | Ja |
| `RESEND_API_KEY` | Resend API key | Ja |
| `SUPABASE_KEY` | Supabase key | Ja |
| `SUPABASE_URL` | Supabase URL | Ja |
| `PORT` | **Automatisch toegevoegd door Railway** | Automatisch |
| `REFLEX_ENV` | **Automatisch ingesteld op 'prod'** | Automatisch |

Configureer deze variabelen in de Railway dashboard onder de "Variables" tab van je project.

### 4. Deployment Setup

Railway heeft geen speciale configuratie nodig buiten de `Dockerfile` en omgevingsvariabelen. De standaard settings werken prima:

- **Root Directory**: / (standaard)
- **Dockerfile Path**: Dockerfile
- **Build Command**: Automatisch via Dockerfile
- **Start Command**: Automatisch via Dockerfile CMD

### 5. Poortconfiguratie

Railway wijst automatisch een poort toe via de `PORT` omgevingsvariabele. Het `start.sh` script detecteert deze poort en configureert Reflex om deze te gebruiken.

### 6. Monitoring en Logs

- Bekijk logs via de Railway dashboard
- De `HEALTHCHECK` in de Dockerfile helpt Railway om de gezondheid van je container te monitoren

### 7. CI/CD Setup

Railway integreert automatisch met GitHub:
- Pushes naar de main branch triggeren automatisch een nieuwe deployment
- Je kunt automatisering configureren voor preview deployments van PRs

### 8. Domein Configuratie

1. Ga naar "Settings" in je Railway project
2. Scroll naar "Domains"
3. Voeg een custom domein toe of gebruik het door Railway gegenereerde domein

## Troubleshooting

### Container start niet op
- Controleer de logs voor errors
- Verifieer dat alle omgevingsvariabelen correct zijn geconfigureerd
- Probeer een herstart van de service

### Frontend werkt, maar API calls falen
- Controleer of de backend port correct is geconfigureerd in `railway_start.py`
- Controleer of de Reflex app correct is geconfigureerd voor productie-gebruik
- Bekijk de logs in Railway voor specifieke Python exceptions

### "document is not defined" of andere browser API fouten
Deze fouten komen vaak voor bij Server-Side Rendering (SSR) in een Node.js omgeving:
- Controleer of `fix_ssr.js` correct is geïnstalleerd
- Controleer de patching in de Dockerfile om te zien of het script correct is geïnjecteerd
- Stel `REFLEX_DISABLE_SSR=1` in als omgevingsvariabele in Railway

## Best Practices

1. **Gebruik een aparte branch voor productie deployments**
2. **Test altijd lokaal voordat je pushed naar de productie branch**
3. **Gebruik geheimen voor gevoelige omgevingsvariabelen**
4. **Stel resource limieten in om onverwachte kosten te voorkomen**