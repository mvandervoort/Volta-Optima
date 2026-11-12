import { Socket } from "node:net";
import { FrameParser, type ParsedFrame } from "./sProtocol";

export type ConnectionState = "offline" | "connecting" | "online";

type Pending = {
  expectedCommand: number;
  resolve: (frame: ParsedFrame) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

export class ConverterConnection {
  private socket: Socket | null = null;
  private parser = new FrameParser();
  private pending: Pending | null = null;
  /** FIFO of queued transactions: one outstanding frame at a time on the bus. */
  private chain: Promise<void> = Promise.resolve();
  private queued = 0;
  private static readonly MAX_QUEUE = 64;
  private state: ConnectionState = "offline";
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;
  private backoff = 1000;

  constructor(
    private readonly host: string,
    private readonly port: number,
    private readonly onStateChange: (state: ConnectionState) => void = () => {},
  ) {}

  getState(): ConnectionState {
    return this.state;
  }

  private setState(state: ConnectionState): void {
    if (this.state === state) return;
    this.state = state;
    if (state === "online") this.backoff = 1000;
    this.onStateChange(state);
  }

  async connect(): Promise<void> {
    if (this.closed || this.state === "online" || this.state === "connecting") return;
    this.setState("connecting");
    const socket = new Socket();
    socket.setNoDelay(true);
    this.socket = socket;

    socket.on("connect", () => {
      this.setState("online");
    });
    socket.on("data", (chunk: Buffer) => {
      const frames = this.parser.push(new Uint8Array(chunk));
      for (const frame of frames) {
        if (!this.pending) continue;
        if (this.pending.expectedCommand !== frame.command) continue;
        const pending = this.pending;
        this.pending = null;
        clearTimeout(pending.timer);
        pending.resolve(frame);
      }
    });
    socket.on("error", (error: Error) => {
      this.rejectPending(error);
      this.handleDisconnect();
    });
    socket.on("close", () => {
      this.handleDisconnect();
    });

    await new Promise<void>((resolve, reject) => {
      socket.once("connect", () => resolve());
      socket.once("error", (error) => reject(error));
      socket.connect(this.port, this.host);
    });
  }

  private handleDisconnect(): void {
    if (this.closed) return;
    this.parser.reset();
    this.rejectPending(new Error("Converter connection closed"));
    this.setState("offline");
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      void this.connect().catch(() => {
        this.backoff = Math.min(this.backoff * 2, 30_000);
        this.handleDisconnect();
      });
    }, this.backoff);
  }

  private rejectPending(error: Error): void {
    if (!this.pending) return;
    const pending = this.pending;
    this.pending = null;
    clearTimeout(pending.timer);
    pending.reject(error);
  }

  request(
    frame: Uint8Array,
    timeoutMs = 500,
    expectedCommand = frame[6 + (frame[5] === 0x82 ? 5 : 1)] ?? 0,
  ): Promise<ParsedFrame> {
    if (this.queued >= ConverterConnection.MAX_QUEUE) {
      return Promise.reject(new Error("Converter queue is full"));
    }
    const run = (): Promise<ParsedFrame> =>
      new Promise<ParsedFrame>((resolve, reject) => {
        if (this.state !== "online" || !this.socket) {
          reject(new Error("Converter is not online"));
          return;
        }
        if (this.pending) {
          reject(new Error("A protocol transaction is already in progress"));
          return;
        }
        const timer = setTimeout(() => {
          this.pending = null;
          reject(new Error("Protocol response timeout"));
        }, timeoutMs);
        this.pending = { expectedCommand, resolve, reject, timer };
        this.socket.write(frame);
      });

    this.queued += 1;
    const result = this.chain.then(run, run).finally(() => {
      this.queued -= 1;
    });
    this.chain = result.then(
      () => undefined,
      () => undefined,
    );
    return result;
  }

  async close(): Promise<void> {
    this.closed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.rejectPending(new Error("Converter connection closed"));
    this.parser.reset();
    this.socket?.destroy();
    this.socket = null;
    this.setState("offline");
  }
}