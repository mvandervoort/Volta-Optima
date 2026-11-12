import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";
import { requireAuth, requireAdmin } from "../middleware/auth";
import { listAudit } from "../db";

export const auditRoutes = new Hono<{ Variables: AppVariables }>();

auditRoutes.use("*", requireAuth, requireAdmin);

auditRoutes.get("/", async (c: AppContext) => {
  const db = c.get("db");
  const limit = c.req.query("limit");
  const deviceId = c.req.query("deviceId");
  const parsedLimit = limit !== undefined ? Number(limit) : undefined;
  if (parsedLimit !== undefined && !Number.isFinite(parsedLimit)) {
    return c.json({ error: "invalid_request" }, 400);
  }
  const rows = listAudit(db, { limit: parsedLimit, deviceId: deviceId ?? undefined });
  return c.json({ audit: rows });
});

auditRoutes.get("/export.csv", async (c: AppContext) => {
  const db = c.get("db");
  const rows = listAudit(db, { limit: 10_000 });
  const lines = ["ts,username,role,action,device_id,field,old_value,new_value,success,detail"];
  for (const row of rows) {
    const csv = (v: unknown) => {
      if (v === null || v === undefined) return "";
      const s = String(v);
      if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
      return s;
    };
    lines.push([
      csv(row.ts),
      csv(row.username),
      csv(row.role),
      csv(row.action),
      csv(row.device_id),
      csv(row.field),
      csv(row.old_value),
      csv(row.new_value),
      csv(row.success),
      csv(row.detail),
    ].join(","));
  }
  c.header("Content-Type", "text/csv; charset=utf-8");
  c.header("Content-Disposition", 'attachment; filename="audit.csv"');
  return c.body(lines.join("\n"));
});
