import type { Database } from "bun:sqlite";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const migrationsDir = join(import.meta.dirname, "migrations");

export type Migration = {
  version: number;
  name: string;
  sql: string;
};

function parseVersion(filename: string): number | null {
  const match = filename.match(/^(\d+)_/);
  return match ? Number(match[1]!) : null;
}

export function listMigrations(): Migration[] {
  if (!existsSync(migrationsDir)) return [];
  return readdirSync(migrationsDir)
    .filter((f) => f.endsWith(".sql"))
    .map((filename) => {
      const version = parseVersion(filename);
      if (version === null) return null;
      const sql = readFileSync(join(migrationsDir, filename), "utf8");
      return { version, name: filename, sql };
    })
    .filter((m): m is Migration => m !== null)
    .sort((a, b) => a.version - b.version);
}

function getSchemaVersion(db: Database): number {
  try {
    const row = db
      .query<{ value: string }, []>("SELECT value FROM settings WHERE key = 'schema_version'")
      .get();
    if (!row) return 0;
    return Number(row.value) || 0;
  } catch {
    return 0;
  }
}

export function runMigrations(db: Database): void {
  const migrations = listMigrations();
  let version = getSchemaVersion(db);
  for (const migration of migrations) {
    if (migration.version <= version) continue;
    db.exec("BEGIN");
    try {
      db.exec(migration.sql);
      db.run(
        `INSERT INTO settings (key, value) VALUES ('schema_version', ?)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value`,
        [String(migration.version)],
      );
      db.exec("COMMIT");
      version = migration.version;
    } catch (error) {
      db.exec("ROLLBACK");
      throw error;
    }
  }
}
