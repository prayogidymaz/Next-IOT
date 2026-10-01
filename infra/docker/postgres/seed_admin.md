# Default admin bootstrap

The API container runs `python -m app.seed` after migrations. Preferred credentials (dev):

| Field | Value |
| --- | --- |
| Email | `admin@nextiot.com` |
| Password | `admin123` |
| Role | `super_admin` (platform superuser) |

Manual re-seed inside the API container:

```bash
docker compose exec api python -m app.seed
```

Verify login:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nextiot.com","password":"admin123"}'
```

Compose Postgres defaults: user `next_iot`, database `next_iot`, password from `POSTGRES_PASSWORD` in `.env`.
