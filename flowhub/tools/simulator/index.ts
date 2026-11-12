import { createServer, type Socket } from "node:net";
import {
  PREAMBLE,
  START_LONG_MASTER,
  START_LONG_SLAVE,
  START_SHORT_MASTER,
  START_SHORT_SLAVE,
  decodeFloat,
  encodeFloat,
  encodeUint24,
  xorChecksum,
} from "../../src/server/bus/sProtocol";

type DeviceState = {
  flowReference: number;
  flowUnit: number;
  tempUnit: number;
  fullScale: number;
  gasType: number;
  setpointPercent: number;
  setpointSource: number;
  valveOverride: number;
  valveControl: number;
};

const PORT = Number(process.env.FLOWHUB_SIM_PORT ?? process.argv[2] ?? 1111);
const SHORT_ADDRESS = Number(process.env.FLOWHUB_SIM_ADDRESS ?? 1);

const OK: [number, number] = [0x00, 0x00];
const NOT_SUPPORTED: [number, number] = [0x80, 0x00];

const DEVICE_ID = 0x010203;
const MANUFACTURER_ID = 10;
const DEVICE_TYPE_CODE = 90;

function identity(): Uint8Array {
  return Uint8Array.of(
    254,
    MANUFACTURER_ID,
    DEVICE_TYPE_CODE,
    5,
    1,
    1,
    3,
    2,
    0,
    (DEVICE_ID >>> 16) & 0xff,
    (DEVICE_ID >>> 8) & 0xff,
    DEVICE_ID & 0xff,
  );
}

function setpointPayload(state: DeviceState): Uint8Array {
  const payload = new Uint8Array(10);
  payload[0] = 57;
  payload.set(encodeFloat(state.setpointPercent), 1);
  payload[5] = state.flowUnit;
  payload.set(encodeFloat(scaledFromPercent(state)), 6);
  return payload;
}

function scaledFromPercent(state: DeviceState): number {
  return (state.setpointPercent / 100) * state.fullScale;
}

function percentFromScaled(state: DeviceState, scaled: number): number {
  if (state.fullScale === 0) return 0;
  return (scaled / state.fullScale) * 100;
}

function buildResponse(
  address: Uint8Array,
  long: boolean,
  command: number,
  status: [number, number],
  data: Uint8Array = new Uint8Array(),
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
  body[offset++] = status[0];
  body[offset++] = status[1];
  body.set(data, offset);

  const frame = new Uint8Array(5 + bodyLength + 1);
  frame.fill(PREAMBLE, 0, 5);
  frame.set(body, 5);
  frame[frame.length - 1] = xorChecksum(body);
  return frame;
}

function handleRequest(buffer: Uint8Array, state: DeviceState): Uint8Array | null {
  let index = 0;
  while (index + 5 < buffer.length) {
    let isPreamble = true;
    for (let i = 0; i < 5; i += 1) {
      if (buffer[index + i] !== PREAMBLE) {
        isPreamble = false;
        break;
      }
    }
    if (isPreamble) break;
    index += 1;
  }
  if (index + 5 >= buffer.length) return null;

  const start = buffer[index + 5]!;
  const long = start === START_LONG_MASTER;
  const short = start === START_SHORT_MASTER;
  if (!long && !short) return null;

  const addressLength = long ? 5 : 1;
  const commandIndex = index + 5 + 1 + addressLength;
  if (buffer.length < commandIndex + 2) return null;

  const address = buffer.slice(index + 5 + 1, commandIndex);
  const command = buffer[commandIndex]!;
  const data = buffer.slice(commandIndex + 1, buffer.length - 1);

  const body = buffer.slice(index + 5, buffer.length - 1);
  if (xorChecksum(body) !== buffer[buffer.length - 1]) return null;

  const target = long ? address : Uint8Array.of(SHORT_ADDRESS);
  if (!long && address[0] !== SHORT_ADDRESS) return null;

  const { payload, status } = dispatch(command, data, state);
  return buildResponse(target, long, command, status, payload);
}

function dispatch(
  command: number,
  data: Uint8Array,
  state: DeviceState,
): { payload: Uint8Array; status: [number, number] } {
  switch (command) {
    case 0:
    case 11:
      return { payload: identity(), status: OK };

    case 1:
      return { payload: withUnit(state.flowUnit, scaledFromPercent(state)), status: OK };

    case 2: {
      const payload = new Uint8Array(13);
      payload[0] = state.flowUnit;
      payload.set(encodeFloat(scaledFromPercent(state)), 1);
      payload.set(encodeFloat(4), 5);
      payload.set(encodeFloat(state.setpointPercent), 9);
      return { payload, status: OK };
    }

    case 3: {
      const payload = new Uint8Array(14);
      payload.set(encodeFloat(4), 0);
      payload[4] = state.flowUnit;
      payload.set(encodeFloat(scaledFromPercent(state)), 5);
      payload[9] = state.tempUnit;
      payload.set(encodeFloat(22.5), 10);
      return { payload, status: OK };
    }

    case 13: {
      const tag = Buffer.from("SIM01@", "ascii");
      const descriptor = Buffer.from("FLOWHUB-SIM ", "ascii");
      const payload = new Uint8Array(21);
      payload.set(tag.subarray(0, 6), 0);
      payload.set(descriptor.subarray(0, 12), 6);
      payload.set([24, 11, 12], 18);
      return { payload, status: OK };
    }

    case 150:
      return { payload: Uint8Array.of(state.gasType), status: OK };

    case 152:
      return { payload: encodeFloat(state.fullScale), status: OK };

    case 195:
      return { payload: Uint8Array.of(state.gasType), status: OK };

    case 196:
      if (data.length >= 2) {
        state.flowReference = data[0]!;
        state.flowUnit = data[1]!;
      }
      return { payload: Uint8Array.of(state.flowReference, state.flowUnit), status: OK };

    case 197:
      if (data.length >= 1) state.tempUnit = data[0]!;
      return { payload: Uint8Array.of(state.tempUnit), status: OK };

    case 215:
      return { payload: Uint8Array.of(state.setpointSource), status: OK };

    case 216:
      if (data.length >= 1) state.setpointSource = data[0]!;
      return { payload: Uint8Array.of(state.setpointSource), status: OK };

    case 230:
      return { payload: Uint8Array.of(state.valveOverride), status: OK };

    case 231:
      if (data.length < 1) return { payload: new Uint8Array(), status: NOT_SUPPORTED };
      state.valveOverride = data[0]!;
      return { payload: Uint8Array.of(state.valveOverride), status: OK };

    case 235:
      return { payload: setpointPayload(state), status: OK };

    case 236: {
      if (data.length < 5) return { payload: new Uint8Array(), status: NOT_SUPPORTED };
      const unitCode = data[0]!;
      const value = decodeFloat(data, 1);
      if (unitCode === 57) {
        state.setpointPercent = value;
      } else {
        state.setpointPercent = percentFromScaled(state, value);
      }
      return { payload: setpointPayload(state), status: OK };
    }

    case 237:
      return { payload: encodeUint24(state.valveControl), status: OK };

    case 128:
      return { payload: new Uint8Array(), status: NOT_SUPPORTED };

    default:
      return { payload: new Uint8Array(), status: NOT_SUPPORTED };
  }
}

function withUnit(unit: number, value: number): Uint8Array {
  const payload = new Uint8Array(5);
  payload[0] = unit;
  payload.set(encodeFloat(value), 1);
  return payload;
}

const state: DeviceState = {
  flowReference: 0,
  flowUnit: 17,
  tempUnit: 1,
  fullScale: 100,
  gasType: 1,
  setpointPercent: 85,
  setpointSource: 3,
  valveOverride: 0,
  valveControl: 1000,
};

const server = createServer((socket: Socket) => {
  console.log(`simulator: client connected (${socket.remoteAddress})`);
  let pending = new Uint8Array(0);

  socket.on("data", (chunk: Buffer) => {
    const combined = new Uint8Array(pending.length + chunk.length);
    combined.set(pending, 0);
    combined.set(chunk, pending.length);
    pending = combined;

    const response = handleRequest(pending, state);
    if (response) {
      socket.write(response);
      pending = new Uint8Array(0);
    }
  });

  socket.on("error", (error) => {
    console.error(`simulator: socket error: ${error.message}`);
  });

  socket.on("close", () => {
    console.log("simulator: client disconnected");
  });
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`simulator: listening on port ${PORT} (short address ${SHORT_ADDRESS})`);
});