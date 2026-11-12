# Restore

## Automatische back-up

`scripts/backup.ts` maakt een consistente snapshot van de SQLite-database met
`VACUUM INTO`. De service hoeft daarvoor niet gestopt te worden; WAL wordt
meegenomen in de snapshot.

```bash
FLOWHUB_DATA_DIR=/data bun scripts/backup.ts
```

In Docker (het script zit in de image):

```bash
docker compose exec -e FLOWHUB_BACKUP_DIR=/data/backups -e FLOWHUB_BACKUP_RETENTION=14 \
  app bun scripts/backup.ts
```

Omgevingsvariabelen:

| Variabele | Default | Betekenis |
| --- | --- | --- |
| `FLOWHUB_DB` | `$FLOWHUB_DATA_DIR/flowhub.db` | Bron-database |
| `FLOWHUB_DATA_DIR` | `./data` | Datamap |
| `FLOWHUB_BACKUP_DIR` | `./backups` | Doelmap |
| `FLOWHUB_BACKUP_RETENTION` | `14` | Aantal snapshots dat bewaard blijft |

In productie draai je dit dagelijks via cron of een systemd-timer, bijvoorbeeld:

```cron
15 2 * * * cd /opt/flowhub && /usr/local/bin/bun scripts/backup.ts >> /var/log/flowhub-backup.log 2>&1
```

## Restore

1. Stop de service: `docker compose stop app` (of `systemctl stop flowhub`).
2. Controleer welke snapshot je wilt terugzetten:
   `ls -la backups/`
3. Zet de snapshot terug:

   ```bash
   cp backups/flowhub-<stamp>.db data/flowhub.db
   rm -f data/flowhub.db-wal data/flowhub.db-shm
   ```

4. Start de service: `docker compose start app` (of `systemctl start flowhub`).
5. Controleer `/api/v1/health` en log in. Controleer daarna of de verwachte
   devices en de laatste auditregels aanwezig zijn.

## Verificatie

Na een restore test je expliciet:

- inloggen met een bestaande admin;
- één device uitlezen;
- de audit-tabel openen en de laatste entries controleren.

## Bewaarbeleid

Bewaar dagelijks 14 snapshots en houd daarnaast één snapshot per maand vóór
elke wijziging aan de busconfiguratie. Bewaar de snapshots buiten de Docker-
host, op een locatie die niet door de app zelf wordt opgeruimd.