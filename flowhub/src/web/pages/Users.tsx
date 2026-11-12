import { useCallback, useEffect, useState } from "react";
import { api, type Role, type UserRow } from "../api";

export function Users({ currentUserId }: { currentUserId: number }) {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("operator");

  const load = useCallback(() => {
    api
      .users()
      .then((result) => setUsers(result.users))
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "laden mislukt"));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function create(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await api.createUser(username, password, role);
      setUsername("");
      setPassword("");
      setRole("operator");
      load();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "aanmaken mislukt");
    }
  }

  return (
    <section>
      <div className="page-head">
        <h1>Gebruikers</h1>
      </div>
      {error && <p className="error">{error}</p>}

      <table className="grid">
        <thead>
          <tr>
            <th>Gebruiker</th>
            <th>Rol</th>
            <th>Actief</th>
            <th>Laatste login</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>
                <select
                  value={user.role}
                  disabled={user.id === currentUserId}
                  onChange={(event) => {
                    const nextRole = event.target.value === "admin" ? "admin" : "operator";
                    void api
                      .patchUser(user.id, { role: nextRole })
                      .then(load)
                      .catch((cause: unknown) =>
                        setError(cause instanceof Error ? cause.message : "wijzigen mislukt"),
                      );
                  }}
                >
                  <option value="operator">operator</option>
                  <option value="admin">admin</option>
                </select>
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={user.active}
                  disabled={user.id === currentUserId}
                  onChange={(event) => {
                    void api
                      .patchUser(user.id, { active: event.target.checked })
                      .then(load)
                      .catch((cause: unknown) =>
                        setError(cause instanceof Error ? cause.message : "wijzigen mislukt"),
                      );
                  }}
                />
              </td>
              <td className="muted">{user.last_login ?? "—"}</td>
              <td />
            </tr>
          ))}
        </tbody>
      </table>

      <article className="card">
        <h2>Nieuwe gebruiker</h2>
        <form onSubmit={create} className="grid-2">
          <label>
            Gebruikersnaam
            <input value={username} onChange={(event) => setUsername(event.target.value)} required minLength={3} />
          </label>
          <label>
            Wachtwoord (min. 10 tekens)
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={10}
            />
          </label>
          <label>
            Rol
            <select value={role} onChange={(event) => setRole(event.target.value === "admin" ? "admin" : "operator")}>
              <option value="operator">operator</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <div className="row">
            <button type="submit">Aanmaken</button>
          </div>
        </form>
      </article>
    </section>
  );
}