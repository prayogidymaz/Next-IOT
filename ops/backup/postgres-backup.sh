#!/usr/bin/env bash
# Next-IoT PostgreSQL backup — gzip + optional age/gpg encrypt + S3-compatible upload.
set -euo pipefail

LOG_FILE="${BACKUP_LOG:-/var/log/next-iot-backup.log}"
BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/next-iot}"
RETENTION_DAILY="${RETENTION_DAILY:-7}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-4}"
RETENTION_MONTHLY="${RETENTION_MONTHLY:-3}"

PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-nextiot}"
PGDATABASE="${PGDATABASE:-nextiot}"

S3_ENDPOINT="${S3_ENDPOINT:-}"
S3_BUCKET="${S3_BUCKET:-next-iot-backups}"
S3_PREFIX="${S3_PREFIX:-postgres}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
day_of_week="$(date -u +%u)"
day_of_month="$(date -u +%d)"

mkdir -p "$BACKUP_ROOT/daily" "$BACKUP_ROOT/weekly" "$BACKUP_ROOT/monthly"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

dump_path="${BACKUP_ROOT}/daily/nextiot-${timestamp}.sql.gz"
log "Starting pg_dump to ${dump_path}"

export PGPASSWORD="${PGPASSWORD:-}"
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" | gzip -9 > "$dump_path"

if [ -n "${AGE_RECIPIENT:-}" ] && command -v age >/dev/null 2>&1; then
  age -r "$AGE_RECIPIENT" -o "${dump_path}.age" "$dump_path"
  rm -f "$dump_path"
  dump_path="${dump_path}.age"
  log "Encrypted with age: ${dump_path}"
elif [ -n "${GPG_RECIPIENT:-}" ] && command -v gpg >/dev/null 2>&1; then
  gpg --batch --yes -r "$GPG_RECIPIENT" -o "${dump_path}.gpg" -e "$dump_path"
  rm -f "$dump_path"
  dump_path="${dump_path}.gpg"
  log "Encrypted with gpg: ${dump_path}"
fi

if [ -n "$S3_ENDPOINT" ] && command -v aws >/dev/null 2>&1; then
  aws s3 cp "$dump_path" "s3://${S3_BUCKET}/${S3_PREFIX}/$(basename "$dump_path")" \
    --endpoint-url "$S3_ENDPOINT"
  log "Uploaded to s3://${S3_BUCKET}/${S3_PREFIX}/"
fi

find "$BACKUP_ROOT/daily" -type f -mtime +"$RETENTION_DAILY" -delete
if [ "$day_of_week" = "7" ]; then
  cp "$dump_path" "$BACKUP_ROOT/weekly/nextiot-${timestamp}$(echo "$dump_path" | grep -oE '\.(gz|age|gpg)$' || true)"
  find "$BACKUP_ROOT/weekly" -type f -mtime +$((RETENTION_WEEKLY * 7)) -delete
fi
if [ "$day_of_month" = "01" ]; then
  cp "$dump_path" "$BACKUP_ROOT/monthly/nextiot-${timestamp}$(echo "$dump_path" | grep -oE '\.(gz|age|gpg)$' || true)"
  find "$BACKUP_ROOT/monthly" -type f -mtime +$((RETENTION_MONTHLY * 31)) -delete
fi

log "Backup complete"
