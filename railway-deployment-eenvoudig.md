# Volta-Optima Railway Deployment (Vereenvoudigd)

Deze documentatie beschrijft de vereenvoudigde aanpak voor het deployen van de Volta-Optima Reflex app naar Railway.

## Overzicht

De vereenvoudigde deployment strategie:
1. Gebruikt standaard Reflex build opties
2. Schakelt SSR (Server-Side Rendering) volledig uit
3. Vereist minimale configuratie
4. Vermijdt complexe patches en scripts

## Vereiste Bestanden

Je hebt slechts 3 bestanden nodig:
- `Dockerfile`: Voor het bouwen van de container
- `start.py`: Een eenvoudig Python start script
- `.dockerignore`: Om build-tijd te versnellen

## SSR Uitschakelen

Server-Side Rendering is uitgeschakeld op 4 niveaus:
1. In `reflex.json` (deel van de repository)
2. Via omgevingsvariabelen in de Dockerfile
3. Met een flag bestand: `.no-ssr`
4. Door de Reflex app te starten met `--env prod --backend-only`

## Deployment Naar Railway

1. Zorg dat je repository de bovengenoemde bestanden bevat
2. Verbind je Railway project met je repository
3. Configureer de environment variables in Railway

## Environment Variables

Belangrijke variabelen om in Railway te configureren:
- `REFLEX_ENV`: Zet op `prod`
- `REFLEX_DISABLE_SSR`: Zet op `1`
- `VITE_DISABLE_SSR`: Zet op `1`
- Kopieer alle geheimen uit je `.env` bestand (API keys, etc.)

## Voordelen

1. **Eenvoudig**: Geen complexe scripts, patches of hacks
2. **Betrouwbaar**: Gebruikt standaard Reflex functies
3. **Onderhoudbaar**: Duidelijk wat er gebeurt, makkelijk aan te passen
4. **Efficiënt**: Snellere builds door onnodige files te negeren

## Probleemoplossing

### Build Faalt

- Controleer of je de laatste versie van Reflex gebruikt
- Verifieer of alle environment variables correct zijn geconfigureerd
- Check de build logs voor specifieke errors

### "document is not defined" Fouten

Deze aanpak voorkomt dit probleem door SSR volledig uit te schakelen. Als je toch deze fout ziet:
1. Controleer of REFLEX_DISABLE_SSR op 1 is gezet in Railway
2. Verify dat reflex.json correct is geconfigureerd
3. Check of `start.py` correct het .no-ssr flag bestand aanmaakt

### Memory Problemen

Als je memory errors ziet tijdens build:
- Schakel naar een grotere instance in Railway
- Kies Railway's L of XL CPU/memory plan voor grotere projecten