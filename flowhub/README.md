# FlowHub

Headless Linux-service voor het uitlezen, instellen en configureren van Brooks
5850S mass flow controllers via het Brooks S-protocol (RS-485) achter een
TCP/IP-naar-RS-485-converter. De bediening gebeurt in een browser; er is geen
desktopapplicatie en geen Windows-client.

## Architectuur

```
browser ──HTTPS──> Caddy ──> Bun/Hono app ──TCP transparant──> converter ──RS-485──> 5850S
                              │                                    │
                              │                                    └─ polling 1 Hz, sequentieel
                              ├─ REST: /api/v1/{health,auth,users,devices,audit}
                              └─ WebSocket: /api/v1/ws (live state)
```

De service is de enige master op de bus. SmartDDE mag niet gelijktijdig op
dezelfde bus draaien.

## Snel starten (development)

```bash
bun install
cp config.example.json config.json     # converter-adres en devices aanpassen
bun run dev                            # server op :8080
bun run dev:web                        # Vite op :5173 (optioneel)
```

Of de simulator erbij, zonder hardware:

```bash
bun tools/simulator/index.ts 1122
# config.json: converter.port = 1122
bun src/server/index.ts
```

De beheerder wordt bij de eerste start aangemaakt uit `FLOWHUB_ADMIN_USER`
en `FLOWHUB_ADMIN_PASSWORD` (zie `.env.example`).

## Productie

```bash
docker compose up -d --build
```

Caddy serveert `https://flowhub.lan` met een interne CA. Accepteer de
CA op de Windows-clients (zie `docs/converter-setup.md`) of gebruik een
eigen certificaat.

## Verificatie

```bash
bun test               # codec, polling, golden frames
bun run typecheck
bun run lint
bun run build
```

## Documentatie

- `docs/s-protocol.md` — byte-layouts, commando- en statuscodes
- `docs/plan.md` — ontwerp en checklist
- `docs/converter-setup.md` — converterconfiguratie
- `docs/restore.md` — back-up en restore

## Belangrijke beperkingen

- Write-protect (#128) wordt niet ondersteund door de 5850S; de UI toont dit
  capability-gated.
- Niet gereguleerd: geen GMP/21 CFR Part 11, geen e-signatures.
- Geen veiligheidsfunctie: noodstop blijft hardwarematig.
- Baudrate wijzigen kan niet via de app; dat gaat via dipswitch en converter.