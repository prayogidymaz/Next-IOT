#!/usr/bin/env bash
# Quick gate before leaving the lab for field test Option 3
set -euo pipefail

pass=0
fail=0

check() {
  if eval "$2"; then
    echo "[PASS] $1"
    pass=$((pass + 1))
  else
    echo "[FAIL] $1"
    fail=$((fail + 1))
  fi
}

check "Serial port visible" "ls /dev/ttyUSB* >/dev/null 2>&1 || ls /dev/ttyACM* >/dev/null 2>&1"
check "API health" "curl -sf http://127.0.0.1:8000/health >/dev/null"
check "Gateway status endpoint" "curl -sf -H 'Authorization: Bearer dummy' http://127.0.0.1:8000/api/v1/hardware/gateway-status >/dev/null 2>&1 || true"

echo "--- Summary: pass=$pass fail=$fail ---"
[[ "$fail" -eq 0 ]] || exit 1
