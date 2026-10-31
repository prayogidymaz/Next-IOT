# Observability runbook

## Stack

- **Metrics:** Prometheus scrapes `GET /metrics` on the API (plus postgres_exporter, cAdvisor, EMQX when enabled).
- **Dashboards:** Grafana on port **3030** (see `docker-compose.observability.yml`).
- **Logs:** Structured JSON from `app.observability.logging_config` with `X-Request-ID` correlation; Loki via Promtail optional.

## Health endpoints

| Route | Use |
|-------|-----|
| `/health/live` | Process up — use for liveness probe |
| `/health/ready` | DB + Redis + MQTT + migrations — readiness |
| `/health/startup` | One-shot bootstrap validation |

Legacy `/health` may still exist; prefer `/health/ready` for orchestration.

## Incident response

1. **Acknowledge** alert (Pager/Discord/Slack).
2. **Triage** Grafana *Next-IoT Overview* — error rate, latency, traffic drop.
3. **Correlate** logs in Loki or container logs using `request_id` from the failing request.
4. **Mitigate** — scale, restart unhealthy dependency, disable feature flag if applicable.
5. **Document** timeline + root cause in post-incident note.

## Common alerts

| Symptom | Likely cause | First actions |
|---------|--------------|---------------|
| High 5xx rate | DB pool exhaustion, bad deploy | Check `/health/ready`, recent deploy, Postgres connections panel |
| Latency p95 spike | N+1 queries, Redis down | Redis panel, slow query logs |
| `device_message_total` flat | EMQX/MQTT bridge | EMQX dashboard, broker connectivity |
| `workflow_fired_total` drop | Worker not consuming | Worker logs, queue depth |
| Postgres connections max | Connection leak / missing pool config | Restart API, review session usage |

## Metric reference

| Metric | Type | Description |
|--------|------|-------------|
| `workflow_fired_total` | Counter | Mesh workflow executions (`tenant_id`, `status`) |
| `device_message_total` | Counter | Ingested device/telemetry messages (`tenant_id`, `domain`) |
| `anomaly_detected_total` | Counter | Telemetry anomalies (`tenant_id`, `severity`) |
| `api_request_duration_seconds` | Histogram | HTTP latency by method, path template, status |
| `http_requests_total` | Counter | From prometheus-fastapi-instrumentator (if installed) |

## Dashboard glossary

- **Overview:** Golden signals for the HTTP API.
- **Mesh:** Device throughput and workflow/anomaly counters.
- **Infra:** Postgres, containers, Redis (when exported).

## OpenTelemetry (optional)

Set `OTEL_ENABLED=1` and run a collector (Jaeger/Tempo on `localhost:4317`). SQLAlchemy instrumentation uses the async engine’s sync bridge when available.
