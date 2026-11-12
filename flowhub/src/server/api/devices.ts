import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";
import { requireAuth, requireAdmin } from "../middleware/auth";
import {
  updateDevice,
  getDeviceInfo,
} from "../db";
import { recordAudit } from "../audit";
import { z } from "zod";

const setpointSchema = z.object({
  value: z.number().finite(),
  unit: z.enum(["percent", "engineering"]),
});

const valveOverrideSchema = z.object({
  mode: z.enum(["normal", "open", "closed"]),
});

const configSchema = z.object({
  gas: z.string().optional(),
  flowUnit: z.number().int().optional(),
  tempUnit: z.number().int().optional(),
  alarmHigh: z.number().optional(),
  alarmLow: z.number().optional(),
  pid: z.string().optional(),
  softstart: z.enum(["disabled", "linear"]).optional(),
  valveRange: z.number().optional(),
  valveOffset: z.number().optional(),
  setpointSource: z.enum(["analog", "digital"]).optional(),
  writeProtect: z.boolean().optional(),
});

const devicePatchSchema = z.object({
  name: z.string().min(1).optional(),
  enabled: z.boolean().optional(),
  pollIntervalMs: z.number().int().min(250).max(60_000).optional(),
});

export const devicesRoutes = new Hono<{ Variables: AppVariables }>();

devicesRoutes.use("*", requireAuth);

devicesRoutes.get("/", async (c: AppContext) => {
  const engine = c.get("pollEngine");
  return c.json({ devices: engine.snapshots() });
});

devicesRoutes.get("/:id", async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const db = c.get("db");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  const snapshots = engine.snapshots();
  const device = snapshots.find((d) => d.id === id);
  if (!device) return c.json({ error: "not_found" }, 404);
  const info = getDeviceInfo(db, id);
  return c.json({ device, info });
});

devicesRoutes.patch("/:id", requireAdmin, async (c: AppContext) => {
  const db = c.get("db");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  let input: z.infer<typeof devicePatchSchema>;
  try {
    input = devicePatchSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const { userId, username: actor, role: actorRole } = authenticated(c);
  const existing = db
    .query<{ id: number; name: string; enabled: number; poll_interval_ms: number | null }, [number]>(
      "SELECT id, name, enabled, poll_interval_ms FROM devices WHERE id = ?",
    )
    .get(id);
  if (!existing) return c.json({ error: "not_found" }, 404);
  updateDevice(db, id, input);
  recordAudit(db, {
    userId,
    username: actor,
    role: actorRole,
    action: "device.update",
    deviceId: String(id),
    oldValue: { name: existing.name, enabled: existing.enabled === 1, poll_interval_ms: existing.poll_interval_ms },
    newValue: {
      name: input.name ?? existing.name,
      enabled: input.enabled !== undefined ? input.enabled : existing.enabled === 1,
      poll_interval_ms: input.pollIntervalMs ?? existing.poll_interval_ms,
    },
    success: true,
    detail: `Updated device settings`,
  });
  return c.json({ ok: true });
});

devicesRoutes.post("/:id/setpoint", async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const db = c.get("db");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  let input: z.infer<typeof setpointSchema>;
  try {
    input = setpointSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const { userId, username: actor, role: actorRole } = authenticated(c);
  try {
    const result = await engine.writeSetpoint(id, {
      value: input.value,
      unit: input.unit,
    });
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.setpoint",
      deviceId: String(id),
      newValue: { value: input.value, unit: input.unit },
      success: true,
      detail: `Setpoint written to ${input.value} ${input.unit}`,
    });
    return c.json(result);
  } catch (error) {
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.setpoint",
      deviceId: String(id),
      newValue: { value: input.value, unit: input.unit },
      success: false,
      detail: error instanceof Error ? error.message : String(error),
    });
    return c.json({ error: error instanceof Error ? error.message : "write_failed" }, 400);
  }
});

devicesRoutes.post("/:id/valve-override", async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const db = c.get("db");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  let input: z.infer<typeof valveOverrideSchema>;
  try {
    input = valveOverrideSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const { userId, username: actor, role: actorRole } = authenticated(c);
  try {
    const result = await engine.writeValveOverride(id, input.mode);
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.valve_override",
      deviceId: String(id),
      newValue: input.mode,
      success: true,
      detail: `Valve override set to ${input.mode}`,
    });
    return c.json(result);
  } catch (error) {
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.valve_override",
      deviceId: String(id),
      newValue: input.mode,
      success: false,
      detail: error instanceof Error ? error.message : String(error),
    });
    return c.json({ error: error instanceof Error ? error.message : "write_failed" }, 400);
  }
});

devicesRoutes.post("/:id/config", requireAdmin, async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const db = c.get("db");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  let input: z.infer<typeof configSchema>;
  try {
    input = configSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const { userId, username: actor, role: actorRole } = authenticated(c);
  try {
    await engine.writeDeviceConfig(id, {
      flowUnit: input.flowUnit,
      tempUnit: input.tempUnit,
      setpointSource: input.setpointSource === "digital" ? 3 : input.setpointSource === "analog" ? 1 : undefined,
      writeProtect: input.writeProtect,
    });
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.config",
      deviceId: String(id),
      newValue: input,
      success: true,
      detail: "Device configuration updated",
    });
    return c.json({ ok: true });
  } catch (error) {
    recordAudit(db, {
      userId,
      username: actor,
      role: actorRole,
      action: "device.config",
      deviceId: String(id),
      newValue: input,
      success: false,
      detail: error instanceof Error ? error.message : String(error),
    });
    return c.json({ error: error instanceof Error ? error.message : "write_failed" }, 400);
  }
});

devicesRoutes.post("/:id/refresh", requireAdmin, async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  try {
    await engine.refreshDeviceById(id);
    return c.json({ ok: true, refreshed: id });
  } catch (error) {
    return c.json({ error: error instanceof Error ? error.message : "refresh_failed" }, 400);
  }
});

function authenticated(c: AppContext): { userId: number; username: string; role: string } {
  const db = c.get("db");
  const userId = c.get("userId");
  if (userId === undefined) throw new Error("not authenticated");
  const user = db
    .query<{ id: number; username: string; role: string }, [number]>("SELECT id, username, role FROM users WHERE id = ?")
    .get(userId);
  if (!user) throw new Error("not authenticated");
  return { userId, username: user.username, role: user.role };
}
