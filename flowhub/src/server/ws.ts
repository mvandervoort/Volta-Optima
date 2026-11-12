import type { ServerWebSocket } from "bun";
import type { Database } from "bun:sqlite";
import { PollEngine } from "./bus/pollEngine";
import { verifySessionToken } from "./auth";

export type ClientWebSocket = ServerWebSocket<{ url: string; userId?: number }>;

export class WebSocketHub {
  private readonly clients = new Set<ClientWebSocket>();

  constructor(
    private readonly db: Database,
    private readonly sessionSecret: string,
    private readonly engine: PollEngine,
  ) {}

  private authenticate(url: string): number | null {
    try {
      const parsed = new URL(url, "http://localhost");
      const token = parsed.searchParams.get("token") ?? null;
      if (!token) return null;
      return verifySessionToken(token, this.sessionSecret);
    } catch {
      return null;
    }
  }

  handler() {
    return {
      open: (ws: ClientWebSocket): void => {
        const userId = this.authenticate(ws.data.url);
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
