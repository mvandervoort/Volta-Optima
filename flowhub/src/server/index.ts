import { serve } from "bun";
import { Hono } from "hono";
import { existsSync, readFileSync } from "node:fs";
import { join, resolve, sep } from "node:path";
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
import { correlationIdFrom, log } from "./log";

const PORT = Number(process.env.FLOWHUB_PORT ?? 8080);
const DATA_DIR = process.env.FLOWHUB_DATA_DIR ?? "./data";
const DB_PATH = join(DATA_DIR, "flowhub.db");
const DIST_DIR = resolve(process.cwd(), "dist");

function requireSessionSecret(): string {
  const secret = process.env.FLOWHUB_SESSION_SECRET ?? "";
  if (!secret || secret === "dev-secret-change-me") {
    throw new Error(
      "FLOWHUB_SESSION_SECRET is required. Generate one with `openssl rand -hex 32`.",
    );
  }
  if (process.env.NODE_ENV === "production" && secret.length < 32) {
    throw new Error("FLOWHUB_SESSION_SECRET must be at least 32 characters in production.");
  }
  return secret;
}

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

/** Resolves a request path inside dist and refuses anything that escapes it. */
function distFile(requestPath: string): string | null {
  const relative = requestPath === "/" ? "index.html" : requestPath.replace(/^\/+/, "");
  if (relative.includes("\0")) return null;
  const candidate = resolve(DIST_DIR, relative);
  if (candidate !== DIST_DIR && !candidate.startsWith(DIST_DIR + sep)) return null;
  return candidate;
}

function spaFallback(): Response | null {
  const index = join(DIST_DIR, "index.html");
  if (existsSync(index)) return staticResponse(index);
  return null;
}

async function main(): Promise<void> {
  const config = loadConfig();
  const sessionSecret = requireSessionSecret();
  const db = openDatabase(DB_PATH);
  await ensureAdmin(db);

  let broadcastState: ((devices: unknown) => void) | null = null;
  let broadcastConnection: ((state: unknown) => void) | null = null;
  const engine = new PollEngine(db, config, {
    onState: (devices) => broadcastState?.(devices),
    onConnection: (state) => broadcastConnection?.(state),
  });
  const hub = new WebSocketHub(db, sessionSecret, engine);
  broadcastState = (devices) => hub.broadcast({ type: "state", devices });
  broadcastConnection = (state) => hub.broadcast({ type: "connection", state });

  await engine.start();

  const app = new Hono<{ Variables: AppVariables }>();

  app.use("*", async (c, next) => {
    c.set("db", db);
    c.set("sessionSecret", sessionSecret);
    c.set("pollEngine", engine);
    c.set("correlationId", correlationIdFrom(c.req.header("x-correlation-id")));
    return next();
  });

  app.use("*", async (c, next) => {
    const started = Date.now();
    await next();
    c.header("x-correlation-id", c.get("correlationId"));
    c.header("x-content-type-options", "nosniff");
    c.header("referrer-policy", "no-referrer");
    c.header("x-frame-options", "DENY");
    if (c.req.path !== "/api/v1/health") {
      log("info", "request", {
        correlationId: c.get("correlationId"),
        method: c.req.method,
        path: c.req.path,
        status: c.res.status,
        durationMs: Date.now() - started,
      });
    }
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
      const candidate = distFile(path);
      if (candidate !== null && existsSync(candidate)) {
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
        const cookie = req.headers.get("cookie") ?? "";
        const upgraded = srv.upgrade(req, { data: { url: req.url, cookie } });
        if (upgraded) return undefined;
        return new Response("websocket_upgrade_failed", { status: 400 });
      }
      return app.fetch(req);
    },
    websocket: hub.handler(),
  });

  log("info", "started", { port: PORT, converter: `${config.converter.host}:${config.converter.port}` });

  const signals: NodeJS.Signals[] = ["SIGTERM", "SIGINT"];
  for (const signal of signals) {
    process.on(signal, () => {
      log("info", "shutdown", { signal });
      engine.stop();
      db.close();
      server.stop();
      process.exit(0);
    });
  }
}

main().catch((error: unknown) => {
  log("error", "startup_failed", {
    error: error instanceof Error ? error.message : String(error),
  });
  process.exit(1);
});