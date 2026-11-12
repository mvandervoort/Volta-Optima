import { useCallback, useEffect, useState } from "react";
import { api, type DeviceSnapshot, type SessionUser } from "./api";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { DeviceDetail } from "./pages/DeviceDetail";
import { Users } from "./pages/Users";
import { Audit } from "./pages/Audit";

type Route =
  | { name: "dashboard" }
  | { name: "device"; id: number }
  | { name: "users" }
  | { name: "audit" };

function parseRoute(): Route {
  const hash = window.location.hash.replace(/^#\/?/, "");
  const [head, tail] = hash.split("/");
  if (head === "devices" && tail !== undefined) {
    const id = Number(tail);
    if (Number.isFinite(id)) return { name: "device", id };
  }
  if (head === "users") return { name: "users" };
  if (head === "audit") return { name: "audit" };
  return { name: "dashboard" };
}

export function App() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [devices, setDevices] = useState<DeviceSnapshot[]>([]);
  const [route, setRoute] = useState<Route>(parseRoute);
  const [busy, setBusy] = useState(true);
  const [live, setLive] = useState(false);

  useEffect(() => {
    const onHashChange = () => setRoute(parseRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    let cancelled = false;
    api
      .me()
      .then(({ user: me }) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setBusy(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const loadDevices = useCallback(() => {
    api
      .devices()
      .then(({ devices: rows }) => setDevices(rows))
      .catch(() => setDevices([]));
  }, []);

  useEffect(() => {
    if (user === null) return;
    loadDevices();

    let closed = false;
    let socket: WebSocket | null = null;
    let attempt = 0;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      if (closed) return;
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      socket = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws`);
      socket.onopen = () => {
        attempt = 0;
        setLive(true);
        loadDevices();
      };
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(String(event.data)) as {
            type: string;
            devices?: DeviceSnapshot[];
          };
          if (payload.type === "state" && payload.devices) setDevices(payload.devices);
          setLive(true);
        } catch {
          // onbekend bericht negeren
        }
      };
      socket.onerror = () => socket?.close();
      socket.onclose = () => {
        setLive(false);
        if (closed) return;
        attempt += 1;
        const delay = Math.min(1000 * 2 ** (attempt - 1), 15_000);
        timer = setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      closed = true;
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [user, loadDevices]);

  const refresh = useCallback(() => {
    loadDevices();
  }, [loadDevices]);

  const logout = useCallback(() => {
    void api.logout().finally(() => {
      setUser(null);
      setDevices([]);
      window.location.hash = "#/login";
    });
  }, []);

  if (busy) return <p className="loading">Laden…</p>;

  if (user === null) {
    return (
      <Login
        onLoggedIn={(me) => {
          setUser(me);
          window.location.hash = "#/";
        }}
      />
    );
  }

  const isAdmin = user.role === "admin";

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <strong>FlowHub</strong>
          <span className="muted"> Brooks 5850S</span>
        </div>
        <nav>
          <a href="#/" className={route.name === "dashboard" ? "active" : ""}>
            Dashboard
          </a>
          {isAdmin && (
            <>
              <a href="#/users" className={route.name === "users" ? "active" : ""}>
                Gebruikers
              </a>
              <a href="#/audit" className={route.name === "audit" ? "active" : ""}>
                  Audit
                </a>
            </>
          )}
        </nav>
        <div className="user">
          <span className={live ? "live ok" : "live warn"}>
            {live ? "live" : "verbinding verbroken"}
          </span>
          <span>
            {user.username} <span className="badge">{isAdmin ? "admin" : "operator"}</span>
          </span>
          <button type="button" onClick={logout}>
            Uitloggen
          </button>
        </div>
      </header>

      <main>
        {route.name === "dashboard" && (
          <Dashboard devices={devices} onRefresh={refresh} isAdmin={isAdmin} />
        )}
        {route.name === "device" && (
          <DeviceDetail
            deviceId={route.id}
            isAdmin={isAdmin}
            onSaved={refresh}
          />
        )}
        {route.name === "users" && isAdmin && <Users currentUserId={user.id} />}
        {route.name === "audit" && isAdmin && <Audit />}
      </main>
    </div>
  );
}