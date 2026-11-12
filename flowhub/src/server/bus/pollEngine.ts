import type { Database } from "bun:sqlite";
import {
  buildRequest,
  decodeFloat,
  decodeIdentity,
  decodeSetpoint,
  decodeUint8,
  decodeUint24,
  CMD,
  encodeFloat,
  encodeUint8,
} from "./sProtocol";
import { parseAddress, type Config, type ParsedAddress } from "../config";
import { ConverterConnection, type ConnectionState } from "./tcp";
import { log } from "../log";
import {
  cacheDeviceInfo,
  ensureDevices,
  getDeviceState,
  listDeviceStates,
  listDevices,
  markDeviceOffline,
  setDeviceSetpointSource,
  upsertDeviceState,
  type DeviceRow,
  type DeviceState,
} from "../db";

export type DeviceStatus = "online" | "stale" | "offline" | "fault";

export type DeviceSnapshot = {
  id: number;
  configId: string;
  name: string;
  address: string;
  enabled: boolean;
  online: boolean;
  status: DeviceStatus;
  flow: number | null;
  unit: string | null;
  setpoint: number | null;
  setpointUnit: string | null;
  setpointScaled: number | null;
  flowUnit: string | null;
  setpointSource: "analog" | "digital" | "unknown";
  valvePosition: number | null;
  temperature: number | null;
  totalizer: number | null;
  statusBits: number | null;
  lastSeen: string | null;
};

type RuntimeDevice = {
  row: DeviceRow;
  address: ParsedAddress;
  consecutiveFailures: number;
  nextPollAt: number;
};

export type PollResult = {
  deviceId: number;
  configId: string;
  ok: boolean;
  error?: string;
  durationMs: number;
};

export type PollEngineEvents = {
  onState?: (devices: DeviceSnapshot[]) => void;
  onConnection?: (state: ConnectionState) => void;
};

const REQUEST_TIMEOUT_MS = 500;
const MAX_FAILURES = 3;
const STALE_AFTER_MS = 3000;
const PERCENT_UNIT_CODE = 57;

/**
 * Owns the single RS-485 master connection and polls configured devices
 * sequentially. Only one transaction is outstanding at a time; a per-cycle
 * time budget ensures one slow device cannot block the whole cycle.
 */
export class PollEngine {
  private readonly connection: ConverterConnection;
  private readonly devices = new Map<number, RuntimeDevice>();
  private timer: ReturnType<typeof setTimeout> | null = null;
  private running = false;
  private lastPollAt: string | null = null;
  private connectionState: ConnectionState = "offline";

  constructor(
    private readonly db: Database,
    private readonly config: Config,
    private readonly events: PollEngineEvents = {},
  ) {
    this.connection = new ConverterConnection(
      config.converter.host,
      config.converter.port,
      (state) => {
        this.connectionState = state;
        this.events.onConnection?.(state);
      },
    );
  }

  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  getLastPollAt(): string | null {
    return this.lastPollAt;
  }

  async start(): Promise<void> {
    if (this.running) return;
    ensureDevices(
      this.db,
      this.config.bus.devices.map((d) => ({ id: d.id, initialName: d.initialName })),
    );
    this.reloadDevices();
    this.running = true;
    await this.connection.connect().catch((error: unknown) => {
      log("error", "converter_connect_failed", {
        error: error instanceof Error ? error.message : String(error),
      });
    });
    void this.refreshAllDevices();
    this.schedule(0);
  }

  private async refreshAllDevices(): Promise<void> {
    for (const device of this.devices.values()) {
      if (!device.row.enabled) continue;
      try {
        await this.refreshDevice(device);
      } catch {
        // Identiteit is optioneel; een device dat dit niet ondersteunt blijft bruikbaar.
      }
    }
  }

  stop(): void {
    this.running = false;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    void this.connection.close().catch(() => {});
  }

  reloadDevices(): void {
    this.devices.clear();
    for (const row of listDevices(this.db)) {
      const cfg = this.config.bus.devices.find((d) => d.id === row.config_id);
      if (!cfg) continue;
      let address: ParsedAddress;
      try {
        address = parseAddress(cfg.address);
      } catch (error) {
        log("error", "device_address_invalid", {
          configId: row.config_id,
          address: cfg.address,
          error: error instanceof Error ? error.message : String(error),
        });
        continue;
      }
      this.devices.set(row.id, {
        row,
        address,
        consecutiveFailures: 0,
        nextPollAt: 0,
      });
    }
  }

  private pollIntervalFor(device: RuntimeDevice): number {
    const configured = device.row.poll_interval_ms;
    if (typeof configured === "number" && configured > 0) return configured;
    return this.config.bus.pollIntervalMs;
  }

  private scheduleDelay(): number {
    let interval = this.config.bus.pollIntervalMs;
    for (const device of this.devices.values()) {
      interval = Math.min(interval, this.pollIntervalFor(device));
    }
    return Math.max(250, interval);
  }

  private schedule(delayMs: number): void {
    if (!this.running) return;
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      this.timer = null;
      void this.cycle();
    }, delayMs);
  }

  private async cycle(): Promise<void> {
    const budgetStart = Date.now();
    const budgetMs = this.scheduleDelay();
    for (const device of this.devices.values()) {
      if (!device.row.enabled) continue;
      if (device.nextPollAt > Date.now()) continue;
      if (Date.now() - budgetStart >= budgetMs) break;
      await this.pollDevice(device);
      device.nextPollAt = Date.now() + this.pollIntervalFor(device);
    }
    this.lastPollAt = new Date().toISOString();
    this.events.onState?.(this.snapshots());
    this.schedule(Math.max(0, budgetMs - (Date.now() - budgetStart)));
  }

  async pollDevice(device: RuntimeDevice): Promise<PollResult> {
    const start = Date.now();
    if (this.connectionState !== "online") {
      this.setOffline(device.row.id);
      return {
        deviceId: device.row.id,
        configId: device.row.config_id,
        ok: false,
        error: "offline",
        durationMs: 0,
      };
    }
    try {
      const flow = await this.readFlow(device);
      const setpoint = await this.readSetpoint(device);
      const temperature = await this.readTemperature(device);
      const valve = await this.readValveControl(device);
      upsertDeviceState(this.db, device.row.id, {
        flow: flow.value,
        unit: flow.unit,
        setpoint: setpoint.percent,
        setpoint_unit: unitName(PERCENT_UNIT_CODE),
        setpoint_scaled: setpoint.scaled,
        flow_unit_code: setpoint.flowUnitCode,
        valve_position: valve,
        temperature,
        totalizer: null,
        status_bits: null,
        online: 1,
        last_seen: new Date().toISOString(),
      });
      device.consecutiveFailures = 0;
      return {
        deviceId: device.row.id,
        configId: device.row.config_id,
        ok: true,
        durationMs: Date.now() - start,
      };
    } catch (error) {
      device.consecutiveFailures += 1;
      const message = error instanceof Error ? error.message : String(error);
      if (device.consecutiveFailures >= MAX_FAILURES) this.setOffline(device.row.id);
      return {
        deviceId: device.row.id,
        configId: device.row.config_id,
        ok: false,
        error: message,
        durationMs: Date.now() - start,
      };
    }
  }

  private async transaction(
    device: RuntimeDevice,
    command: number,
    data?: Uint8Array,
  ): Promise<Uint8Array> {
    const address =
      device.address.kind === "short" ? device.address.value : device.address.value;
    const frame = buildRequest(address, command, data);
    const response = await this.connection.request(frame, REQUEST_TIMEOUT_MS);
    if (response.status[0]! !== 0) {
      throw new Error(`Command #${command} device status ${response.status[0]!.toString(16)}`);
    }
    return response.data;
  }

  /** Writes get a short retry; a single missed turnaround must not fail a setpoint change. */
  private async writeTransaction(
    device: RuntimeDevice,
    command: number,
    data?: Uint8Array,
  ): Promise<Uint8Array> {
    let lastError: Error | null = null;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        return await this.transaction(device, command, data);
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        if (!/timeout|closed|not online/i.test(lastError.message)) throw lastError;
        await new Promise((resolve) => setTimeout(resolve, 150));
      }
    }
    throw lastError ?? new Error("write failed");
  }

  private async readFlow(device: RuntimeDevice): Promise<{ value: number | null; unit: string | null }> {
    const data = await this.transaction(device, CMD.READ_PRIMARY_VARIABLE);
    return { value: decodeFloat(data, 1), unit: unitName(decodeUint8(data, 0)) };
  }

  private async readSetpoint(device: RuntimeDevice): Promise<{
    percent: number;
    flowUnitCode: number;
    scaled: number;
  }> {
    const data = await this.transaction(device, CMD.READ_SETPOINT);
    return decodeSetpoint(data);
  }

  private async readTemperature(device: RuntimeDevice): Promise<number | null> {
    const data = await this.transaction(device, CMD.READ_DYNAMIC_VARIABLES);
    return decodeFloat(data, 10);
  }

  private async readValveControl(device: RuntimeDevice): Promise<number | null> {
    const data = await this.transaction(device, CMD.READ_VALVE_CONTROL);
    return decodeUint24(data, 0);
  }

  private async readFlowUnit(
    device: RuntimeDevice,
  ): Promise<{ flowReference: number; flowUnit: number }> {
    const data = await this.transaction(device, CMD.READ_FLOW_UNIT);
    return { flowReference: decodeUint8(data, 0), flowUnit: decodeUint8(data, 1) };
  }

  /** #215 is best-effort: the manual does not document its response layout. */
  private async readSetpointSource(device: RuntimeDevice): Promise<number | null> {
    try {
      const data = await this.transaction(device, CMD.READ_SETPOINT_SETTINGS);
      if (data.length < 1) return null;
      return decodeUint8(data, 0);
    } catch {
      return null;
    }
  }

  /** Refresh identity/config info and cache it in SQLite. */
  async refreshDevice(device: RuntimeDevice): Promise<void> {
    const data = await this.transaction(device, CMD.READ_UNIQUE_ID);
    const identity = decodeIdentity(data);
    cacheDeviceInfo(this.db, device.row.id, {
      model: `Brooks ${identity.deviceTypeCode}`,
      serial: String(identity.deviceId),
      tag: null,
      firmware: String(identity.softwareRevision),
      hardware: String(identity.hardwareRevision),
      manufacturer_id: identity.manufacturerId,
      device_type_code: identity.deviceTypeCode,
    });
    const source = await this.readSetpointSource(device);
    if (source !== null) setDeviceSetpointSource(this.db, device.row.id, source);
  }

  private getDevice(deviceId: number): RuntimeDevice {
    const device = this.devices.get(deviceId);
    if (!device) throw new Error(`Unknown device ${deviceId}`);
    return device;
  }

  /** Refresh identity/config info for a device by row id and cache it in SQLite. */
  async refreshDeviceById(deviceId: number): Promise<void> {
    const device = this.getDevice(deviceId);
    await this.refreshDevice(device);
  }

  /** Write setpoint (#236) then read back via #235/#237. */
  async writeSetpoint(
    deviceId: number,
    input: { value: number; unit: "percent" | "engineering" },
  ): Promise<{
    setpoint: number | null;
    setpointUnit: string | null;
    setpointScaled: number | null;
    valvePosition: number | null;
  }> {
    const device = this.getDevice(deviceId);
    const unitCode = input.unit === "percent" ? PERCENT_UNIT_CODE : 250;
    const data = new Uint8Array([unitCode, ...Array.from(encodeFloat(input.value))]);
    await this.writeTransaction(device, CMD.WRITE_SETPOINT, data);
    const setpoint = await this.readSetpoint(device);
    const valvePosition = await this.readValveControl(device);
    const existing = getDeviceState(this.db, device.row.id);
    upsertDeviceState(this.db, device.row.id, {
      flow: existing?.flow ?? null,
      unit: existing?.unit ?? null,
      setpoint: setpoint.percent,
      setpoint_unit: unitName(PERCENT_UNIT_CODE),
      setpoint_scaled: setpoint.scaled,
      flow_unit_code: setpoint.flowUnitCode,
      valve_position: valvePosition,
      temperature: existing?.temperature ?? null,
      totalizer: existing?.totalizer ?? null,
      status_bits: existing?.status_bits ?? null,
      online: existing?.online ?? 0,
      last_seen: existing?.last_seen ?? null,
    });
    return {
      setpoint: setpoint.percent,
      setpointUnit: unitName(PERCENT_UNIT_CODE),
      setpointScaled: setpoint.scaled,
      valvePosition,
    };
  }

  /** Write valve override (#231) then read back via #230. */
  async writeValveOverride(
    deviceId: number,
    mode: "normal" | "open" | "closed",
  ): Promise<{ code: number }> {
    const device = this.getDevice(deviceId);
    const code = mode === "normal" ? 0 : mode === "open" ? 1 : 2;
    await this.writeTransaction(device, CMD.WRITE_VALVE_OVERRIDE, encodeUint8(code));
    const data = await this.transaction(device, CMD.READ_VALVE_OVERRIDE);
    const readback = decodeUint8(data, 0);
    if (readback !== code) {
      throw new Error(`Valve override readback mismatch: expected ${code}, got ${readback}`);
    }
    return { code: readback };
  }

  /** Write device configuration with readback. Write-protect (#128) is not supported on 5850S. */
  async writeDeviceConfig(
    deviceId: number,
    input: {
      flowUnit?: number;
      tempUnit?: number;
      setpointSource?: number;
      writeProtect?: boolean;
    },
  ): Promise<void> {
    const device = this.getDevice(deviceId);
    if (input.writeProtect === true) {
      throw new Error("Write-protect (#128) is not supported on this device");
    }
    if (input.flowUnit !== undefined) {
      const current = await this.readFlowUnit(device);
      await this.writeTransaction(
        device,
        CMD.READ_FLOW_UNIT,
        Uint8Array.of(current.flowReference, input.flowUnit),
      );
      const after = await this.readFlowUnit(device);
      if (after.flowUnit !== input.flowUnit) {
        throw new Error(`Flow unit readback mismatch: expected ${input.flowUnit}, got ${after.flowUnit}`);
      }
    }
    if (input.tempUnit !== undefined) {
      await this.writeTransaction(device, CMD.READ_TEMPERATURE_UNIT, encodeUint8(input.tempUnit));
      const after = await this.transaction(device, CMD.READ_TEMPERATURE_UNIT);
      const readback = decodeUint8(after, 0);
      if (readback !== input.tempUnit) {
        throw new Error(`Temperature unit readback mismatch: expected ${input.tempUnit}, got ${readback}`);
      }
    }
    if (input.setpointSource !== undefined) {
      await this.writeTransaction(device, CMD.WRITE_SETPOINT_SOURCE, encodeUint8(input.setpointSource));
      setDeviceSetpointSource(this.db, device.row.id, input.setpointSource);
    }
  }

  private setOffline(deviceId: number): void {
    markDeviceOffline(this.db, deviceId);
    for (const device of this.devices.values()) {
      if (device.row.id === deviceId) device.consecutiveFailures = MAX_FAILURES;
    }
  }

  snapshots(): DeviceSnapshot[] {
    const states = new Map(listDeviceStates(this.db).map((s) => [s.device_id, s]));
    const out: DeviceSnapshot[] = [];
    for (const device of this.devices.values()) {
      const state = states.get(device.row.id);
      const lastSeen = state?.last_seen ?? null;
      out.push({
        id: device.row.id,
        configId: device.row.config_id,
        name: device.row.name,
        address: addressText(device.address),
        enabled: device.row.enabled === 1,
        online: (state?.online ?? 0) === 1,
        status: this.statusOf(device, state),
        flow: state?.flow ?? null,
        unit: state?.unit ?? null,
        setpoint: state?.setpoint ?? null,
        setpointUnit: state?.setpoint_unit ?? null,
        setpointScaled: state?.setpoint_scaled ?? null,
        flowUnit: state?.flow_unit_code != null ? unitName(state.flow_unit_code) : null,
        setpointSource: setpointSourceName(state?.setpoint_source ?? null),
        valvePosition: state?.valve_position ?? null,
        temperature: state?.temperature ?? null,
        totalizer: state?.totalizer ?? null,
        statusBits: state?.status_bits ?? null,
        lastSeen,
      });
    }
    return out;
  }

  private statusOf(
    device: RuntimeDevice,
    state: DeviceState | undefined,
  ): DeviceStatus {
    if (!state || (state.online === 0 && device.consecutiveFailures >= MAX_FAILURES)) {
      return "offline";
    }
    if (!state.last_seen) return "offline";
    if (Date.now() - new Date(state.last_seen).getTime() > STALE_AFTER_MS) return "stale";
    return "online";
  }
}

function addressText(address: ParsedAddress): string {
  if (address.kind === "short") return String(address.value);
  return Array.from(address.value)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function setpointSourceName(code: number | null): "analog" | "digital" | "unknown" {
  if (code === 1) return "analog";
  if (code === 3) return "digital";
  return "unknown";
}

function unitName(code: number): string {
  switch (code) {
    case 17:
      return "L/min";
    case 19:
      return "m3/h";
    case 24:
      return "L/s";
    case 28:
      return "m3/s";
    case 57:
      return "%";
    case 131:
      return "m3/min";
    case 138:
      return "L/h";
    case 170:
      return "mL/s";
    case 171:
      return "mL/min";
    case 172:
      return "mL/h";
    default:
      return `code:${code}`;
  }
}