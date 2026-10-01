#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-/dev/ttyUSB0}"
BUILD_DIR="${2:-../../apps/hardware/esp32_lora_ptt/.pio/build/esp32s3_ptt}"

BOOT="$BUILD_DIR/bootloader.bin"
PART="$BUILD_DIR/partitions.bin"
APP="$BUILD_DIR/firmware.bin"

for f in "$BOOT" "$PART" "$APP"; do
  [[ -f "$f" ]] || { echo "Missing $f"; exit 1; }
done

python3 -m esptool --chip esp32s3 --port "$PORT" --baud 921600 \
  write_flash -z 0x0 "$BOOT" 0x8000 "$PART" 0x10000 "$APP"

echo "Flash complete on $PORT"
