import { createServer, type Socket } from "node:net";
import {
  PREAMBLE,
  START_LONG_MASTER,
  START_LONG_SLAVE,
  START_SHORT_MASTER,
  START_SHORT_SLAVE,
  decodeFloat,
  encodeFloat,
  xorChecksum,
} from "../../src/server/bus/sProtocol";

type DeviceState = {
  setpoint: number;
  valveOverride: number;
  valvePosition: number;
  flowUnit: number;
  tempUnit: number;
};

const PORT = Number(process.env.FLOWHUB_SIM_PORT ?? process.argv[2] ?? 1111);
const SHORT_ADDRESS = Number(process.env.FLOWHUB_SIM_ADDRESS ?? 1);

const OK: [number, number] = [0x00, 0x00];
const NOT_SUPPORTED: [number, number] = [0x80, 0x00];

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

function withUnit(unit: number, value: number): Uint8Array {
  const payload = new Uint8Array(5);
  payload[0] = unit;
  payload.set(encodeFloat(value), 1);
  return payload;
}

function dispatch(
  command: number,
  data: Uint8Array,
  state: DeviceState,
): { payload: Uint8Array; status: [number, number] } {
  switch (command) {
    case 1:
    case 2:
      return { payload: withUnit(state.flowUnit, 25), status: OK };
    case 3: {
      const payload = new Uint8Array(14);
      payload.set(encodeFloat(25), 0);
      payload.set(encodeFloat(22.5), 10);
      return { payload, status: OK };
    }
    case 11:
      return { payload: Uint8Array.of(0x00, 0x0a, 0x01, 0x02, 0x03, 0x04, 0x01, 0x00), status: OK };
    case 13:
      return { payload: Uint8Array.from(Buffer.from("SIM-MFC-1", "ascii")), status: OK };
    case 150:
      return { payload: Uint8Array.of(1), status: OK };
    case 152:
      return { payload: encodeFloat(100), status: OK };
    case 195:
      return { payload: Uint8Array.of(1), status: OK };
    case 196:
      return { payload: Uint8Array.of(state.flowUnit), status: OK };
    case 197:
      return { payload: Uint8Array.of(state.tempUnit), status: OK };
    case 230:
      return { payload: Uint8Array.of(state.valveOverride), status: OK };
    case 231:
      if (data.length < 1) return { payload: new Uint8Array(), status: NOT_SUPPORTED };
      state.valveOverride = data[0]!;
      return { payload: new Uint8Array(), status: OK };
    case 235: {
      const payload = new Uint8Array(6);
      payload.set(encodeFloat(state.setpoint), 1);
      payload[5] = state.flowUnit;
      return { payload, status: OK };
    }
    case 236:
      if (data.length < 5) return { payload: new Uint8Array(), status: NOT_SUPPORTED };
      state.flowUnit = data[0]!;
      state.setpoint = decodeFloat(data, 1);
      return { payload: new Uint8Array(), status: OK };
    case 237:
      return { payload: encodeFloat(state.valvePosition), status: OK };
    case 128:
      return { payload: new Uint8Array(), status: NOT_SUPPORTED };
    default:
      return { payload: new Uint8Array(), status: NOT_SUPPORTED };
  }
}

const state: DeviceState = {
  setpoint: 85,
  valveOverride: 0,
  valvePosition: 100,
  flowUnit: 57,
  tempUnit: 1,
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