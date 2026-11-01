import * as SQLite from "expo-sqlite";

export type QueuedAction = {
  id: number;
  kind: string;
  payload_json: string;
  created_at: string;
};

let db: SQLite.SQLiteDatabase | null = null;

async function database(): Promise<SQLite.SQLiteDatabase> {
  if (db) return db;
  db = await SQLite.openDatabaseAsync("next_iot_field.db");
  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS offline_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL,
      payload_json TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
  `);
  return db;
}

export async function enqueueOfflineAction(kind: string, payload: Record<string, unknown>): Promise<void> {
  const conn = await database();
  await conn.runAsync(
    "INSERT INTO offline_queue (kind, payload_json, created_at) VALUES (?, ?, ?)",
    kind,
    JSON.stringify(payload),
    new Date().toISOString(),
  );
}

export async function peekOfflineActions(limit = 20): Promise<QueuedAction[]> {
  const conn = await database();
  return conn.getAllAsync<QueuedAction>(
    "SELECT id, kind, payload_json, created_at FROM offline_queue ORDER BY id ASC LIMIT ?",
    limit,
  );
}

export async function removeOfflineAction(id: number): Promise<void> {
  const conn = await database();
  await conn.runAsync("DELETE FROM offline_queue WHERE id = ?", id);
}
