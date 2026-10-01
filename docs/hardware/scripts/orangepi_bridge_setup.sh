#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Packages"
sudo apt update
sudo apt install -y python3-pip python3-venv minicom
python3 -m pip install --user pyserial httpx

echo "[2/4] dialout group"
sudo usermod -aG dialout "$USER" || true

echo "[3/4] Serial devices"
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "No USB serial yet — plug gateway dongle"

echo "[4/4] Suggested env"
cat <<'EOF'
export LORA_BRIDGE_SERIAL_PORT=/dev/ttyUSB0
export LORA_BRIDGE_BAUD_RATE=115200
export LORA_BRIDGE_API_BASE_URL=http://127.0.0.1:8000
EOF

echo "Log out/in for group changes. Then: cd apps/api && python -m app.hardware.lora_bridge"
