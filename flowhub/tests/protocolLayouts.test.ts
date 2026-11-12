import { describe, expect, test } from "bun:test";
import {
  buildRequest,
  CMD,
  decodeIdentity,
  decodeSetpoint,
  decodeUint24,
  encodeFloat,
  encodeUint24,
  FrameParser,
  PREAMBLE,
  START_LONG_SLAVE,
  START_SHORT_SLAVE,
  xorChecksum,
} from "../src/server/bus/sProtocol";

function slaveResponse(
  command: number,
  data: Uint8Array,
  address = Uint8Array.of(1),
  long = false,
): Uint8Array {
  const start = long ? START_LONG_SLAVE : START_SHORT_SLAVE;
  const bodyLength = 1 + address.length + 1 + 1 + 2 + data.length;
  const body = new Uint8Array(bodyLength);
  let offset = 0;
  body[offset++] = start;
  body.set(address, offset);
  offset += address.length;
  body[offset++] = command;
  body[offset++] = 2 + data.length;
  body[offset++] = 0x00;
  body[offset++] = 0x00;
  body.set(data, offset);

  const frame = new Uint8Array(5 + bodyLength + 1);
  frame.fill(PREAMBLE, 0, 5);
  frame.set(body, 5);
  frame[frame.length - 1] = xorChecksum(body);
  return frame;
}

function setpointPayload(percent: number, flowUnit: number, scaled: number): Uint8Array {
  const payload = new Uint8Array(10);
  payload[0] = 57;
  payload.set(encodeFloat(percent), 1);
  payload[5] = flowUnit;
  payload.set(encodeFloat(scaled), 6);
  return payload;
}

describe("Documented response layouts", () => {
  test("#235 ten-byte layout splits percent and flow-unit value", () => {
    const reading = decodeSetpoint(setpointPayload(50, 17, 25));
    expect(reading.percent).toBeCloseTo(50, 5);
    expect(reading.flowUnitCode).toBe(17);
    expect(reading.scaled).toBeCloseTo(25, 5);
  });

  test("#0 twelve-byte identity layout", () => {
    const payload = Uint8Array.of(254, 10, 90, 5, 1, 1, 3, 2, 0, 0x01, 0x02, 0x03);
    const identity = decodeIdentity(payload);
    expect(identity.manufacturerId).toBe(10);
    expect(identity.deviceTypeCode).toBe(90);
    expect(identity.softwareRevision).toBe(3);
    expect(identity.hardwareRevision).toBe(2);
    expect(identity.deviceId).toBe(0x010203);
  });

  test("#237 valve control is a 24-bit value, not a float", () => {
    const payload = encodeUint24(1000);
    expect(payload.length).toBe(3);
    expect(decodeUint24(payload, 0)).toBe(1000);
    expect(decodeUint24(Uint8Array.of(0x0f, 0xff, 0xff))).toBe(0x0fffff);
  });
});

describe("Request layouts", () => {
  test("#196 select flow unit sends flow reference and unit", () => {
    const request = buildRequest(1, CMD.READ_FLOW_UNIT, Uint8Array.of(0, 17));
    expect(Array.from(request)).toEqual([0xff, 0xff, 0xff, 0xff, 0xff, 0x02, 0x01, 0xc4, 0x00, 0x11, 0xd6]);
    expect(request[9]).toBe(17);
  });

  test("#236 write setpoint keeps unit code and float", () => {
    const body = new Uint8Array([57, ...Array.from(encodeFloat(85))]);
    const request = buildRequest(1, CMD.WRITE_SETPOINT, body);
    expect(request[8]).toBe(57);
    expect(request.length).toBe(5 + 1 + 1 + 1 + 5 + 1);
  });
});

describe("Frame parsing of slave responses", () => {
  test("byteCount includes the two status bytes", () => {
    const frame = slaveResponse(CMD.READ_FLOW_UNIT, Uint8Array.of(0, 17));
    const parser = new FrameParser();
    const frames = parser.push(frame);
    expect(frames.length).toBe(1);
    expect(frames[0]!.command).toBe(CMD.READ_FLOW_UNIT);
    expect(Array.from(frames[0]!.data)).toEqual([0, 17]);
    expect(Array.from(frames[0]!.status)).toEqual([0, 0]);
  });

  test("long-frame response carries a five-byte address", () => {
    const address = Uint8Array.of(0x8a, 0x05, 0x3e, 0xeb, 0x09);
    const frame = slaveResponse(CMD.READ_SETPOINT, setpointPayload(85, 17, 42.5), address, true);
    const parser = new FrameParser();
    const frames = parser.push(frame);
    expect(frames.length).toBe(1);
    expect(Array.from(frames[0]!.address)).toEqual(Array.from(address));
    expect(decodeSetpoint(frames[0]!.data).percent).toBeCloseTo(85, 5);
  });
});