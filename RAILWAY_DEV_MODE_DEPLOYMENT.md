# Railway Deployment in Development Mode

## Waarom Development Mode?

Door een bug in Reflex's build systeem faalt de production build met "document is not defined" errors tijdens SSR pre-rendering. Ondanks alle officiële methodes om SSR uit te schakelen (via reflex.json en environment variables), blijft dit probleem bestaan.

**Oplossing**: De app draaien in development mode op Railway. Dit omzeilt het SSR build probleem.

## Trade-offs

### Nadelen:
-  Langzamere initiële load times (geen geoptimaliseerde production build)
- Frontend assets worden niet geminificeerd
- Meer uitgebreid logging
- Niet de aanbevolen aanpak voor high-traffic productie

### Voordelen:
✅ De app werkt en kan deployen zonder fouten
✅ Hot reloading tijdens development (als nodig)
✅ Eenvoudiger debuggen door uitgebreide logs
✅ Tijdelijke oplossing totdat Reflex's SSR bug is gefixt

## Deployment Configuratie

### Dockerfile
```dockerfile
# Development mode om SSR build problemen te omzeilen
ENV REFLEX_ENV=dev
ENV REFLEX_DISABLE_SSR=1
ENV VITE_DISABLE_SSR=1

# Reflex init in development mode
RUN reflex init
```

### start.py
```python
os.environ["REFLEX_ENV"] = "dev"
cmd = ["reflex", "run", "--env", "dev", ...]
```

## Volgende Stappen

1. **Korte termijn**: Deze development mode deployment gebruiken
2. **Monitoring**: Observeren of prestaties acceptabel zijn voor jouw use case
3. **Escalatie**: Bug report indienen bij het Reflex team (zie `REFLEX_SSR_BUG_REPORT.md`)
4. **Lange termijn**: Migreren naar production mode zodra Reflex de SSR bug heeft gefixt

## Performance Optimalisatie Tips

Hoewel in development mode, kan je nog steeds optimaliseren:
- Railway instellen op een grotere instance voor betere performance
- CDN gebruiken voor statische assets
- Caching implementeren op database/API niveau
- Database queries optimaliseren

## Terug naar Production Mode

Wanneer Reflex de SSR bug heeft gefixt:
1. Update Reflex naar de nieuwste versie
2. Wijzig `ENV REFLEX_ENV=dev` naar `ENV REFLEX_ENV=prod` in Dockerfile
3. Wijzig `--env dev` naar `--env prod` in start.py
4. Test in staging omgeving eerst
5. Deploy naar production

## Support

Voor vragen of problemen:
- Raadpleeg de `REFLEX_SSR_BUG_REPORT.md` voor technische details
- Check Reflex GitHub issues voor updates over de SSR bug
- Contact het Reflex team via hun Discord kanaal