import type { ServerWebSocket } from "bun";
import type { Database } from "bun:sqlite";
import { PollEngine } from "./bus/pollEngine";
import { verifySessionToken } from "./auth";
import { getUserById } from "./db";

export type ClientWebSocket = ServerWebSocket<{ url: string; cookie: string; userId?: number }>;

const SESSION_COOKIE = "flowhub_session";

function sessionFromCookie(header: string): string | null {
  for (const part of header.split(";")) {
    const separator = part.indexOf("=");
    if (separator < 0) continue;
    if (part.slice(0, separator).trim() !== SESSION_COOKIE) continue;
    return part.slice(separator + 1).trim() || null;
  }
  return null;
}

export class WebSocketHub {
  private readonly clients = new Set<ClientWebSocket>();

  constructor(
    private readonly db: Database,
    private readonly sessionSecret: string,
    private readonly engine: PollEngine,
  ) {}

  private authenticate(url: string, cookie: string): number | null {
    try {
      const parsed = new URL(url, "http://localhost");
      const token = parsed.searchParams.get("token") ?? sessionFromCookie(cookie);
      if (!token) return null;
      const session = verifySessionToken(token, this.sessionSecret);
      if (session === null) return null;
      const user = getUserById(this.db, session.userId);
      if (!user || user.active !== 1 || user.token_version !== session.tokenVersion) return null;
      return user.id;
    } catch {
      return null;
    }
  }

  handler() {
    return {
      open: (ws: ClientWebSocket): void => {
        const userId = this.authenticate(ws.data.url, ws.data.cookie);
        if (userId === null) {
          ws.close(1008, "unauthorized");
          return;
        }
        ws.data.userId = userId;
        this.clients.add(ws);
        ws.send(JSON.stringify({ type: "state", devices: this.engine.snapshots() }));
        ws.send(JSON.stringify({ type: "connection", state: this.engine.getConnectionState() }));
      },
      message: (ws: ClientWebSocket, message: string | Buffer): void => {
        if (message === "ping") ws.send("pong");
      },
      close: (ws: ClientWebSocket): void => {
        this.clients.delete(ws);
      },
    };
  }

  broadcast(payload: unknown): void {
    const text = JSON.stringify(payload);
    for (const ws of this.clients) {
      if (ws.readyState === 1) {
        ws.send(text);
      }
    }
  }

  getClientCount(): number {
    return this.clients.size;
  }
}
