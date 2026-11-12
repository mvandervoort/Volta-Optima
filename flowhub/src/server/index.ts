import { serve } from "bun";
import { Hono } from "hono";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { loadConfig } from "./config";
import { openDatabase } from "./db";
import { ensureAdmin } from "./auth";
import { PollEngine } from "./bus/pollEngine";
import { WebSocketHub } from "./ws";
import { healthRoutes } from "./api/health";
import { authRoutes } from "./api/auth";
import { usersRoutes } from "./api/users";
import { devicesRoutes } from "./api/devices";
import { auditRoutes } from "./api/audit";
import { loadSession } from "./middleware/auth";
import type { AppVariables } from "./middleware/auth";

const PORT = Number(process.env.FLOWHUB_PORT ?? 8080);
const DATA_DIR = process.env.FLOWHUB_DATA_DIR ?? "./data";
const DB_PATH = join(DATA_DIR, "flowhub.db");
const DIST_DIR = join(process.cwd(), "dist");
const SESSION_SECRET = process.env.FLOWHUB_SESSION_SECRET ?? "dev-secret-change-me";

function contentType(path: string): string {
  if (path.endsWith(".html")) return "text/html; charset=utf-8";
  if (path.endsWith(".js")) return "application/javascript";
  if (path.endsWith(".css")) return "text/css";
  if (path.endsWith(".json")) return "application/json";
  if (path.endsWith(".png") || path.endsWith(".jpg") || path.endsWith(".jpeg") || path.endsWith(".webp"))
    return "image/*";
  if (path.endsWith(".svg")) return "image/svg+xml";
  if (path.endsWith(".ico")) return "image/x-icon";
  if (path.endsWith(".woff") || path.endsWith(".woff2")) return "font/*";
  if (path.endsWith(".ttf") || path.endsWith(".otf")) return "font/*";
  return "application/octet-stream";
}

function staticResponse(filePath: string): Response {
  const buffer = readFileSync(filePath);
  return new Response(buffer, { headers: { "content-type": contentType(filePath) } });
}

function spaFallback(): Response | null {
  const index = join(DIST_DIR, "index.html");
  if (existsSync(index)) return staticResponse(index);
  return null;
}

async function main(): Promise<void> {
  const config = loadConfig();
  const db = openDatabase(DB_PATH);
  await ensureAdmin(db);

  let broadcastState: ((devices: unknown) => void) | null = null;
  let broadcastConnection: ((state: unknown) => void) | null = null;
  const engine = new PollEngine(db, config, {
    onState: (devices) => broadcastState?.(devices),
    onConnection: (state) => broadcastConnection?.(state),
  });
  const hub = new WebSocketHub(db, SESSION_SECRET, engine);
  broadcastState = (devices) => hub.broadcast({ type: "state", devices });
  broadcastConnection = (state) => hub.broadcast({ type: "connection", state });

  const app = new Hono<{ Variables: AppVariables }>();

  app.use("*", async (c, next) => {
    c.set("db", db);
    c.set("sessionSecret", SESSION_SECRET);
    c.set("pollEngine", engine);
    return next();
  });
  app.use("*", loadSession);

  app.route("/api/v1/health", healthRoutes);
  app.route("/api/v1/auth", authRoutes);
  app.route("/api/v1/users", usersRoutes);
  app.route("/api/v1/devices", devicesRoutes);
  app.route("/api/v1/audit", auditRoutes);

  app.get("*", (c) => {
    const path = c.req.path;
    if (path.startsWith("/api")) return c.json({ error: "not_found" }, 404);
    if (existsSync(DIST_DIR)) {
      const candidate = join(DIST_DIR, path === "/" ? "index.html" : path.slice(1));
      if (existsSync(candidate)) {
        return staticResponse(candidate);
      }
    }
    const fallback = spaFallback();
    if (fallback) return fallback;
    return c.json(
      { error: "frontend_not_built", hint: "Run `bun run build` to build the web UI" },
      503,
    );
  });

  const server = serve({
    port: PORT,
    fetch(req, srv) {
      const url = new URL(req.url);
      if (url.pathname === "/api/v1/ws") {
        const upgraded = srv.upgrade(req, { data: { url: req.url } });
        if (upgraded) return undefined;
        return new Response("websocket_upgrade_failed", { status: 400 });
      }
      return app.fetch(req);
    },
    websocket: hub.handler(),
  });

  console.log(`FlowHub listening on http://localhost:${PORT}`);

  const signals: NodeJS.Signals[] = ["SIGTERM", "SIGINT"];
  for (const signal of signals) {
    process.on(signal, () => {
      console.log(`Received ${signal}, shutting down...`);
      engine.stop();
      db.close();
      server.stop();
      process.exit(0);
    });
  }
}

main().catch((error: unknown) => {
  console.error("Failed to start FlowHub:", error instanceof Error ? error.message : String(error));
  process.exit(1);
});
