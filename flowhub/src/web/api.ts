export type Role = "admin" | "operator";

export type SessionUser = {
  id: number;
  username: string;
  role: Role;
  active?: boolean;
};

export type DeviceStatus = "online" | "stale" | "offline" | "fault";

export type DeviceSnapshot = {
  id: number;
  configId: string;
  name: string;
  address: string;
  online: boolean;
  status: DeviceStatus;
  flow: number | null;
  unit: string | null;
  setpoint: number | null;
  setpointUnit: string | null;
  valvePosition: number | null;
  temperature: number | null;
  totalizer: number | null;
  statusBits: number | null;
  lastSeen: string | null;
};

export type DeviceInfo = {
  device_id: number;
  flow_unit: number | null;
  temp_unit: number | null;
  gas_type: number | null;
  tag: string | null;
  serial: string | null;
  updated_at: string | null;
};

export type UserRow = {
  id: number;
  username: string;
  role: Role;
  active: boolean;
  created_at: string | null;
  last_login: string | null;
};

export type AuditEntry = {
  id: number;
  ts: string;
  user_id: number | null;
  username: string;
  role: string;
  action: string;
  device_id: string | null;
  field: string | null;
  old_value: string | null;
  new_value: string | null;
  success: number;
  detail: string | null;
};

class ApiError extends Error {
  constructor(
    readonly code: string,
    readonly status: number,
  ) {
    super(code);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  const text = await response.text();
  const data = text.length > 0 ? (JSON.parse(text) as unknown) : null;
  if (!response.ok) {
    const code =
      data !== null && typeof data === "object" && "error" in data
        ? String((data as { error: unknown }).error)
        : `http_${response.status}`;
    if (response.status === 401) window.location.hash = "#/login";
    throw new ApiError(code, response.status);
  }
  return data as T;
}

export const api = {
  me: () => request<{ user: SessionUser }>("/auth/me"),
  login: (username: string, password: string) =>
    request<{ ok: true; user: SessionUser }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  logout: () => request<{ ok: true }>("/auth/logout", { method: "POST" }),

  devices: () => request<{ devices: DeviceSnapshot[] }>("/devices"),
  device: (id: number) => request<{ device: DeviceSnapshot; info: DeviceInfo | null }>(`/devices/${id}`),
  patchDevice: (id: number, body: { name?: string; enabled?: boolean; pollIntervalMs?: number }) =>
    request<{ ok: true }>(`/devices/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  setpoint: (id: number, value: number, unit: "percent" | "engineering") =>
    request<{ ok: boolean }>(`/devices/${id}/setpoint`, {
      method: "POST",
      body: JSON.stringify({ value, unit }),
    }),
  valveOverride: (id: number, mode: "normal" | "open" | "closed") =>
    request<{ ok: boolean }>(`/devices/${id}/valve-override`, {
      method: "POST",
      body: JSON.stringify({ mode }),
    }),
  refresh: (id: number) => request<{ ok: true }>(`/devices/${id}/refresh`, { method: "POST" }),
  writeConfig: (id: number, body: Record<string, unknown>) =>
    request<{ ok: true }>(`/devices/${id}/config`, { method: "POST", body: JSON.stringify(body) }),

  users: () => request<{ users: UserRow[] }>("/users"),
  createUser: (username: string, password: string, role: Role) =>
    request<UserRow>("/users", { method: "POST", body: JSON.stringify({ username, password, role }) }),
  patchUser: (id: number, body: { role?: Role; active?: boolean }) =>
    request<UserRow>(`/users/${id}`, { method: "PATCH", body: JSON.stringify(body) }),

  audit: (limit = 200) => request<{ audit: AuditEntry[] }>(`/audit?limit=${limit}`),
};

export { ApiError };