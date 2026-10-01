#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

echo "==> Next-IOT production deploy"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy from .env.production.example"
  exit 1
fi

# shellcheck disable=SC1090
set -a && source "$ENV_FILE" && set +a

mkdir -p infra/certs infra/mqtt

if [[ ! -f infra/mqtt/passwords ]]; then
  echo "==> Creating Mosquitto password file"
  docker run --rm -v "$ROOT/infra/mqtt:/mosquitto/config" eclipse-mosquitto:2 \
    mosquitto_passwd -b -c /mosquitto/config/passwords "${MQTT_USERNAME:-iot_bridge}" "${MQTT_PASSWORD:-changeme}"
fi

if [[ ! -f infra/certs/fullchain.pem ]]; then
  echo "==> Generating self-signed TLS cert (replace with real certs for production)"
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout infra/certs/privkey.pem \
    -out infra/certs/fullchain.pem \
    -subj "/CN=${PUBLIC_HOST:-localhost}"
fi

echo "==> Validate compose"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null

echo "==> Build images"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

echo "==> Start stack"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo "==> Wait for API health"
for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${PROXY_HTTP_PORT:-80}/health" >/dev/null; then
    echo "Health OK"
    exit 0
  fi
  sleep 3
done

echo "Health check failed — inspect: docker compose -f $COMPOSE_FILE logs api proxy"
exit 1
