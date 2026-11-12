import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";

export const healthRoutes = new Hono<{ Variables: AppVariables }>();

healthRoutes.get("/", async (c: AppContext) => {
  const engine = c.get("pollEngine");
  const devices = engine.snapshots();
  const online = devices.filter((d) => d.online).length;
  return c.json({
    status: engine.getConnectionState() === "online" ? "online" : "degraded",
    converter: engine.getConnectionState(),
    devices: { total: devices.length, online },
    lastPoll: engine.getLastPollAt(),
    version: process.env.FLOWHUB_VERSION ?? "0.1.0",
  });
});
