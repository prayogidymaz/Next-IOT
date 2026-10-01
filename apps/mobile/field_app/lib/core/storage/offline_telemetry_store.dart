import 'dart:convert';

import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class OfflineTelemetryStore {
  Database? _db;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await openDatabase(
      join(await getDatabasesPath(), 'field_telemetry_queue.db'),
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE pending_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            created_at TEXT NOT NULL
          )
        ''');
      },
    );
    return _db!;
  }

  Future<void> enqueue(String deviceId, Map<String, Object?> metrics) async {
    final db = await database;
    await db.insert('pending_telemetry', {
      'device_id': deviceId,
      'metrics_json': jsonEncode(metrics),
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  Future<List<Map<String, Object?>>> pendingRows({int limit = 50}) async {
    final db = await database;
    return db.query('pending_telemetry', orderBy: 'id ASC', limit: limit);
  }

  Future<void> deleteRow(int id) async {
    await deleteRows([id]);
  }

  Future<void> deleteRows(List<int> ids) async {
    if (ids.isEmpty) return;
    final db = await database;
    final placeholders = List.filled(ids.length, '?').join(',');
    await db.delete('pending_telemetry', where: 'id IN ($placeholders)', whereArgs: ids);
  }

  Future<int> pendingCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) AS c FROM pending_telemetry');
    return (result.first['c'] as int?) ?? 0;
  }
}
