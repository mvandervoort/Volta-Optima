import { describe, expect, test } from "bun:test";
import {
  buildRequest,
  CMD,
  decodeFloat,
  decodeUint24,
  decodeUint8,
  encodeFloat,
  FrameParser,
  packedAsciiFromBytes,
  packedAsciiToBytes,
  xorChecksum,
} from "../src/server/bus/sProtocol";

describe("S-protocol codec", () => {
  test("short-frame request #236 matches documented layout", () => {
    const body = Uint8Array.from([0x39, 0x42, 0xaa, 0x00, 0x00]);
    const req = buildRequest(5, CMD.WRITE_SETPOINT, body);
    expect(Array.from(req)).toEqual([
      0xff, 0xff, 0xff, 0xff, 0xff, 0x02, 0x05, 0xec, 0x39, 0x42, 0xaa, 0x00, 0x00, 0x3a,
    ]);
  });

  test("long-frame request uses 0x82 start and 5-byte address", () => {
    const address = Uint8Array.from([0x8a, 0x05, 0x3e, 0xeb, 0x09]);
    const req = buildRequest(address, CMD.READ_SETPOINT);
    expect(req[5]).toBe(0x82);
    expect(Array.from(req.slice(6, 11))).toEqual([0x8a, 0x05, 0x3e, 0xeb, 0x09]);
    expect(req[11]).toBe(CMD.READ_SETPOINT);
  });

  test("checksum XORs start..data to the checksum byte", () => {
    const req = buildRequest(5, CMD.READ_SETPOINT);
    const body = req.slice(5, -1);
    const last = req[req.length - 1]!;
    expect(xorChecksum(body)).toBe(last);
    expect(xorChecksum(req.slice(5))).toBe(0);
  });

  test("parses a #235 response with status and data", () => {
    const body = [
      0x06, 0x05, 235, 12, 0x00, 0x00, 0x39, 0x42, 0xaa, 0x00, 0x00, 0x11, 0x42, 0xaa, 0x00, 0x00,
    ];
    let x = 0;
    for (const b of body) x ^= b;
    const frame = Uint8Array.from([0xff, 0xff, 0xff, 0xff, 0xff, ...body, x]);
    const frames = new FrameParser().push(frame);
    expect(frames).toHaveLength(1);
    const parsed = frames[0]!;
    expect(parsed.command).toBe(235);
    expect(parsed.byteCount).toBe(12);
    expect(Array.from(parsed.status)).toEqual([0, 0]);
    expect(decodeUint8(parsed.data, 0)).toBe(57);
    expect(decodeFloat(parsed.data, 1)).toBe(85);
    expect(decodeUint8(parsed.data, 5)).toBe(17);
    expect(decodeFloat(parsed.data, 6)).toBe(85);
  });

  test("parses a #0 unique-identifier response", () => {
    const body = [
      0x06, 0x05, 0x00, 14, 0x00, 0x00, 0xfe, 0x0a, 0x5a, 0x02, 0x05, 0x01, 0x00, 0x00, 0x00, 0x3e,
      0xeb, 0x09,
    ];
    let x = 0;
    for (const b of body) x ^= b;
    const frame = Uint8Array.from([0xff, 0xff, 0xff, 0xff, 0xff, ...body, x]);
    const frames = new FrameParser().push(frame);
    expect(frames).toHaveLength(1);
    const d = frames[0]!.data;
    expect(d).toHaveLength(12);
    expect(decodeUint8(d, 0)).toBe(254);
    expect(decodeUint8(d, 1)).toBe(10);
    expect(decodeUint8(d, 2)).toBe(90);
    expect(decodeUint24(d, 9)).toBe(0x3eeb09);
  });

  test("drops a frame with a bad checksum and keeps buffering", () => {
    const good = [0x06, 0x01, 0x01, 2, 0x00, 0x00, 0x11, 0x22];
    const bad = [...good];
    bad.push((good.reduce((a, b) => a ^ b, 0) ^ 0xff) & 0xff);
    const parser = new FrameParser();
    expect(parser.push(Uint8Array.from([0xff, ...bad]))).toHaveLength(0);
  });

  test("handles fragmented chunks across pushes", () => {
    const body = [0x06, 0x05, 231, 3, 0x00, 0x00, 0x02];
    let x = 0;
    for (const b of body) x ^= b;
    const frame = Uint8Array.from([0xff, 0xff, ...body, x]);
    const parser = new FrameParser();
    expect(parser.push(frame.slice(0, 4))).toHaveLength(0);
    expect(parser.push(frame.slice(4, 7))).toHaveLength(0);
    const out = parser.push(frame.slice(7));
    expect(out).toHaveLength(1);
    expect(out[0]!.command).toBe(231);
    expect(decodeUint8(out[0]!.data, 0)).toBe(2);
  });

  test("float round-trips big-endian", () => {
    const encoded = encodeFloat(85.5);
    expect(Array.from(encoded)).toEqual([0x42, 0xab, 0x00, 0x00]);
    expect(decodeFloat(encoded)).toBeCloseTo(85.5, 5);
  });

  test("uint24 decodes big-endian device id", () => {
    expect(decodeUint24(Uint8Array.from([0x3e, 0xeb, 0x09]))).toBe(0x3eeb09);
  });

  test("packed-ascii packs 8 chars into 6 bytes and back", () => {
    const packed = packedAsciiToBytes("5850S001");
    expect(packed).toHaveLength(6);
    expect(packedAsciiFromBytes(packed)).toBe("5850S001");
  });

  test("packed-ascii pads short tags with @ and strips them", () => {
    const packed = packedAsciiToBytes("5850S");
    expect(packed).toHaveLength(6);
    expect(packedAsciiFromBytes(packed)).toBe("5850S");
  });
});