import type { Context, MiddlewareHandler } from "hono";
import type { Database } from "bun:sqlite";
import type { UserRole } from "../db";
import type { PollEngine } from "../bus/pollEngine";
import { getSessionUser } from "../auth";
import { getUserById } from "../db";

export type AppVariables = {
  db: Database;
  sessionSecret: string;
  pollEngine: PollEngine;
  userId: number | undefined;
  userRole: UserRole | undefined;
};

export type AppContext = Context<{ Variables: AppVariables }>;

export const loadSession: MiddlewareHandler<{ Variables: AppVariables }> = async (
  c,
  next,
) => {
  const db = c.get("db");
  const secret = c.get("sessionSecret");
  const userId = getSessionUser(c, secret);
  if (userId !== null) {
    const user = getUserById(db, userId);
    if (user && user.active === 1) {
      c.set("userId", user.id);
      c.set("userRole", user.role);
    }
  }
  await next();
};

export const requireAuth: MiddlewareHandler<{ Variables: AppVariables }> = async (
  c,
  next,
) => {
  if (c.get("userId") === undefined) {
    return c.json({ error: "unauthorized" }, 401);
  }
  await next();
};

export const requireAdmin: MiddlewareHandler<{ Variables: AppVariables }> = async (
  c,
  next,
) => {
  if (c.get("userRole") !== "admin") {
    return c.json({ error: "forbidden" }, 403);
  }
  await next();
};

export function authenticatedUser(c: AppContext): { userId: number; userRole: UserRole } {
  const userId = c.get("userId");
  const userRole = c.get("userRole");
  if (userId === undefined || userRole === undefined) {
    throw new Error("authenticated user not set");
  }
  return { userId, userRole };
}
