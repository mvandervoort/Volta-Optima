# Runbook

Operationeel draaiboek voor de FlowHub-service op de Linux industrial PC.

## Dagelijks

- Controleer `GET /api/v1/health` → `status: online`, `converter: online`,
  `devices.online` gelijk aan het aantal enabled devices.
- Bij `degraded`: zie "Storingen" hieronder.

## Storingen

### Converter offline

1. `nc -vz <converter-ip> <poort>`.
2. Controleer voeding en netwerk van de converter.
3. Controleer of een andere applicatie de bus als master gebruikt.
4. FlowHub verbindt automatisch opnieuw met backoff; herstarten is zelden nodig.

### Eén device offline, rest online

- Device uit of verkeerd adres/dipswitch.
- Dubbel adres op de bus: twee devices met hetzelfde polling-adres.
- Bekijk de audit en `/api/v1/devices` voor `status` en `lastSeen`.

### Alle devices offline, converter online

- Baudrate of parity klopt niet met de 5850S-instelling.
- Converter staat niet in transparante modus.
- Kabel/terminatie op de RS-485-bus.

### Setpoint schrijven mislukt

- Controleer of de setpoint-source op `digitaal` staat; bij `analog` kan een
  externe ingang de digitale waarde overrulen.
- Controleer of de engineering-unit overeenkomt met het device.
- De fout wordt met oude en nieuwe waarde geaudit.

### Write-protect

- #128 wordt niet ondersteund door de 5850S. De UI toont "niet ondersteund".
  Dit is geen storing.

## Onderhoud

- Back-up: dagelijks via cron, zie `docs/restore.md`.
- Logs: JSON op stdout, opgeruimd door de containerlog-driver.
- Updates: nieuwe image bouwen, `docker compose up -d`, vorige tag bewaren
  voor rollback.
- Sessies verlopen na 12 uur; gebruikers loggen opnieuw in.

## Rollback

1. `docker compose down`
2. Vorige image-tag terugzetten in `docker-compose.yml`.
3. `docker compose up -d`
4. Database-migraties zijn backward-compatible; bij twijfel de laatste back-up
   terugzetten volgens `docs/restore.md`.

## Rechten

| Actie | Operator | Admin |
| --- | --- | --- |
| Devices bekijken | ja | ja |
| Setpoint schrijven | ja (met bevestiging) | ja |
| Klep-override | ja (met bevestiging) | ja |
| Apparaatconfiguratie | nee | ja |
| Gebruikersbeheer | nee | ja |
| Auditlog / export | nee | ja |

Elke schrijfactie wordt geaudit met gebruiker, tijd, oud/nieuw en resultaat.