# Converter setup

FlowHub praat met de 5850S via een Waveshare RS232/485-to-Ethernet converter
(SKU 16530). De app configureert de converter **niet**; dat gebeurt eenmalig
handmatig in de webinterface van de converter. De app opent alleen een
TCP-verbinding en stuurt transparante bytes.

## 1. Netwerk

1. Sluit de converter aan op het geïsoleerde VLAN van de IPC.
2. Geef een **statisch IP** (bijv. `192.168.1.50`) en noteer host + poort.
3. Zet de TCP-servermodus aan (de converter luistert, de app verbindt).
4. Noteer de poort (standaard `1111`) en zet die in `config.json` onder
   `converter.port`.

## 2. Seriële kant

De 5850S gebruikt standaard **9600 8O1** (8 databits, oneven parity, 1 stopbit).

| Instelling | Waarde |
| --- | --- |
| Baudrate | 9600 (1200–38400 mogelijk) |
| Databits | 8 |
| Parity | odd (oneven) |
| Stopbits | 1 |
| Modus | RS-485, transparant |

Let op: de parity in `config.json` is alleen documentatie voor de beheerder.
De converter doet de daadwerkelijke framing; de app kan parity niet instellen
en een verkeerde parity geeft stil falen (geen antwoorden, geen foutmelding).

## 3. Transparante modus

- Kies **transparant / raw**, niet Modbus RTU of Modbus TCP.
- Zet geen frame-conversie, geen packet-splitting en geen timeout-actie aan.
- De converter mag niet zelf het antwoord bufferen; FlowHub doet de
  stream-reassembly en checksumvalidatie.

## 4. RS-485-bus

- Daisy-chain, één master (FlowHub).
- Terminatie (120 Ω) aan beide uiteinden, bias-weerstanden één keer.
- Adressen 0–31 (kort polling-adres 1–15, lange adressen 5-byte hex).
- SmartDDE mag **niet** gelijktijdig op dezelfde bus draaien.

## 5. Verifiëren vóór ingebruikname

1. `nc -vz <converter-ip> <poort>` moet slagen.
2. Start FlowHub en controleer `/api/v1/health` → `converter: online`.
3. Eén device moet binnen enkele seconden `status: online` tonen.
4. Vergelijk flow en setpoint met de waarde op het 5850S-display.

Bij `converter: offline` ondanks een bereikbare poort: controleer baudrate,
parity en of de converter echt in transparante modus staat.

## 6. Bekende valkuilen

- Waveshare accepteert maximaal 8 gelijktijdige TCP-clients; FlowHub gebruikt
  er één.
- Een verkeerde dipswitch-stand op de 5850S (baudrate/adres) geeft geen
  antwoord en is niet te onderscheiden van een kabelbreuk.
- Na een converter-herstel of IP-wijziging moet FlowHub opnieuw verbinden;
  dat gebeurt automatisch met backoff.