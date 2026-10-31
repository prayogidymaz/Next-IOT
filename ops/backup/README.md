# PostgreSQL backup & disaster recovery

## Scripts

| Script | Purpose |
|--------|---------|
| `postgres-backup.sh` | Daily `pg_dump`, gzip, optional `age`/`gpg`, upload to S3-compatible storage |
| `restore-drill.sh` | Monthly restore into ephemeral Postgres container + webhook report |

## Environment variables

- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `BACKUP_ROOT` (default `/var/backups/next-iot`)
- `S3_ENDPOINT`, `S3_BUCKET`, `S3_PREFIX` + AWS CLI credentials for B2/R2/MinIO
- `AGE_RECIPIENT` or `GPG_RECIPIENT` for encryption at rest
- `RESTORE_DRILL_WEBHOOK` — Discord/Slack incoming webhook

## Crontab example

```cron
0 2 * * * /opt/next-iot/ops/backup/postgres-backup.sh
0 4 1 * * /opt/next-iot/ops/backup/restore-drill.sh
```

## Recovery runbook

1. Stop API workers writing to the database (`docker compose stop api worker`).
2. Identify backup object in object storage or `BACKUP_ROOT/daily`.
3. Decrypt if needed (`age -d` / `gpg -d`), then `gunzip`.
4. Create fresh database or drop connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='nextiot';`
5. `psql -U nextiot -d nextiot -f restore.sql` (or `docker exec -i postgres psql ...`).
6. Run `alembic upgrade head` only if backup predates schema — prefer backup taken after migrations.
7. Smoke test: `curl /health/ready`, login, one tenant-scoped read.
8. Resume services and monitor error rate in Grafana.

## Rotation policy

- **7** daily copies in `daily/`
- **4** weekly copies (Sunday run copied to `weekly/`)
- **3** monthly copies (1st of month copied to `monthly/`)
