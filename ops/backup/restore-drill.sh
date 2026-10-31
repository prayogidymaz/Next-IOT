#!/usr/bin/env bash
# Monthly restore drill — download latest backup, restore to temp Postgres, verify row count.
set -euo pipefail

LOG_FILE="${BACKUP_LOG:-/var/log/next-iot-restore-drill.log}"
BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/next-iot}"
CONTAINER_NAME="${DRILL_CONTAINER:-nextiot-restore-drill}"
WEBHOOK_URL="${RESTORE_DRILL_WEBHOOK:-}"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

latest="$(ls -1t "$BACKUP_ROOT/daily"/nextiot-* 2>/dev/null | head -1 || true)"
if [ -z "$latest" ]; then
  log "No backup found under ${BACKUP_ROOT}/daily"
  exit 1
fi

log "Using backup: $latest"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

if [[ "$latest" == *.age ]]; then
  age -d -o "$work/restore.sql.gz" "$latest"
elif [[ "$latest" == *.gpg ]]; then
  gpg -d -o "$work/restore.sql.gz" "$latest"
else
  cp "$latest" "$work/restore.sql.gz"
fi

gunzip -c "$work/restore.sql.gz" > "$work/restore.sql"

docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d --name "$CONTAINER_NAME" \
  -e POSTGRES_USER=drill \
  -e POSTGRES_PASSWORD=drill \
  -e POSTGRES_DB=drill \
  postgres:16

sleep 8
docker exec -i "$CONTAINER_NAME" psql -U drill -d drill < "$work/restore.sql"

row_count="$(docker exec "$CONTAINER_NAME" psql -U drill -d drill -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")"
log "Public tables after restore: ${row_count}"

docker rm -f "$CONTAINER_NAME" >/dev/null

if [ -n "$WEBHOOK_URL" ]; then
  curl -fsS -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"Next-IoT restore drill OK — public tables: ${row_count}\"}"
fi

log "Restore drill complete"
