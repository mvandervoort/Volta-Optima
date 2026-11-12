import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";
import { requireAuth, requireAdmin } from "../middleware/auth";
import { listAudit } from "../db";

export const auditRoutes = new Hono<{ Variables: AppVariables }>();

auditRoutes.use("*", requireAuth, requireAdmin);

const MAX_LIMIT = 500;

auditRoutes.get("/", async (c: AppContext) => {
  const db = c.get("db");
  const limitRaw = c.req.query("limit");
  const offsetRaw = c.req.query("offset");
  const deviceId = c.req.query("deviceId");
  const limit = limitRaw !== undefined ? Number(limitRaw) : 200;
  const offset = offsetRaw !== undefined ? Number(offsetRaw) : 0;
  if (!Number.isFinite(limit) || limit < 1 || !Number.isFinite(offset) || offset < 0) {
    return c.json({ error: "invalid_request" }, 400);
  }
  const effectiveLimit = Math.min(Math.trunc(limit), MAX_LIMIT);
  const effectiveOffset = Math.trunc(offset);
  const rows = listAudit(db, {
    limit: effectiveLimit,
    offset: effectiveOffset,
    deviceId: deviceId ?? undefined,
  });
  return c.json({
    audit: rows,
    limit: effectiveLimit,
    offset: effectiveOffset,
    hasMore: rows.length === effectiveLimit,
  });
});

function csvCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  let text = String(value);
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

auditRoutes.get("/export.csv", async (c: AppContext) => {
  const db = c.get("db");
  const rows = listAudit(db, { limit: 10_000 });
  const lines = ["ts,username,role,action,device_id,field,old_value,new_value,success,detail"];
  for (const row of rows) {
    lines.push(
      [
        csvCell(row.ts),
        csvCell(row.username),
        csvCell(row.role),
        csvCell(row.action),
        csvCell(row.device_id),
        csvCell(row.field),
        csvCell(row.old_value),
        csvCell(row.new_value),
        csvCell(row.success),
        csvCell(row.detail),
      ].join(","),
    );
  }
  c.header("Content-Type", "text/csv; charset=utf-8");
  c.header("Content-Disposition", 'attachment; filename="audit.csv"');
  return c.body(lines.join("\n"));
});
