import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";
import {
  verifyPassword,
  createSessionToken,
  setSessionCookie,
  clearSessionCookie,
  getClientIp,
  LoginRateLimiter,
} from "../auth";
import {
  getUserByUsername,
  getUserById,
} from "../db";
import { recordAudit } from "../audit";
import { z } from "zod";

export const authRoutes = new Hono<{ Variables: AppVariables }>();

const rateLimiter = new LoginRateLimiter();

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

function insecure(): boolean {
  return process.env.FLOWHUB_INSECURE_COOKIE === "1";
}

authRoutes.post("/login", async (c: AppContext) => {
  const db = c.get("db");
  const secret = c.get("sessionSecret");
  const ip = getClientIp(c);
  let body: { username: string; password: string };
  try {
    body = loginSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const key = `${ip}:${body.username}`;
  if (rateLimiter.isBlocked(key)) {
    recordAudit(db, {
      username: body.username,
      role: "unknown",
      action: "auth.login",
      success: false,
      detail: "Rate limited",
    });
    return c.json({ error: "rate_limited" }, 429);
  }
  const user = getUserByUsername(db, body.username);
  if (!user || !(await verifyPassword(body.password, user.password_hash))) {
    rateLimiter.recordFailure(key);
    recordAudit(db, {
      username: body.username,
      role: "unknown",
      action: "auth.login",
      success: false,
      detail: "Invalid credentials",
    });
    return c.json({ error: "invalid_credentials" }, 401);
  }
  if (user.active !== 1) {
    rateLimiter.recordFailure(key);
    return c.json({ error: "account_inactive" }, 403);
  }
  rateLimiter.reset(key);
  const token = createSessionToken(user.id, secret);
  setSessionCookie(c, token, insecure());
  recordAudit(db, {
    userId: user.id,
    username: user.username,
    role: user.role,
    action: "auth.login",
    success: true,
    detail: "Login successful",
  });
  return c.json({
    ok: true,
    user: { id: user.id, username: user.username, role: user.role },
  });
});

authRoutes.post("/logout", async (c: AppContext) => {
  const db = c.get("db");
  const userId = c.get("userId");
  const user = userId !== undefined ? getUserById(db, userId) : null;
  clearSessionCookie(c, insecure());
  if (user) {
    recordAudit(db, {
      userId: user.id,
      username: user.username,
      role: user.role,
      action: "auth.logout",
      success: true,
    });
  }
  return c.json({ ok: true });
});

authRoutes.get("/me", async (c: AppContext) => {
  const userId = c.get("userId");
  const userRole = c.get("userRole");
  if (userId === undefined || userRole === undefined) {
    return c.json({ error: "unauthorized" }, 401);
  }
  const db = c.get("db");
  const user = getUserById(db, userId);
  if (!user) return c.json({ error: "unauthorized" }, 401);
  return c.json({
    user: { id: user.id, username: user.username, role: user.role, active: user.active === 1 },
  });
});
