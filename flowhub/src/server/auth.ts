import { createHmac, timingSafeEqual } from "node:crypto";
import type { Context } from "hono";
import { setCookie } from "hono/cookie";
import type { Database } from "bun:sqlite";
import { createUser, listUsers } from "./db";
import { recordAudit } from "./audit";

const COOKIE_NAME = "flowhub_session";
const SESSION_TTL_SECONDS = 60 * 60 * 12;

export async function hashPassword(password: string): Promise<string> {
  return Bun.password.hash(password, { algorithm: "bcrypt", cost: 10 });
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  try {
    return await Bun.password.verify(password, hash);
  } catch {
    return false;
  }
}

function sign(payload: string, secret: string): string {
  return createHmac("sha256", secret).update(payload).digest("base64url");
}

export type SessionPayload = {
  userId: number;
  tokenVersion: number;
};

export function createSessionToken(
  userId: number,
  secret: string,
  tokenVersion = 0,
  ttlSeconds = SESSION_TTL_SECONDS,
): string {
  const payload = JSON.stringify({
    uid: userId,
    tv: tokenVersion,
    exp: Math.floor(Date.now() / 1000) + ttlSeconds,
  });
  const encoded = Buffer.from(payload, "utf8").toString("base64url");
  return `${encoded}.${sign(encoded, secret)}`;
}

export function verifySessionToken(token: string, secret: string): SessionPayload | null {
  const [encoded, signature] = token.split(".");
  if (!encoded || !signature) return null;
  const expected = sign(encoded, secret);
  const signatureBuffer = Buffer.from(signature);
  const expectedBuffer = Buffer.from(expected);
  if (signatureBuffer.length !== expectedBuffer.length) return null;
  if (!timingSafeEqual(signatureBuffer, expectedBuffer)) return null;
  try {
    const payload = JSON.parse(Buffer.from(encoded, "base64url").toString("utf8")) as {
      uid: number;
      tv?: number;
      exp: number;
    };
    if (!Number.isFinite(payload.uid) || payload.exp < Math.floor(Date.now() / 1000)) return null;
    return {
      userId: payload.uid,
      tokenVersion: Number.isFinite(payload.tv) ? Number(payload.tv) : 0,
    };
  } catch {
    return null;
  }
}

export function parseCookies(header: string | null | undefined): Record<string, string> {
  const cookies: Record<string, string> = {};
  if (!header) return cookies;
  for (const part of header.split(";")) {
    const index = part.indexOf("=");
    if (index === -1) continue;
    const key = part.slice(0, index).trim();
    const value = part.slice(index + 1).trim();
    if (key) cookies[key] = decodeURIComponent(value);
  }
  return cookies;
}

export function setSessionCookie(c: Context, token: string, insecure = false): void {
  setCookie(c, COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: "Strict",
    secure: !insecure,
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  });
}

export function clearSessionCookie(c: Context, insecure = false): void {
  setCookie(c, COOKIE_NAME, "", {
    httpOnly: true,
    sameSite: "Strict",
    secure: !insecure,
    path: "/",
    maxAge: 0,
  });
}

export function getSessionUser(c: Context, secret: string): SessionPayload | null {
  const cookies = parseCookies(c.req.header("cookie"));
  const token = cookies[COOKIE_NAME] ?? null;
  if (!token) return null;
  return verifySessionToken(token, secret);
}

/**
 * Behind the Caddy reverse proxy the client address arrives in X-Forwarded-For.
 * Outside that setup the header is attacker-controlled, so it is only trusted
 * when FLOWHUB_TRUST_PROXY=1.
 */
export function getClientIp(c: Context): string {
  if (process.env.FLOWHUB_TRUST_PROXY === "1") {
    const forwarded = c.req.header("x-forwarded-for");
    if (forwarded) return forwarded.split(",")[0]!.trim();
    const realIp = c.req.header("x-real-ip");
    if (realIp) return realIp;
  }
  return "local";
}

type Attempt = { count: number; first: number };

export class LoginRateLimiter {
  private attempts = new Map<string, Attempt>();
  private lastSweep = Date.now();

  constructor(
    private readonly limit = 5,
    private readonly windowMs = 5 * 60 * 1000,
  ) {}

  private sweep(): void {
    const now = Date.now();
    if (now - this.lastSweep < this.windowMs) return;
    this.lastSweep = now;
    for (const [key, attempt] of this.attempts) {
      if (now - attempt.first > this.windowMs) this.attempts.delete(key);
    }
  }

  isBlocked(key: string): boolean {
    this.sweep();
    const attempt = this.attempts.get(key);
    if (!attempt) return false;
    if (Date.now() - attempt.first > this.windowMs) {
      this.attempts.delete(key);
      return false;
    }
    return attempt.count >= this.limit;
  }

  recordFailure(key: string): void {
    const attempt = this.attempts.get(key);
    if (!attempt || Date.now() - attempt.first > this.windowMs) {
      this.attempts.set(key, { count: 1, first: Date.now() });
      return;
    }
    attempt.count += 1;
  }

  reset(key: string): void {
    this.attempts.delete(key);
  }
}

export async function ensureAdmin(db: Database): Promise<void> {
  const username = process.env.FLOWHUB_ADMIN_USER;
  const password = process.env.FLOWHUB_ADMIN_PASSWORD;
  if (!username || !password) {
    throw new Error(
      "FLOWHUB_ADMIN_USER and FLOWHUB_ADMIN_PASSWORD must be set to bootstrap the admin account",
    );
  }
  if (password.length < 10) {
    throw new Error("Admin password must be at least 10 characters");
  }
  const existing = listUsers(db);
  if (existing.length > 0) return;
  const passwordHash = await hashPassword(password);
  const user = createUser(db, { username, passwordHash, role: "admin" });
  recordAudit(db, {
    username: user.username,
    role: user.role,
    action: "admin.bootstrap",
    success: true,
    detail: "Default admin account created at startup",
  });
}