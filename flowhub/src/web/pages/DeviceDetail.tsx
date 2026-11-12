import { useCallback, useEffect, useState } from "react";
import { api, type DeviceInfo, type DeviceSnapshot } from "../api";

export function DeviceDetail({
  deviceId,
  isAdmin,
  onSaved,
}: {
  deviceId: number;
  isAdmin: boolean;
  onSaved: () => void;
}) {
  const [device, setDevice] = useState<DeviceSnapshot | null>(null);
  const [info, setInfo] = useState<DeviceInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(() => {
    api
      .device(deviceId)
      .then((result) => {
        setDevice(result.device);
        setInfo(result.info);
      })
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "laden mislukt"));
  }, [deviceId]);

  useEffect(() => {
    load();
  }, [load]);

  const run = useCallback(
    async (action: () => Promise<unknown>, message: string) => {
      setError(null);
      setNotice(null);
      try {
        await action();
        setNotice(message);
        load();
        onSaved();
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "actie mislukt");
      }
    },
    [load, onSaved],
  );

  if (error !== null && device === null) return <p className="error">{error}</p>;
  if (device === null) return <p className="loading">Laden…</p>;

  return (
    <section>
      <div className="page-head">
        <div>
          <h1>{device.name}</h1>
          <p className="muted">
            adres <span className="mono">{device.address}</span> · status {device.status}
          </p>
        </div>
        <a href="#/">Terug</a>
      </div>

      {notice && <p className="ok">{notice}</p>}
      {error && <p className="error">{error}</p>}

      <div className="cards">
        <article className="card">
          <h2>Proceswaarden</h2>
          <dl>
            <dt>Flow</dt>
            <dd>{device.flow?.toFixed(2) ?? "—"} {device.unit ?? ""}</dd>
            <dt>Setpoint</dt>
            <dd>{device.setpoint?.toFixed(2) ?? "—"} {device.setpointUnit ?? ""}</dd>
            <dt>Temperatuur</dt>
            <dd>{device.temperature?.toFixed(2) ?? "—"}</dd>
            <dt>Valve override</dt>
            <dd>{device.valvePosition ?? "—"}</dd>
            <dt>Laatst gezien</dt>
            <dd className="muted">{device.lastSeen ?? "—"}</dd>
          </dl>
        </article>

        <SetpointCard device={device} run={run} />
        <ValveCard device={device} run={run} />

        {isAdmin && <DeviceConfigCard device={device} info={info} run={run} />}
      </div>
    </section>
  );
}

function SetpointCard({
  device,
  run,
}: {
  device: DeviceSnapshot;
  run: (action: () => Promise<unknown>, message: string) => Promise<void>;
}) {
  const [value, setValue] = useState(device.setpoint?.toString() ?? "");
  const [unit, setUnit] = useState<"percent" | "engineering">("percent");
  const [confirming, setConfirming] = useState(false);

  return (
    <article className="card">
      <h2>Setpoint schrijven</h2>
      <label>
        Waarde
        <input value={value} onChange={(event) => setValue(event.target.value)} inputMode="decimal" />
      </label>
      <label>
        Eenheid
        <select value={unit} onChange={(event) => setUnit(event.target.value === "engineering" ? "engineering" : "percent")}>
          <option value="percent">procent</option>
          <option value="engineering">engineering</option>
        </select>
      </label>

      {!confirming ? (
        <button type="button" onClick={() => setConfirming(true)} disabled={value.trim() === ""}>
          Setpoint wijzigen
        </button>
      ) : (
        <div className="confirm">
          <p>
            Bevestig: setpoint wordt <strong>{value} {unit}</strong> op {device.name}.
          </p>
          <button
            type="button"
            onClick={() => {
              setConfirming(false);
              void run(() => api.setpoint(device.id, Number(value), unit), "Setpoint geschreven");
            }}
          >
            Bevestigen
          </button>
          <button type="button" className="secondary" onClick={() => setConfirming(false)}>
            Annuleren
          </button>
        </div>
      )}
    </article>
  );
}

function ValveCard({
  device,
  run,
}: {
  device: DeviceSnapshot;
  run: (action: () => Promise<unknown>, message: string) => Promise<void>;
}) {
  return (
    <article className="card">
      <h2>Klep-bediening</h2>
      <p className="muted small">Elke actie wordt gelogd.</p>
      <div className="row">
        {(["normal", "open", "closed"] as const).map((mode) => (
          <button
            key={mode}
            type="button"
            onClick={() => {
              const label = mode === "normal" ? "normaal" : mode === "open" ? "open" : "gesloten";
              if (window.confirm(`Klep op ${label} zetten voor ${device.name}?`)) {
                void run(() => api.valveOverride(device.id, mode), `Klep: ${label}`);
              }
            }}
          >
            {mode}
          </button>
        ))}
      </div>
    </article>
  );
}

function DeviceConfigCard({
  device,
  info,
  run,
}: {
  device: DeviceSnapshot;
  info: DeviceInfo | null;
  run: (action: () => Promise<unknown>, message: string) => Promise<void>;
}) {
  const [name, setName] = useState(device.name);
  const [enabled, setEnabled] = useState(true);
  const [pollIntervalMs, setPollIntervalMs] = useState(1000);
  const [flowUnit, setFlowUnit] = useState(String(info?.flow_unit ?? ""));
  const [tempUnit, setTempUnit] = useState(String(info?.temp_unit ?? ""));
  const [setpointSource, setSetpointSource] = useState<"analog" | "digital">("digital");

  return (
    <article className="card wide">
      <h2>Apparaatconfiguratie (admin)</h2>
      <p className="warn">
        Let op: analoge of digitale setpoint-source kan bediening overrulen. Wijzigingen worden gelogd met oude en nieuwe waarde.
      </p>
      <div className="grid-2">
        <label>
          Naam
          <input value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <label>
          Poll-interval (ms)
          <input
            value={String(pollIntervalMs)}
            inputMode="numeric"
            onChange={(event) => setPollIntervalMs(Number(event.target.value) || 1000)}
          />
        </label>
        <label>
          Flow-unit
          <input value={flowUnit} inputMode="numeric" onChange={(event) => setFlowUnit(event.target.value)} />
        </label>
        <label>
          Temperatuur-unit
          <input value={tempUnit} inputMode="numeric" onChange={(event) => setTempUnit(event.target.value)} />
        </label>
        <label>
          Setpoint-source
          <select value={setpointSource} onChange={(event) => setSetpointSource(event.target.value === "analog" ? "analog" : "digital")}>
            <option value="digital">digitaal</option>
            <option value="analog">analog</option>
          </select>
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} />
          Inschakelen
        </label>
      </div>

      <p className="muted small">
        Write-protect (#128) wordt niet ondersteund door de 5850S en is daarom niet instelbaar.
      </p>

      <div className="row">
        <button
          type="button"
          onClick={() =>
            void run(
              () => api.patchDevice(device.id, { name, enabled, pollIntervalMs }),
              "Apparaatinstellingen opgeslagen",
            )
          }
        >
          Instellingen opslaan
        </button>
        <button
          type="button"
          className="secondary"
          onClick={() => {
            if (window.confirm("Configuratie naar het apparaat schrijven?")) {
              void run(
                () =>
                  api.writeConfig(device.id, {
                    flowUnit: Number(flowUnit),
                    tempUnit: Number(tempUnit),
                    setpointSource,
                  }),
                "Configuratie geschreven",
              );
            }
          }}
        >
          Configuratie schrijven
        </button>
        <button type="button" className="secondary" onClick={() => void run(() => api.refresh(device.id), "Verversen gestart")}>
          Nu verversen
        </button>
      </div>
    </article>
  );
}