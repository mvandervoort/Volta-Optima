# Brooks S-protocol — implementatiereferentie

**Bron:** Brooks *RS485 Communications S-Protocol for GF40 & GF80 Series*
(Manual 541-C-053-AAA), gecombineerd met *RS485 Manual SLA5800 & SLAMf*
(541-C-053-equivalent). Cross-check: 4800-serie supplement `541B136AAG`.

De 5850S gebruikt dezelfde S-protocol commandoset als GF40/GF80 en SLA5800.
De layouts hieronder zijn identiek geverifieerd in beide bronnen. De code-tabellen
(9-3, 9-5, 9-14 e.a.) komen uit de GF40/GF80-manual, paragraaf "Transmitter
Specific Tables". Waar de 5850S afwijkt, staat dat expliciet vermeld.

**BELANGRIJK:** dit bestand is de gezaghebbende code voor de codec. Wijzig niets
in `src/server/bus/sProtocol.ts` dat hier niet onderbouwd is.

---

## 1. Fysieke laag

- UART: 1 startbit, 8 databits, **1 parity bit (odd)**, 1 stopbit → 8O1 (default 9600).
- Baudrate 1200–38400; RS-485 multidrop, max 32 devices, adressen 0–31.
- Converter: transparante hex-modus, app opent alleen TCP; converter wordt niet door
  FlowHub geconfigureerd.
- Minimaal **5 preamble-tekens (0xFF)** meesturen (manual: slave heeft er 2 nodig,
  maar door converterverlies minimaal 5 sturen).

## 2. Frame-structuur (HART)

```
[preamble 0xFF ×5] [start] [address] [command] [byte count] [status×2] [data] [checksum]
```

- **Start character** (1 byte):
  - Kort frame (1-byte adres): master→slave `0x02`, slave→master `0x06`.
  - Lang frame (5-byte adres): master→slave `0x82`, slave→master `0x86`.
  - Bit 7 = adresetting (0 kort / 1 lang); laagste 3 bits: `010` = STX, `110` = ACK.
- **Address:** kort = 1 byte (LS-nibble = polling-adres, 0–15); lang = 5 bytes
  (6-bit manufacturer-ID = 10, 1 byte device type = 90, 3 byte device-ID).
- **Command:** 1 byte, 0–255.
- **Byte count:** 1 byte; telt de 2 statusbytes (alleen respons) + databytes.
  **Sluite NIET de checksum-byte in.**
- **Status:** alleen in slave→master, 2 bytes. Zie §7.
- **Data:** max 24 bytes. Formaten: uint8, uint24, IEEE-754 float32 (big-endian),
  ASCII, packed-ASCII (6-bit).
- **Checksum:** XOR ("longitudinal parity") van alle bytes **vanaf start character
  t/m data**, exclusief de checksum zelf. De XOR van het volledige frame (inclusief
  checksum) is exact 0.

**Verificatie tegen echte capture** (4800, command #236, setpoint 85%):
`FF FF FF FF FF 82 8A 05 3E EB 09 EC 05 39 42 AA 00 00 E9`
→ XOR(start..data) = `0xE9` = laatste byte; float `42 AA 00 00` = **85.0**. ✓

## 3. Datatypes

- **uint8:** 1 byte, big-endian.
- **uint24:** 3 bytes, big-endian (b0<<16 | b1<<8 | b2).
- **IEEE-754 float32:** big-endian, 4 bytes.
- **ASCII:** 8-bit per teken.
- **Packed-ASCII (6-bit):** verwijder bit 7 en 6 van elke ASCII-char; pak 4×6-bit
  in 3 bytes. 8 tekens → 6 bytes. Reconstructie: unpack 4×6-bit, zet bit 5-complement
  in bit 6, bit 7 = 0. Tabel 3-3 codes: `@`=00, `A`=01 … `Z`=1A, `[`=1B, `\`=1C,
  `]`=1D, `^`=1E, `_`=1F, spatie=20, `!`=21 … `?`=3F.

## 4. Adressering en discovery

- **Kort frame:** 1-byte polling-adres, LS-nibble 1–15 (0 = broadcast).
- **Lang frame:** 5-byte adres (manufacturer 10 + device type 90 + device-ID 24-bit).
- **Broadcast lang adres `0000000000`:** alle slaves; alleen #11 reageert, en alleen
  op matchende tag.
- **Command #11 (Read Unique ID by Tag):** request = 6 bytes packed-ASCII tag (8
  tekens = laatste 8 cijfers van serienummer). Response = #0-formaat (zie §5.1).
- **Command #6 (Write Polling Address):** request/response data = 1 byte polling
  address (0–15). Alleen kort frame.
- Device-type code voor alle GF40/GF80/5850S = **90 (dec)**; manufacturer = **10 (dec)**.

## 5. Commandoreferentie

Notatie: `data[]` is de data-sectie (na statusbytes); request stuurt deze bytes mee,
response bevat deze bytes.

### 5.1 Universal commands (0–19)

| Cmd | Naam | Request | Response |
|-----|------|---------|----------|
| #0  | Read Unique Identifier | — | `254, mfrID, devType, preambles, univRev, transRev, swRev, hwRev, flags, devID[3]` (12 bytes) |
| #1  | Read Primary Variable | — | `unit(uint8), flow(float32)` (5 bytes) |
| #2  | Read Primary Variable Current & %Range | — | `unit(uint8), flow(float32), current/voltage(float32), pv%(float32)` (13 bytes) |
| #3  | Read Current and all Dynamic Variables | — | `current(float32), pvUnit(uint8), pv(float32), svUnit(uint8), sv(float32)` (14 bytes) |
| #6  | Write Polling Address | `addr(uint8)` | `addr(uint8)` |
| #11 | Read Unique ID by Tag | `tag(6×packed-ASCII)` | `254, mfrID, devType, preambles, univRev, transRev, swRev, hwRev, flags, devID[3]` (12 bytes) |
| #13 | Read Tag, Descriptor, Date | — | `tag[6], descriptor[12], date[3]` |
| #48 | Read Additional Transmitter Status | — | `status[6] + additional` |

**#0/#11 response layout (12 bytes):**
```
#0  device type expansion code = 254 (uint8)
#1  manufacturer identification code = 10 (uint8)
#2  manufacturer device type code = 90 (uint8)
#3  number of response preamble characters (uint8)
#4  universal command revision level (uint8)
#5  transmitter specific command revision level (uint8)
#6  software revision level (uint8)
#7  hardware revision level (uint8)
#8  flags (uint8)
#9-11 device identification number (uint24)
```

### 5.2 Read-only transmitter commands

| Cmd | Naam | Response |
|-----|------|----------|
| #150 | Read Process Gas Type | gas type code (uint8) |
| #151 | Read Gas Density, Flow Reference & Range | density(float32), flow ref(uint8), flow range(float32) |
| #152 | Read Full Scale Flow Range | full scale(float32) |
| #190 | Read Standard Temperature & Pressure | stp(float32), stp(float32) |
| #193 | Read Operational Settings | zie manual §8 |
| #230 | Get Valve Override Status | `valve override code (uint8)` |
| #235 | Read Setpoint in % and Selected Units | `unitCode(uint8=57), setp%(float32), flowUnit(uint8), setpUnits(float32)` (10 bytes) |
| #237 | Read Valve Control Value | valve control value (uint24) |
| #240 | Read Totalizer Status | totalizer status (uint8) |
| #245 | Read Alarm Enable | alarm enable code (uint8) |
| #247 | Read High/Low Flow Alarm | zie manual §8 |

### 5.3 Schrijfacties (request = response-layout)

| Cmd | Naam | Request data |
|-----|------|--------------|
| #128 | Enter/Exit Write Protect Mode (Non-Public) | **Geen effect op GF40/GF80/5850S** — write-protect wordt daar niet ondersteund. Zie §6. |
| #195 | Select Gas Calibration | calibration number (uint8, 1–6) |
| #196 | Select Flow Unit | `flow ref(uint8), flow unit(uint8)` (2 bytes) |
| #197 | Select Temperature Unit | `temp unit(uint8)` (1 byte) |
| #215 | Read Setpoint Settings | — |
| #216 | Select Setpoint Source | `setpoint source code(uint8)` |
| #218 | Select Softstart | softstart code(uint8) |
| #219 | Write Linear Softstart Ramp Value | ramp up(float32), ramp down(float32) |
| #220 | Read PID Controller Values | — |
| #221 | Write PID Controller Values | zie manual §8 |
| #222 | Read Valve Range & Offset | valve range(float32), valve offset(float32) |
| #223 | Write Valve Range & Offset | valve range(float32), valve offset(float32) |
| #231 | Set Valve Override Status | `valve override code(uint8)` (0=off, 1=open, 2=close) |
| #236 | Write Setpoint in % or Selected Units | `unitCode(uint8), setp(float32)` (5 bytes) |
| #246 | Write Alarm Enable | alarm enable code(uint8) |
| #248 | Write High/Low Flow Alarm | zie manual §8 |

**#235 response layout (10 bytes):**
```
#0     percent unit code = 57 (uint8)
#1-4   setpoint in % of full scale (float32)
#5     selected flow unit code (uint8)
#6-9   setpoint in selected flow unit (float32)
```

**#236 request layout (5 bytes):**
```
#0     unit code (57 = percent, 250/Not Used = selected flow unit)
#1-4   setpoint value (float32)
```
Response = #235-layout. **Let op:** na #236 schakelt de device automatisch de
setpoint-source naar digital (tot #216 of power-cycle).

**#196 request layout (2 bytes):** `#0 flow reference, #1 flow unit`
**#197 request layout (1 byte):** `#0 temperature unit`
**#231 request layout (1 byte):** `#0 valve override code`

### 5.4 Readback na write (verplicht in FlowHub)

- Na **#236** → readback via **#235** (en #237 valve control).
- Na **#231** → readback via **#230**.
- Na **#196/#197/#128/#216** → readback van de betreffende read-command.

## 6. Write-protect (belangrijke correctie)

De GF40/GF80/5850S ondersteunen **geen** write-protect via #128: de manual stelt
expliciet *"Write Protect mode is not supported by GF40/GF80 Series"* en command
#128 *"is not required and has no effect."* De write-protect-codes (tabel 9-8)
beschrijven alleen `0 = not write protected` / `2..249 undefined`.

**Gevolg voor FlowHub:** `writeProtect` in de config en de write-protect-status in
de UI moeten de device-werkelijkheid volgen — voor 5850S is write-protect niet
beschikbaar. De UI toont de status als "niet ondersteund" i.p.v. een schakelaar te
bieden die niets doet. Isoleer dit achter een capability-check zodat de code
toekomstige Brooks-types (die write-protect wél ondersteunen) kan accommoderen.

## 7. Statusbytes (beide responsbytes)

- **Byte 0, bit 7 = 1 → communicatiefout.** Dan is byte 1 = 0 en gelden:
  - bit 6 parity error (0xC0), bit 5 overrun (0xA0), bit 4 framing (0x90),
    bit 3 checksum (0x88), bit 1 Rx buffer overflow (0x82).
- **Byte 0, bit 7 = 0 → command execution info** (bit 6 device malfunction,
  bit 5 configuration changed, bit 4 cold start, bit 3 analog output fixed,
  bit 2 analog output saturated, bit 1 non-primary out of range,
  bit 0 primary out of range). **Byte 1 = device status** (zie additional status
  command #48 voor detail).
- **Command error codes** (byte 0, bits 6..0, niet bit-mapped):
  `0` no error, `2` invalid selection, `3` parameter too large, `4` parameter too
  small, `5` incorrect byte count, `6` transmitter specific command error,
  `7` in write-protect mode, `8–15` command specific, `16` access restricted,
  `32` device busy, `64` commanded not implemented.

**FlowHub moet beide statusbytes per respons loggen** en bij een niet-nul status de
device als "fault" markeren in de UI (statusbadge), niet als offline.

## 8. Code-tabellen

### 8.1 Flow rate unit codes (9-3)
| Code | Unit |
|------|------|
| 17 | Liters/minute |
| 19 | Cubic meters/hour |
| 24 | Liters/second |
| 28 | Cubic meters/second |
| 57 | Percent of flow range |
| 131 | Cubic meters/minute |
| 138 | Liters/hour |
| 170 | Millilitres/second |
| 171 | Millilitres/minute |
| 172 | Millilitres/hour |
| 0–16,18,20–23,25–27,29–56,58–130,132–137,139–169,173–249 | Undefined |

**Flow reference codes** (zelfde tabel): `0 Normal (273.15 K / 1013.33 mBar)`,
`1 Standard (user defined)`, `2 Calibration`, `3..249 undefined`, `250..255 reserved`.

### 8.2 Temperature unit codes (9-5)
| Code | Unit |
|------|------|
| 32 | Degrees Celsius |
| 33 | Degrees Fahrenheit |
| 35 | Kelvin |
| 0–31,34,36–249 | Undefined |

### 8.3 Valve override codes (9-14)
| Code | Betekenis |
|------|-----------|
| 0 | Valve override off (normal operation) |
| 1 | Valve override open |
| 2 | Valve override close |
| 3 | Valve override manual (read-only) |
| 4–249 | Undefined |

**Note (manual):** deze codes zijn *"alle 'Undefined' voor de meter-modellen"*.
Alleen controller-modellen (5850S/5851S/5853S) ondersteunen valve override.

### 8.4 Setpoint source codes (9-12)
| Code | Betekenis |
|------|-----------|
| 1..2 | Analog input |
| 3 | Digital communication input |
| 10 | Analog in/out 0–5 V |
| 11 | Analog in/out 0–10 V |
| 20 | Analog in/out 0–20 mA |
| 21 | Analog in/out 4–20 mA |

### 8.5 Softstart codes (9-13)
| Code | Betekenis |
|------|-----------|
| 0 | Softstart disabled |
| 4 | Linear up and down softstart |

### 8.6 Totalizer unit codes (9-16)
| Code | Unit |
|------|------|
| 41 | liters |
| 43 | cubic meters |
| 60 | gram |
| 61 | kilogram |
| 63 | pound |
| 175 | milliliter |

### 8.7 Device type (9-2)
Alle GF40/GF80/5850S: device type code = **90**.

## 9. Eenheidsconsistentie (kritiek)

De setpoint/#196/#197-write moet de engineering-unit van de device volgen. De
manual waarschuwt dat #236-unit code 57 = percent, en dat bij "Not Used" de waarde
in de geselecteerde flow-unit wordt geïnterpreteerd. **FlowHub blokkeert een
setpoint-write als de gevraagde engineering unit niet overeenkomt met de device
flow unit (#196/#1/#235 readback).** Vergelijk vóór write altijd de readback-unit
met de gevraagde unit; bij mismatch → weiger met auditregel, geen stille conversie.

## 10. Bronbestanden

- GF40/GF80: `RS485-S-Protocol-Manual-GF40-GF80-EN.pdf` (brooksinstrument.com, 2024).
- SLA5800/SLAMf: `RS485-Manual-SLA5800-SLAMf-EN.pdf` (sales.brooksinstrument.com, 2024).
- 4800 cross-check: `541B136AAG` (manualslib; 403 op directe fetch, capture-frame
  hierboven geverifieerd tegen de float-decodering).
- 5850S device-manual: `X-TMF-5800S-MFC-eng` (541-C-051-AAG), verwijst naar
  `541-C-053-AAA` voor de communicatiecommando's.