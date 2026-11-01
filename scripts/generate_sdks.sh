#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENAPI_URL="${OPENAPI_URL:-http://localhost:8000/openapi.json}"
CLI="${OPENAPI_GENERATOR_CLI:-openapi-generator-cli}"

mkdir -p "$ROOT/sdks/python" "$ROOT/sdks/typescript"

$CLI generate -i "$OPENAPI_URL" -g python -o "$ROOT/sdks/python" \
  --additional-properties=packageName=next_iot_sdk,projectName=next-iot-python-sdk

$CLI generate -i "$OPENAPI_URL" -g typescript-fetch -o "$ROOT/sdks/typescript" \
  --additional-properties=npmName=@next-iot/sdk,npmVersion=0.1.0,supportsES6=true

echo "SDKs written to sdks/python and sdks/typescript"
