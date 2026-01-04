# Railway Deployment Checklist voor Volta-Optima

## Voor deployment:

### 1. Docker Cache Leegmaken (BELANGRIJK!)
Railway gebruikt Docker cache. Om er zeker van te zijn dat de nieuwe configuratie wordt gebruikt:

**Aanbevolen Aanpak: Force Rebuild**
1. Commit en push je wijzigingen naar je repository
2. In Railway Dashboard: Ga naar je service
3. Klik in de deployment sectie op de 3 dots (⋮) bij de laatste deployment
4. Kies "Redeploy" of "Remove" gevolgd door een nieuwe deployment
5. Railway bouwt alles opnieuw vanaf scratch

**Alternatief: Dockerfile wijziging forceren**
Als Railway toch cache gebruikt, voeg een dummy comment toe in Dockerfile:
```dockerfile
# Updated: 2026-01-04 [huidige tijd]
```
Commit en push - Railway detecteert de wijziging en herbouwt alles.

### 2. Benodigde Environment Variables in Railway
Zorg dat deze variabelen zijn ingesteld:

#### Verplicht:
- `PORT` - (Automatisch ingesteld door Railway)
- `REFLEX_ENV` - Zet op `production`

#### App-specifiek (kopieer uit je .env):
- `DIRECTUS_API_KEY`
- `DIRECTUS_URL`
- `GITHUB_TOKEN`
- `GOOGLE_ANALYTICS_ID`
- `GOOGLE_API_KEY`
- `QUESTDB_PASSWORD`
- `QUESTDB_URL`
- `QUESTDB_USERNAME`
- `RESEND_API_KEY`
- `SUPABASE_KEY`
- `SUPABASE_URL`
- `ADVICE_LIMIT_LOGGED_IN_MULTIPLIER`
- `ADVICE_LIMIT_PER_DAY`
- `ADVICE_LIMIT_TOTAL`

### 3. Deployment Stappen
1. ✅ Commit alle wijzigingen aan Dockerfile en start.py
2. ✅ Push naar je repository
3. ✅ Clear Railway cache (zie optie A hierboven)
4. ✅  Railway detecteert automatisch wijzigtje en start deployment
5. ⏳ Wacht op "reflex export --frontend-only --no-zip" stap (kan 1-2 minuten duren)
6. ⏳ Wacht op volledige deployment
7. ✅ Test de deployment door naar je Railway URL te gaan

### 4. Verwachte Log Output
Je zou dit moeten zien in de Railway logs:

```
Building...
RUN reflex init
✓ Reflex initialized successfully
RUN reflex export --frontend-only --no-zip
✓ Frontend exported successfully
Starting...
Starting Reflex app in production mode...
Reflex app running on http://0.0.0.0:XXXX
```

### 5. Troubleshooting

**Als "document is not defined" error nog steeds optreedt:**
- Controleer of `reflex export --frontend-only --no-zip` succesvol was
- Clear Railway cache en redeploy
- Check of REFLEX_ENV=production is ingesteld

**Als "list index out of range" error optreedt:**
- Dit zou NIET meer moeten gebeuren dankzij `reflex export`
- Als het toch gebeurt, check of start.py wordt gebruikt (zou niet moeten)

**Als de app start maar 404 geeft:**
- Check of de frontend export succesvol was
- Bekijk logs voor "Frontend exported successfully"
- Frontend assets moeten in /.web/_static staan

### 6. Snelheid
De eerste deployment na het clearen van de cache zal langer duren (5-10 minuten) omdat alles opnieuw wordt gebouwd. Latere deployments gebruiken de cache en zijn sneller (2-3 minuten).

## Belangrijkste Verschil met Vorige Aanpak
❌ OUD: Development mode, uvicorn direct, SSR problemen
✅ NIEUW: Production mode, `reflex export --frontend-only`, geen SSR problemen