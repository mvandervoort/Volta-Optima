import { Database } from "bun:sqlite";
import { existsSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const dataDir = process.env.FLOWHUB_DATA_DIR ?? "./data";
const dbPath = process.env.FLOWHUB_DB ?? join(dataDir, "flowhub.db");
const backupDir = process.env.FLOWHUB_BACKUP_DIR ?? "./backups";
const retention = Number(process.env.FLOWHUB_BACKUP_RETENTION ?? "14");

function fail(message: string): never {
  console.error(`backup: ${message}`);
  process.exit(1);
}

if (!existsSync(dbPath)) fail(`database not found at ${dbPath}`);

mkdirSync(backupDir, { recursive: true });

const stamp = new Date().toISOString().replace(/[:.]/g, "-");
const target = join(backupDir, `flowhub-${stamp}.db`);

if (existsSync(target)) fail(`backup target already exists: ${target}`);

const db = new Database(dbPath, { readonly: true });
try {
  db.exec(`VACUUM INTO '${target.replace(/'/g, "''")}'`);
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
} finally {
  db.close();
}

console.log(`backup: wrote ${target}`);

if (Number.isFinite(retention) && retention > 0) {
  const backups = readdirSync(backupDir)
    .filter((name) => /^flowhub-.*\.db$/.test(name))
    .sort();
  const excess = backups.slice(0, Math.max(0, backups.length - retention));
  for (const name of excess) {
    rmSync(join(backupDir, name), { force: true });
    console.log(`backup: pruned ${name}`);
  }
}