import type { DeviceSnapshot } from "../api";

function statusLabel(device: DeviceSnapshot): string {
  switch (device.status) {
    case "online":
      return "online";
    case "stale":
      return "verouderd";
    case "fault":
      return "fout";
    default:
      return "offline";
  }
}

function sourceLabel(source: DeviceSnapshot["setpointSource"]): string {
  switch (source) {
    case "analog":
      return "analoog";
    case "digital":
      return "digitaal";
    default:
      return "onbekend";
  }
}

function value(value: number | null, unit: string | null): string {
  if (value === null || value === undefined) return "—";
  return `${value.toFixed(2)}${unit ? ` ${unit}` : ""}`;
}

export function Dashboard({
  devices,
  onRefresh,
  isAdmin,
}: {
  devices: DeviceSnapshot[];
  onRefresh: () => void;
  isAdmin: boolean;
}) {
  const analogActive = devices.some((device) => device.setpointSource === "analog");

  return (
    <section>
      <div className="page-head">
        <h1>Devices</h1>
        <button type="button" onClick={onRefresh}>
          Verversen
        </button>
      </div>

      {analogActive && (
        <p className="warn">
          Let op: bij minimaal één device staat de setpoint-bron op <strong>analoog</strong>. Een
          digitale setpoint kan daar worden overruled door de analoge ingang.
        </p>
      )}

      {devices.length === 0 ? (
        <p className="muted">Geen devices geconfigureerd.</p>
      ) : (
        <table className="grid">
          <thead>
            <tr>
              <th>Naam</th>
              <th>Adres</th>
              <th>Status</th>
              <th>Flow</th>
              <th>Setpoint</th>
              <th>Bron</th>
              <th>Temperatuur</th>
              <th>Laatst gezien</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {devices.map((device) => (
              <tr key={device.id} className={`status-${device.status}`}>
                <td>{device.name}</td>
                <td className="mono">{device.address}</td>
                <td>{statusLabel(device)}</td>
                <td>{value(device.flow, device.unit)}</td>
                <td>
                  {value(device.setpoint, device.setpointUnit)}
                  {device.setpointScaled !== null && device.flowUnit !== null && (
                    <span className="muted small"> ({value(device.setpointScaled, device.flowUnit)})</span>
                  )}
                </td>
                <td className={device.setpointSource === "analog" ? "warn" : undefined}>
                  {sourceLabel(device.setpointSource)}
                </td>
                <td>{value(device.temperature, null)}</td>
                <td className="muted">{device.lastSeen ?? "—"}</td>
                <td>
                  <a href={`#/devices/${device.id}`}>Openen</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!isAdmin && (
        <p className="muted small">
          Je bent operator. Je kunt setpoints schrijven en de klep bedienen; apparaatconfiguratie en
          gebruikersbeheer zijn admin-only.
        </p>
      )}
    </section>
  );
}