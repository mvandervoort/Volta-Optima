export const PREAMBLE = 0xff;
export const START_SHORT_MASTER = 0x02;
export const START_SHORT_SLAVE = 0x06;
export const START_LONG_MASTER = 0x82;
export const START_LONG_SLAVE = 0x86;

export const CMD = {
  READ_PRIMARY_VARIABLE: 1,
  READ_PRIMARY_VARIABLE_CURRENT_PERCENT: 2,
  READ_DYNAMIC_VARIABLES: 3,
  WRITE_POLLING_ADDRESS: 6,
  READ_UNIQUE_IDENTIFIER: 11,
  READ_TAG_DESCRIPTOR_DATE: 13,
  READ_ADDITIONAL_STATUS: 48,
  READ_PROCESS_GAS_TYPE: 150,
  READ_GAS_DENSITY_RANGE: 151,
  READ_FULL_SCALE: 152,
  READ_STP: 190,
  READ_OPERATIONAL_SETTINGS: 193,
  READ_GAS_NUMBER: 195,
  READ_FLOW_UNIT: 196,
  READ_TEMPERATURE_UNIT: 197,
  READ_SETPOINT_SETTINGS: 215,
  WRITE_SETPOINT_SOURCE: 216,
  READ_VALVE_OVERRIDE: 230,
  WRITE_VALVE_OVERRIDE: 231,
  READ_SETPOINT: 235,
  WRITE_SETPOINT: 236,
  READ_VALVE_CONTROL: 237,
  READ_ALARM_ENABLE: 245,
  WRITE_ALARM_ENABLE: 246,
  READ_ALARM_LIMITS: 247,
  WRITE_ALARM_LIMITS: 248,
} as const;

export type ParsedFrame = {
  start: number;
  long: boolean;
  address: Uint8Array;
  command: number;
  byteCount: number;
  status: Uint8Array;
  data: Uint8Array;
  checksum: number;
  raw: Uint8Array;
};

export function xorChecksum(bytes: Uint8Array): number {
  let value = 0;
  for (const byte of bytes) value ^= byte;
  return value;
}

export function buildRequest(
  address: number | Uint8Array,
  command: number,
  data: Uint8Array = new Uint8Array(),
): Uint8Array {
  const long = typeof address !== "number";
  const addressBytes = long ? address : Uint8Array.of(address);
  const start = long ? START_LONG_MASTER : START_SHORT_MASTER;
  const bodyLength = 1 + addressBytes.length + 1 + data.length;
  const body = new Uint8Array(bodyLength);
  let offset = 0;
  body[offset++] = start;
  body.set(addressBytes, offset);
  offset += addressBytes.length;
  body[offset++] = command;
  body.set(data, offset);

  const frame = new Uint8Array(5 + bodyLength + 1);
  frame.fill(PREAMBLE, 0, 5);
  frame.set(body, 5);
  frame[frame.length - 1] = xorChecksum(body);
  return frame;
}

export class FrameParser {
  private buffer = new Uint8Array(0);

  push(chunk: Uint8Array): ParsedFrame[] {
    const combined = new Uint8Array(this.buffer.length + chunk.length);
    combined.set(this.buffer, 0);
    combined.set(chunk, this.buffer.length);
    this.buffer = combined;
    return this.drain();
  }

  reset(): void {
    this.buffer = new Uint8Array(0);
  }

  private drain(): ParsedFrame[] {
    const frames: ParsedFrame[] = [];
    let index = 0;
    while (index < this.buffer.length) {
      const start = this.buffer[index];
      if (start !== START_SHORT_SLAVE && start !== START_LONG_SLAVE) {
        index += 1;
        continue;
      }
      const long = start === START_LONG_SLAVE;
      const addressLength = long ? 5 : 1;
      const headerLength = 1 + addressLength + 1 + 1;
      if (this.buffer.length - index < headerLength + 1) break;
      const byteCount = this.buffer[index + 1 + addressLength + 1]!;
      const total = headerLength + byteCount + 1;
      if (this.buffer.length - index < total) break;
      const raw = this.buffer.slice(index, index + total);
      const body = raw.slice(0, raw.length - 1);
      const expected = xorChecksum(body);
      if (expected !== raw[raw.length - 1]) {
        index += 1;
        continue;
      }
      const address = raw.slice(1, 1 + addressLength);
      const command = raw[1 + addressLength]!;
      const status = raw.slice(1 + addressLength + 2, 1 + addressLength + 2 + 2);
      const data = raw.slice(1 + addressLength + 2 + 2, raw.length - 1);
      frames.push({
        start,
        long,
        address,
        command,
        byteCount,
        status,
        data,
        checksum: raw[raw.length - 1]!,
        raw,
      });
      index += total;
    }
    this.buffer = this.buffer.slice(index);
    return frames;
  }
}

export function encodeFloat(value: number): Uint8Array {
  const bytes = new Uint8Array(4);
  new DataView(bytes.buffer).setFloat32(0, value, false);
  return bytes;
}

export function decodeFloat(data: Uint8Array, offset = 0): number {
  if (data.length < offset + 4) return Number.NaN;
  return new DataView(data.buffer, data.byteOffset + offset, 4).getFloat32(0, false);
}

export function encodeUint8(value: number): Uint8Array {
  return Uint8Array.of(value & 0xff);
}

export function decodeUint8(data: Uint8Array, offset = 0): number {
  return data[offset] ?? 0;
}

export function encodeUint24(value: number): Uint8Array {
  return Uint8Array.of((value >>> 16) & 0xff, (value >>> 8) & 0xff, value & 0xff);
}

export function decodeUint24(data: Uint8Array, offset = 0): number {
  return ((data[offset] ?? 0) << 16) | ((data[offset + 1] ?? 0) << 8) | (data[offset + 2] ?? 0);
}

export function decodeAscii(data: Uint8Array): string {
  return new TextDecoder("ascii").decode(data).replace(/\0/g, "").trim();
}

const PACKED_ASCII_CODES: Record<string, number> = {
  "@": 0x00,
  A: 0x01,
  B: 0x02,
  C: 0x03,
  D: 0x04,
  E: 0x05,
  F: 0x06,
  G: 0x07,
  H: 0x08,
  I: 0x09,
  J: 0x0a,
  K: 0x0b,
  L: 0x0c,
  M: 0x0d,
  N: 0x0e,
  O: 0x0f,
  P: 0x10,
  Q: 0x11,
  R: 0x12,
  S: 0x13,
  T: 0x14,
  U: 0x15,
  V: 0x16,
  W: 0x17,
  X: 0x18,
  Y: 0x19,
  Z: 0x1a,
  "[": 0x1b,
  "\\": 0x1c,
  "]": 0x1d,
  "^": 0x1e,
  _: 0x1f,
  " ": 0x20,
  "!": 0x21,
  '"': 0x22,
  "#": 0x23,
  $: 0x24,
  "%": 0x25,
  "&": 0x26,
  "'": 0x27,
  "(": 0x28,
  ")": 0x29,
  "*": 0x2a,
  "+": 0x2b,
  ",": 0x2c,
  "-": 0x2d,
  ".": 0x2e,
  "/": 0x2f,
  "0": 0x30,
  "1": 0x31,
  "2": 0x32,
  "3": 0x33,
  "4": 0x34,
  "5": 0x35,
  "6": 0x36,
  "7": 0x37,
  "8": 0x38,
  "9": 0x39,
  ":": 0x3a,
  ";": 0x3b,
  "<": 0x3c,
  "=": 0x3d,
  ">": 0x3e,
  "?": 0x3f,
};

const PACKED_ASCII_CHARS = Object.entries(PACKED_ASCII_CODES).reduce<Record<number, string>>(
  (map, [char, code]) => {
    map[code] = char;
    return map;
  },
  {},
);

export function packedAsciiToBytes(tag: string): Uint8Array {
  const chars = tag.toUpperCase().slice(0, 8).split("");
  while (chars.length % 4 !== 0) chars.push("@");
  const bytes: number[] = [];
  for (let index = 0; index < chars.length; index += 4) {
    const c0 = PACKED_ASCII_CODES[chars[index]!] ?? 0;
    const c1 = PACKED_ASCII_CODES[chars[index + 1]!] ?? 0;
    const c2 = PACKED_ASCII_CODES[chars[index + 2]!] ?? 0;
    const c3 = PACKED_ASCII_CODES[chars[index + 3]!] ?? 0;
    bytes.push((c0 << 2) | (c1 >> 4));
    bytes.push(((c1 & 0x0f) << 4) | (c2 >> 2));
    bytes.push(((c2 & 0x03) << 6) | c3);
  }
  return Uint8Array.from(bytes);
}

export function packedAsciiFromBytes(bytes: Uint8Array): string {
  const chars: string[] = [];
  for (let index = 0; index + 2 < bytes.length; index += 3) {
    const b0 = bytes[index]!;
    const b1 = bytes[index + 1]!;
    const b2 = bytes[index + 2]!;
    chars.push(PACKED_ASCII_CHARS[b0 >> 2] ?? "?");
    chars.push(PACKED_ASCII_CHARS[((b0 & 0x03) << 4) | (b1 >> 4)] ?? "?");
    chars.push(PACKED_ASCII_CHARS[((b1 & 0x0f) << 2) | (b2 >> 6)] ?? "?");
    chars.push(PACKED_ASCII_CHARS[b2 & 0x3f] ?? "?");
  }
  return chars.join("").replace(/@+$/g, "");
}

export function parseResponse(frame: ParsedFrame): {
  status: Uint8Array;
  payload: Uint8Array;
  command: number;
  address: Uint8Array;
} {
  return {
    status: frame.status,
    payload: frame.data,
    command: frame.command,
    address: frame.address,
  };
}