import { useCallback, useEffect, useState } from "react";
import { api, type AuditEntry } from "../api";

export function Audit() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(200);

  const load = useCallback((rows: number) => {
    api
      .audit(rows)
      .then((result) => setEntries(result.audit))
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "laden mislukt"));
  }, []);

  useEffect(() => {
    load(limit);
  }, [load, limit]);

  return (
    <section>
      <div className="page-head">
        <h1>Auditlog</h1>
        <div className="row">
          <label className="inline">
            Regels
            <select value={String(limit)} onChange={(event) => setLimit(Number(event.target.value))}>
              <option value="50">50</option>
              <option value="200">200</option>
              <option value="500">500</option>
            </select>
          </label>
          <a href="/api/v1/audit/export.csv">CSV exporteren</a>
        </div>
      </div>

      {error && <p className="error">{error}</p>}

      <table className="grid">
        <thead>
          <tr>
            <th>Tijd</th>
            <th>Gebruiker</th>
            <th>Rol</th>
            <th>Actie</th>
            <th>Device</th>
            <th>Veld</th>
            <th>Oud</th>
            <th>Nieuw</th>
            <th>OK</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id}>
              <td className="muted">{entry.ts}</td>
              <td>{entry.username}</td>
              <td>{entry.role}</td>
              <td>{entry.action}</td>
              <td>{entry.device_id ?? "—"}</td>
              <td>{entry.field ?? "—"}</td>
              <td className="mono">{entry.old_value ?? "—"}</td>
              <td className="mono">{entry.new_value ?? "—"}</td>
              <td>{entry.success === 1 ? "ja" : "nee"}</td>
              <td className="muted">{entry.detail ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}