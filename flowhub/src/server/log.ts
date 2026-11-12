export type LogLevel = "debug" | "info" | "warn" | "error";

/** JSON-lines logging: one object per line, ready for journald or Docker log drivers. */
export function log(
  level: LogLevel,
  message: string,
  fields: Record<string, unknown> = {},
): void {
  const line = JSON.stringify({ ts: new Date().toISOString(), level, message, ...fields });
  if (level === "error") console.error(line);
  else if (level === "warn") console.warn(line);
  else console.log(line);
}

export function correlationIdFrom(header: string | null | undefined): string {
  if (header && /^[A-Za-z0-9._-]{1,64}$/.test(header)) return header;
  return crypto.randomUUID();
}