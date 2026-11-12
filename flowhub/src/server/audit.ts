import type { Database } from "bun:sqlite";
import { nowIso } from "./db";

export type AuditEntry = {
  userId?: number | null;
  username: string;
  role: string;
  action: string;
  deviceId?: string | null;
  field?: string | null;
  oldValue?: unknown;
  newValue?: unknown;
  success: boolean;
  detail?: string | null;
};

function stringify(value: unknown): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export function recordAudit(db: Database, entry: AuditEntry): void {
  db.run(
    `INSERT INTO audit
      (ts, user_id, username, role, action, device_id, field, old_value, new_value, success, detail)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      nowIso(),
      entry.userId ?? null,
      entry.username,
      entry.role,
      entry.action,
      entry.deviceId ?? null,
      entry.field ?? null,
      stringify(entry.oldValue),
      stringify(entry.newValue),
      entry.success ? 1 : 0,
      entry.detail ?? null,
    ],
  );
}