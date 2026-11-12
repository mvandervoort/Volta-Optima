import { Database } from "bun:sqlite";
import { runMigrations } from "./db/migrate";

export type UserRole = "operator" | "admin";

export type UserRow = {
  id: number;
  username: string;
  password_hash: string;
  role: UserRole;
  active: number;
  created_at: string;
  last_login: string | null;
};

export type DeviceRow = {
  id: number;
  config_id: string;
  name: string;
  enabled: number;
  poll_interval_ms: number;
  created_at: string;
  updated_at: string;
};

export type AuditRow = {
  id: number;
  ts: string;
  user_id: number | null;
  username: string;
  role: string;
  action: string;
  device_id: string | null;
  field: string | null;
  old_value: string | null;
  new_value: string | null;
  success: number;
  detail: string | null;
};

export function openDatabase(path: string): Database {
  const db = new Database(path, { create: true });
  db.exec("PRAGMA journal_mode = WAL;");
  db.exec("PRAGMA foreign_keys = ON;");
  runMigrations(db);
  return db;
}

export function nowIso(): string {
  return new Date().toISOString();
}

export function getUserByUsername(db: Database, username: string): UserRow | null {
  return db
    .query<UserRow, [string]>("SELECT * FROM users WHERE username = ?")
    .get(username);
}

export function getUserById(db: Database, id: number): UserRow | null {
  return db.query<UserRow, [number]>("SELECT * FROM users WHERE id = ?").get(id);
}

export function listUsers(db: Database): UserRow[] {
  return db
    .query<UserRow, []>("SELECT * FROM users ORDER BY username")
    .all();
}

export function createUser(
  db: Database,
  input: { username: string; passwordHash: string; role: UserRole },
): UserRow {
  const ts = nowIso();
  db.run(
    "INSERT INTO users (username, password_hash, role, active, created_at) VALUES (?, ?, ?, 1, ?)",
    [input.username, input.passwordHash, input.role, ts],
  );
  return getUserByUsername(db, input.username)!;
}

export function setUserActive(db: Database, id: number, active: boolean): void {
  db.run("UPDATE users SET active = ? WHERE id = ?", [active ? 1 : 0, id]);
}

export function setUserRole(db: Database, id: number, role: UserRole): void {
  db.run("UPDATE users SET role = ? WHERE id = ?", [role, id]);
}

export function touchLastLogin(db: Database, id: number): void {
  db.run("UPDATE users SET last_login = ? WHERE id = ?", [nowIso(), id]);
}

export function ensureDevices(db: Database, configDevices: { id: string; initialName: string }[]): void {
  const ts = nowIso();
  for (const device of configDevices) {
    const existing = db
      .query<DeviceRow, [string]>("SELECT * FROM devices WHERE config_id = ?")
      .get(device.id);
    if (!existing) {
      db.run(
        "INSERT INTO devices (config_id, name, enabled, created_at, updated_at) VALUES (?, ?, 1, ?, ?)",
        [device.id, device.initialName, ts, ts],
      );
    }
  }
}

export function listDevices(db: Database): DeviceRow[] {
  return db
    .query<DeviceRow, []>("SELECT * FROM devices ORDER BY config_id")
    .all();
}

export function updateDevice(
  db: Database,
  id: number,
  input: { name?: string; enabled?: boolean; pollIntervalMs?: number },
): void {
  const fields: string[] = [];
  const values: (string | number)[] = [];
  if (input.name !== undefined) {
    fields.push("name = ?");
    values.push(input.name);
  }
  if (input.enabled !== undefined) {
    fields.push("enabled = ?");
    values.push(input.enabled ? 1 : 0);
  }
  if (input.pollIntervalMs !== undefined) {
    fields.push("poll_interval_ms = ?");
    values.push(input.pollIntervalMs);
  }
  if (fields.length === 0) return;
  fields.push("updated_at = ?");
  values.push(nowIso());
  values.push(id);
  db.run(`UPDATE devices SET ${fields.join(", ")} WHERE id = ?`, values);
}

export type DeviceInfoRow = {
  device_id: number;
  model: string | null;
  serial: string | null;
  tag: string | null;
  firmware: string | null;
  hardware: string | null;
  manufacturer_id: number | null;
  device_type_code: number | null;
  refreshed_at: string;
};

export function getDeviceInfo(db: Database, deviceId: number): DeviceInfoRow | null {
  return db
    .query<DeviceInfoRow, [number]>("SELECT * FROM device_info WHERE device_id = ?")
    .get(deviceId);
}

export function cacheDeviceInfo(
  db: Database,
  deviceId: number,
  info: Omit<DeviceInfoRow, "device_id" | "refreshed_at">,
): void {
  db.run(
    `INSERT INTO device_info
      (device_id, model, serial, tag, firmware, hardware, manufacturer_id, device_type_code, refreshed_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(device_id) DO UPDATE SET
      model = excluded.model, serial = excluded.serial, tag = excluded.tag,
      firmware = excluded.firmware, hardware = excluded.hardware,
      manufacturer_id = excluded.manufacturer_id, device_type_code = excluded.device_type_code,
      refreshed_at = excluded.refreshed_at`,
    [
      deviceId,
      info.model,
      info.serial,
      info.tag,
      info.firmware,
      info.hardware,
      info.manufacturer_id,
      info.device_type_code,
      nowIso(),
    ],
  );
}

export type DeviceState = {
  device_id: number;
  flow: number | null;
  unit: string | null;
  setpoint: number | null;
  setpoint_unit: string | null;
  valve_position: number | null;
  temperature: number | null;
  totalizer: number | null;
  status_bits: number | null;
  online: number;
  last_seen: string | null;
  updated_at: string;
};

export function getDeviceState(db: Database, deviceId: number): DeviceState | null {
  return db
    .query<DeviceState, [number]>("SELECT * FROM device_state WHERE device_id = ?")
    .get(deviceId);
}

export function listDeviceStates(db: Database): DeviceState[] {
  return db.query<DeviceState, []>("SELECT * FROM device_state").all();
}

export function upsertDeviceState(
  db: Database,
  deviceId: number,
  state: Omit<DeviceState, "device_id" | "updated_at">,
): void {
  db.run(
    `INSERT INTO device_state
      (device_id, flow, unit, setpoint, setpoint_unit, valve_position, temperature,
       totalizer, status_bits, online, last_seen, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(device_id) DO UPDATE SET
      flow = excluded.flow, unit = excluded.unit, setpoint = excluded.setpoint,
      setpoint_unit = excluded.setpoint_unit, valve_position = excluded.valve_position,
      temperature = excluded.temperature, totalizer = excluded.totalizer,
      status_bits = excluded.status_bits, online = excluded.online,
      last_seen = excluded.last_seen, updated_at = excluded.updated_at`,
    [
      deviceId,
      state.flow,
      state.unit,
      state.setpoint,
      state.setpoint_unit,
      state.valve_position,
      state.temperature,
      state.totalizer,
      state.status_bits,
      state.online,
      state.last_seen,
      nowIso(),
    ],
  );
}

export function markDeviceOffline(db: Database, deviceId: number): void {
  db.run(
    `INSERT INTO device_state (device_id, online, updated_at) VALUES (?, 0, ?)
     ON CONFLICT(device_id) DO UPDATE SET online = 0, updated_at = excluded.updated_at`,
    [deviceId, nowIso()],
  );
}

export function listAudit(
  db: Database,
  opts: { limit?: number; deviceId?: string | null },
): AuditRow[] {
  let sql = "SELECT * FROM audit";
  const params: (string | number)[] = [];
  const clauses: string[] = [];
  if (opts.deviceId) {
    clauses.push("device_id = ?");
    params.push(opts.deviceId);
  }
  if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
  sql += " ORDER BY id DESC";
  if (opts.limit !== undefined) {
    sql += " LIMIT ?";
    params.push(opts.limit);
  }
  return db.query<AuditRow, (string | number)[]>(sql).all(...params);
}