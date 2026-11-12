import { useCallback, useEffect, useState } from "react";
import { api, type AuditEntry } from "../api";

export function Audit() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback((rows: number, skip: number) => {
    setBusy(true);
    api
      .audit(rows, skip)
      .then((result) => {
        setEntries(result.audit);
        setHasMore(result.hasMore);
      })
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "laden mislukt"))
      .finally(() => setBusy(false));
  }, []);

  useEffect(() => {
    load(limit, offset);
  }, [load, limit, offset]);

  return (
    <section>
      <div className="page-head">
        <h1>Auditlog</h1>
        <div className="row">
          <label className="inline">
            Regels
            <select
              value={String(limit)}
              onChange={(event) => {
                setOffset(0);
                setLimit(Number(event.target.value));
              }}
            >
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

      <div className="row pager">
        <button
          type="button"
          className="secondary"
          disabled={offset === 0 || busy}
          onClick={() => setOffset(Math.max(0, offset - limit))}
        >
          Vorige
        </button>
        <span className="muted small">
          regels {offset + 1}–{offset + entries.length}
        </span>
        <button
          type="button"
          className="secondary"
          disabled={!hasMore || busy}
          onClick={() => setOffset(offset + limit)}
        >
          Volgende
        </button>
      </div>
    </section>
  );
}