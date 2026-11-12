import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import { Database } from "bun:sqlite";
import { PollEngine } from "../src/server/bus/pollEngine";
import { openDatabase, ensureDevices } from "../src/server/db";
import type { Config } from "../src/server/config";

const config: Config = {
  converter: { host: "127.0.0.1", port: 1, baudRate: 9600, dataBits: 8, parity: "odd", stopBits: 1 },
  bus: {
    pollIntervalMs: 1000,
    devices: [
      { id: "mfc-1", initialName: "MFC-1", address: "1" },
      { id: "mfc-2", initialName: "MFC-2", address: "2" },
    ],
  },
};

describe("PollEngine", () => {
  let db: Database;
  let engine: PollEngine;

  beforeEach(() => {
    db = openDatabase(":memory:");
    ensureDevices(
      db,
      config.bus.devices.map((d) => ({ id: d.id, initialName: d.initialName })),
    );
    engine = new PollEngine(db, config);
    engine.reloadDevices();
  });

  afterEach(() => {
    engine.stop();
    db.close();
  });

  test("reports offline devices when converter is down", async () => {
    engine.reloadDevices();
    const snapshots = engine.snapshots();
    expect(snapshots).toHaveLength(2);
    for (const s of snapshots) {
      expect(s.online).toBe(false);
      expect(s.status).toBe("offline");
    }
    expect(engine.getConnectionState()).toBe("offline");
  });

  test("poll device fails fast when offline", async () => {
    const device = [...engine["devices"].values()][0]!;
    const result = await engine.pollDevice(device);
    expect(result.ok).toBe(false);
    expect(result.error).toBe("offline");
  });
});