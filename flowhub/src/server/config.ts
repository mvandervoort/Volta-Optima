import { z } from "zod";
import { existsSync, readFileSync } from "node:fs";
import { Buffer } from "node:buffer";

const parity = z.enum(["none", "odd", "even"]);

export const configSchema = z.object({
  converter: z.object({
    host: z.string().min(1),
    port: z.number().int().min(1).max(65535),
    baudRate: z.number().int().positive(),
    dataBits: z.literal(8),
    parity,
    stopBits: z.literal(1),
  }),
  bus: z.object({
    pollIntervalMs: z.number().int().min(250).max(60_000).default(1000),
    devices: z
      .array(
        z.object({
          id: z.string().min(1),
          initialName: z.string().min(1),
          address: z.string().min(1),
          tag: z.string().optional(),
          serial: z.string().optional(),
        }),
      )
      .min(1)
      .max(32),
  }),
});

export type Config = z.infer<typeof configSchema>;
export type DeviceConfig = Config["bus"]["devices"][number];

export function loadConfig(path = process.env.FLOWHUB_CONFIG ?? "./config.json"): Config {
  if (!existsSync(path)) {
    throw new Error(`FlowHub config not found at ${path}. Copy config.example.json and edit it.`);
  }
  const raw = JSON.parse(readFileSync(path, "utf8"));
  const parsed = configSchema.safeParse(raw);
  if (!parsed.success) {
    throw new Error(`Invalid FlowHub config: ${parsed.error.message}`);
  }
  return parsed.data;
}

export type ParsedAddress =
  | { kind: "short"; value: number }
  | { kind: "long"; value: Uint8Array };

export function parseAddress(address: string): ParsedAddress {
  const trimmed = address.trim();
  if (/^\d{1,2}$/.test(trimmed)) {
    const value = Number(trimmed);
    if (value < 1 || value > 15) {
      throw new Error(`Short polling address must be 1-15, got ${trimmed}`);
    }
    return { kind: "short", value };
  }
  if (/^[0-9a-fA-F]{10}$/.test(trimmed)) {
    return { kind: "long", value: Uint8Array.from(Buffer.from(trimmed, "hex")) };
  }
  throw new Error(
    `Invalid address "${address}". Use a short polling number (1-15) or a 5-byte long address (10 hex chars).`,
  );
}

export function addressToString(address: ParsedAddress): string {
  if (address.kind === "short") return String(address.value);
  return Buffer.from(address.value).toString("hex");
}