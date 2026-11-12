# Startgids — FlowHub van nul naar werkend

Deze gids is voor de technisch beheerder. Je hebt Docker-kennis nodig en je
kunt fysieke handelingen doen (converter, RS-485, clients). Elke fase eindigt
met een **controlepunt**: slaagt dat niet, ga dan niet verder.

Uitgangspunt: FlowHub staat in de submap `flowhub/` van de repository
`mvandervoort/Volta-Optima`.

---

## Fase 0 — Wat je nodig hebt

| Nodig | Details |
| --- | --- |
| Linux industrial PC | x64, Docker Engine + Compose v2, NTP actief |
| Converter | Waveshare RS232/485-to-Ethernet (SKU 16530) |
| Devices | Eén of meer Brooks 5850S op één RS-485-bus |
| Bus | Daisy-chain, 120 Ω terminatie aan beide uiteinden, bias één keer |
| Netwerk | Geïsoleerd VLAN, statisch IP voor IPC én converter |
| Clients | Edge of Chrome; geen legacy IE |
| Poorten | 443 (Caddy), 8080 (app, alleen intern), TCP naar converter (meestal 1111) |

Voor development zonder Docker: Bun 1.4 of nieuwer.

**Belangrijkste regel:** er mag maar **één master** op de RS-485-bus staan.
SmartDDE moet uit staan zodra FlowHub draait.

---

## Fase 1 — Code ophalen

```bash
git clone https://github.com/mvandervoort/Volta-Optima.git
cd Volta-Optima
git checkout kilo/jade-frame-nk1
cd flowhub
```

Tot FlowHub naar `main` is gemerged, staat het werk op de branch
`kilo/jade-frame-nk1`.

**Controlepunt:** `ls` toont `package.json`, `src/`, `docs/`, `tools/`,
`Dockerfile` en `docker-compose.yml`.

---

## Fase 2 — Eerst zonder hardware (simulator)

Deze fase bewijst dat de software en je configuratie kloppen, zonder dat je
iets aan de bus hoeft te hangen. Sla hem niet over: als hier iets misgaat,
weet je dat het niet aan de hardware ligt.

```bash
bun install
cp config.example.json config.json
```

Zet in `config.json` tijdelijk `converter.port` op `1122` en laat de rest staan.

Start de simulator in terminal 1:

```bash
bun tools/simulator/index.ts 1122
```

Start de server in terminal 2:

```bash
FLOWHUB_ADMIN_USER=admin \
FLOWHUB_ADMIN_PASSWORD=admin-secret-123 \
FLOWHUB_SESSION_SECRET=dev-secret-1234567890 \
FLOWHUB_INSECURE_COOKIE=1 \
bun src/server/index.ts
```

Open `http://localhost:8080` en log in als `admin` / `admin-secret-123`.

> `FLOWHUB_INSECURE_COOKIE=1` is **alleen** voor http. Zodra je via https
> werkt, laat je hem weg; anders wordt de sessiecookie onveilig gezet.

**Controlepunt:**

- dashboard toont `MFC-1` met status **online**, flow 25 %, setpoint 85 %;
- setpoint wijzigen naar 50 % → de waarde komt terug als 50 %;
- klep op `open` → er verschijnt een auditregel;
- `curl http://localhost:8080/api/v1/health` → `"converter":"online"`.

---

## Fase 3 — Converter instellen

Volg `docs/converter-setup.md`. Samengevat:

1. Statisch IP in het IPC-VLAN.
2. **TCP server**-modus, poort `1111`.
3. **Transparant / raw**, géén Modbus RTU of Modbus TCP.
4. Seriële kant: **9600 8O1** (8 databits, oneven parity, 1 stopbit).

De app configureert de converter niet; die opent alleen de TCP-verbinding.
De `parity` in `config.json` is documentatie voor jou, niet iets wat de app
instelt.

**Controlepunt:** `nc -vz <converter-ip> 1111` slaagt.

---

## Fase 4 — `config.json` voor de echte bus

```bash
cp config.example.json config.json
```

Vul in:

```json
{
  "converter": {
    "host": "192.168.1.50",
    "port": 1111,
    "baudRate": 9600,
    "dataBits": 8,
    "parity": "odd",
    "stopBits": 1
  },
  "bus": {
    "pollIntervalMs": 1000,
    "devices": [
      { "id": "mfc-1", "initialName": "MFC-1", "address": "01" }
    ]
  }
}
```

Over `address`:

- kort polling-nummer: `"01"` t/m `"15"` (moet overeenkomen met de dipswitch);
- of een lang adres van 5 bytes als 10 hex-tekens, bijvoorbeeld `"8a053eeb09"`.

`id` is de stabiele sleutel in de database; wijzig hem niet later. `initialName`
wordt alleen gebruikt bij de eerste aanmaak.

**Controlepunt:** de server start zonder configuratiefout.

---

## Fase 5 — Eerste start met echte hardware

Stop de simulator. Start de server met dezelfde omgevingsvariabelen als in
fase 2, maar nu met je echte `config.json`.

**Controlepunt, binnen ongeveer 5 seconden:**

- log toont `FlowHub listening on http://localhost:8080`;
- `/api/v1/health` → `"converter":"online"`;
- het device gaat naar **online** en `lastSeen` loopt mee.

Gaat het device niet online, zie "Storingen" onderaan. Ga pas verder als één
device betrouwbaar online is.

---

## Fase 6 — Gebruikers inrichten

Log in als admin → **Gebruikers**:

- maak minimaal één `operator`-account;
- wachtwoord minimaal 10 tekens;
- admin-accounts alleen waar nodig.

**Controlepunt:** uitloggen, inloggen als operator. Het dashboard en de
setpoint-/klepbediening werken; **Gebruikers** en **Audit** zijn verborgen.

---

## Fase 7 — Schrijfacties op de bench

Met één device aangesloten:

1. Setpoint wijzigen (met bevestiging) en vergelijken met het display van de
   5850S.
2. Klep op `open`, dan `closed`, dan terug naar `normal`. Controleer of de
   fysieke klep/flow reageert.
3. Open **Audit** en controleer of elke actie er staat met gebruiker, tijd,
   oude en nieuwe waarde.

**Controlepunt:** het device volgt de opdrachten en de audit klopt. Als de
setpoint wel wordt geaccepteerd maar het device niet reageert, staat de
setpoint-source waarschijnlijk op `analog` (zie fase 8).

---

## Fase 8 — Docker + Caddy (productie)

```bash
cd flowhub
cp .env.example .env
```

Vul `.env` in:

```bash
FLOWHUB_ADMIN_USER=admin
FLOWHUB_ADMIN_PASSWORD=<sterk wachtwoord, min. 10 tekens>
FLOWHUB_SESSION_SECRET=<openssl rand -hex 32>
FLOWHUB_PORT=8080
FLOWHUB_CONFIG=/etc/flowhub/config.json
FLOWHUB_DATA_DIR=/data
# FLOWHUB_INSECURE_COOKIE=1  <- niet zetten in productie
```

> `config.json` moet naast `docker-compose.yml` bestaan **vóór** je `up` doet.
> Ontbreekt het bestand, dan maakt Docker er een map van en start de app niet.

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f app
```

**Controlepunt:**

```bash
curl -k -H 'Host: flowhub.lan' https://localhost/api/v1/health
```

geeft `"status":"online"` (of `"degraded"` zolang er nog geen device online is).
De container-healthcheck gebruikt intern `http://127.0.0.1:8080/api/v1/health`.

---

## Fase 9 — Clients en TLS

Caddy gebruikt een interne CA. Haal het root-certificaat op:

```bash
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./flowhub-root.crt
```

Op elke Windows-client:

1. `flowhub-root.crt` installeren onder **Vertrouwde basiscertificeringsinstanties**.
2. `flowhub.lan` laten resolven naar het IP van de IPC (DNS of `hosts`).

**Controlepunt:** `https://flowhub.lan` opent zonder certificaatwaarschuwing en
de login werkt (cookie wordt nu `Secure` gezet).

---

## Fase 10 — Back-up

Het back-upscript zit in de image:

```bash
docker compose exec app bun scripts/backup.ts
```

Standaard schrijft het naar `./backups` **binnen de container**. Zet voor
productie een expliciete map in het volume:

```bash
docker compose exec -e FLOWHUB_BACKUP_DIR=/data/backups -e FLOWHUB_BACKUP_RETENTION=14 \
  app bun scripts/backup.ts
```

Dagelijks via cron op de host:

```cron
15 2 * * * cd /opt/Volta-Optima/flowhub && docker compose exec -e FLOWHUB_BACKUP_DIR=/data/backups app bun scripts/backup.ts >> /var/log/flowhub-backup.log 2>&1
```

Kopieer de back-ups periodiek van de IPC af; een back-up op dezelfde schijf is
geen back-up. Restore staat in `docs/restore.md`.

**Controlepunt:** er staat een `flowhub-<tijdstip>.db` in de back-upmap en een
test-restore is één keer uitgevoerd.

---

## Fase 11 — Cutover van SmartDDE

1. Lees met SmartDDE de baseline uit (flow, setpoint, units) en noteer die.
2. **Stop SmartDDE** — er mag maar één master op de bus staan.
3. Start FlowHub (fase 5 of 8).
4. Vergelijk de waarden met je baseline en met de displays.
5. Laat een operator een oefenwijziging doen en controleer de audit.
6. Verwijs SmartDDE af en ruim de oude installatie op.

**Rollback:** stop FlowHub, start SmartDDE opnieuw. De bus en de devices zijn
niet gewijzigd; FlowHub schrijft alleen setpoint, klep-override en
configuratieparameters, en elke write wordt geaudit.

---

## Acceptatiechecklist

- [ ] `/api/v1/health` is `online`, alle enabled devices online
- [ ] operator kan inloggen en ziet alleen toegestane schermen
- [ ] setpoint schrijven werkt en komt overeen met het device
- [ ] klep-override werkt en wordt geaudit
- [ ] audit toont gebruiker, tijd, oud/nieuw en resultaat
- [ ] https werkt op elke client zonder waarschuwing
- [ ] back-up draait en een restore is getest
- [ ] SmartDDE staat uit en is verwijderd van de IPC
- [ ] runbook (`docs/runbook.md`) is doorgenomen met de operators

---

## Storingen — snel

| Symptoom | Eerste controle |
| --- | --- |
| `converter: offline` | `nc -vz <ip> 1111`; converter aan/bereikbaar? |
| Converter online, alle devices offline | baudrate/parity, transparante modus, kabel/terminatie |
| Eén device offline | device uit, dipswitch-adres, dubbel adres op de bus |
| Setpoint geaccepteerd, device reageert niet | setpoint-source staat op `analog` |
| Login werkt niet via http | `FLOWHUB_INSECURE_COOKIE=1` (alleen lokaal) |
| Login werkt niet via https | root-CA niet vertrouwd op de client |
| App start niet in Docker | `config.json` ontbreekt naast `docker-compose.yml` |
| `docker compose` klaagt over variabelen | `.env` ontbreekt of is onvolledig |

---

## Wat nog niet is bewezen

Wees hier eerlijk over richting de klant:

- De **Docker-build is nooit uitgevoerd** in de ontwikkelsandbox (geen Docker
  beschikbaar). Fase 8 is de eerste echte test; reken op een iteratie.
- Er is **geen echte 5850S** getest. Fase 5 en 7 zijn de hardwarevalidatie.
- **Playwright E2E** is nog niet geschreven; UI-tests zijn handmatig gedaan.
- Write-protect (#128) wordt niet ondersteund door de 5850S. De UI toont dat
  als "niet ondersteund"; dat is verwacht gedrag, geen fout.
- Geen GMP/21 CFR Part 11 en geen SIL. De audit is operationeel, de noodstop
  blijft hardwarematig.