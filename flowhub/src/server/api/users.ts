import { Hono } from "hono";
import type { AppContext, AppVariables } from "../middleware/auth";
import { requireAuth, requireAdmin } from "../middleware/auth";
import { hashPassword } from "../auth";
import {
  listUsers,
  createUser,
  setUserActive,
  setUserRole,
  getUserById,
} from "../db";
import { recordAudit } from "../audit";
import { z } from "zod";

const userSchema = z.object({
  username: z.string().min(3).max(64),
  password: z.string().min(10),
  role: z.enum(["operator", "admin"]),
});

const patchUserSchema = z.object({
  name: z.string().optional(),
  role: z.enum(["operator", "admin"]).optional(),
  active: z.boolean().optional(),
});

export const usersRoutes = new Hono<{ Variables: AppVariables }>();

usersRoutes.use("*", requireAuth, requireAdmin);

usersRoutes.get("/", async (c: AppContext) => {
  const db = c.get("db");
  return c.json({
    users: listUsers(db).map((u) => ({
      id: u.id,
      username: u.username,
      role: u.role,
      active: u.active === 1,
      created_at: u.created_at,
      last_login: u.last_login,
    })),
  });
});

usersRoutes.post("/", async (c: AppContext) => {
  const db = c.get("db");
  const { userId, username: actor, role: actorRole } = authenticated(c);
  let input: z.infer<typeof userSchema>;
  try {
    input = userSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const user = createUser(db, {
    username: input.username,
    passwordHash: await hashPassword(input.password),
    role: input.role,
  });
  recordAudit(db, {
    userId,
    username: actor,
    role: actorRole,
    action: "user.create",
    deviceId: String(user.id),
    newValue: input.role,
    success: true,
    detail: `Created user ${input.username}`,
  });
  return c.json(
    {
      id: user.id,
      username: user.username,
      role: user.role,
      active: true,
    },
    201,
  );
});

usersRoutes.patch("/:id", async (c: AppContext) => {
  const db = c.get("db");
  const { userId, username: actor, role: actorRole } = authenticated(c);
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid_request" }, 400);
  let input: z.infer<typeof patchUserSchema>;
  try {
    input = patchUserSchema.parse(await c.req.json());
  } catch {
    return c.json({ error: "invalid_request" }, 400);
  }
  const user = getUserById(db, id);
  if (!user) return c.json({ error: "not_found" }, 404);
  if (input.role !== undefined) setUserRole(db, id, input.role);
  if (input.active !== undefined) setUserActive(db, id, input.active);
  recordAudit(db, {
    userId,
    username: actor,
    role: actorRole,
    action: "user.update",
    deviceId: String(id),
    oldValue: { role: user.role, active: user.active === 1 },
    newValue: { role: input.role ?? user.role, active: input.active ?? user.active === 1 },
    success: true,
    detail: `Updated user ${user.username}`,
  });
  const updated = getUserById(db, id)!;
  return c.json({
    id: updated.id,
    username: updated.username,
    role: updated.role,
    active: updated.active === 1,
  });
});

function authenticated(c: AppContext): { userId: number; username: string; role: string } {
  const db = c.get("db");
  const userId = c.get("userId");
  if (userId === undefined) throw new Error("not authenticated");
  const user = getUserById(db, userId);
  if (!user) throw new Error("not authenticated");
  return { userId, username: user.username, role: user.role };
}
