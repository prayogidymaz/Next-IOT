# Real Hardware Field Test Guide — Option 3

**Targets:** ESP32-S3 edge node (smartwatch / wearable) + **Orange Pi 5 Pro** (or Cyberdeck SBC) LoRa gateway  
**Stack:** Codec2 voice (1200/1300 bit/s), SX1262 LoRa, Next-IoT `lora_bridge` → API → **Cyberdeck UI** (`/cyberdeck`)

Related firmware docs: [`../firmware/lora-ptt/README.md`](../firmware/lora-ptt/README.md), [`../firmware/lora-ptt/PACKET_STRUCTURE.md`](../firmware/lora-ptt/PACKET_STRUCTURE.md)

---

## 1. Bill of materials

| Item | Role |
| --- | --- |
| ESP32-S3 DevKit (16 MB flash, 8 MB PSRAM recommended) | Edge PTT node / smartwatch MCU |
| INMP441 | I2S MEMS microphone |
| MAX98357A | I2S Class-D amplifier + speaker |
| SX1262 LoRa module (SPI) | RF link (915 MHz US / 868 MHz EU — match region) |
| Tactile PTT button | GPIO0 or custom (active LOW) |
| Orange Pi 5 Pro + USB-UART cable | Cyberdeck gateway SBC |
| USB-SX1262 dongle or second ESP32 as USB-serial gateway | Optional: serial feed into bridge |

---

## 2. Wiring schematics (ESP32-S3 edge node)

Default pin map matches [`codec2_ptt_template.ino`](../firmware/lora-ptt/codec2_ptt_template.ino). Adjust in firmware if your PCB differs.

### 2.1 INMP441 (I2S microphone)

| INMP441 | ESP32-S3 | Notes |
| --- | --- | --- |
| VDD | 3.3 V | |
| GND | GND | |
| L/R | GND | Left channel |
| **WS** (LRCLK) | **GPIO 5** | Word select |
| **SCK** (BCLK) | **GPIO 4** | Bit clock |
| **SD** (DOUT) | **GPIO 6** | Data in → ESP32 I2S RX |

### 2.2 MAX98357A (I2S amplifier)

| MAX98357A | ESP32-S3 | Notes |
| --- | --- | --- |
| VIN | 5 V (or 3.3 V per module) | |
| GND | GND | |
| **LRC** (LRCLK) | **GPIO 16** | |
| **BCLK** | **GPIO 15** | |
| **DIN** | **GPIO 7** | ESP32 I2S TX → amp |
| GAIN | leave floating or tie per module datasheet | |

Speaker: 4–8 Ω across amp `+` / `-`.

### 2.3 SX1262 (SPI LoRa)

| SX1262 | ESP32-S3 | Notes |
| --- | --- | --- |
| **NSS** (CS) | **GPIO 10** | SPI chip select |
| **SCK** | Default SPI SCK (often GPIO 12 on S3 — verify board) | |
| **MOSI** | Default SPI MOSI | |
| **MISO** | Default SPI MISO | |
| **RST** | **GPIO 12** | Reset |
| **BUSY** | **GPIO 13** | RadioLib busy |
| **DIO1** | **GPIO 11** | IRQ |
| ANT | 915/868 antenna | **Never transmit without load** |

> **Note:** If your devkit uses flash on conflicting GPIOs, move LoRa pins and update `#define` lines in firmware.

### 2.4 PTT button

| Button | ESP32-S3 |
| --- | --- |
| One leg | **GPIO 0** |
| Other leg | GND |
| Mode | `INPUT_PULLUP`, press = LOW |

---

## 3. PlatformIO build & flash (ESP32-S3 PTT firmware)

### 3.1 Project layout (recommended)

Copy the template into a PlatformIO project:

```text
apps/hardware/esp32_lora_ptt/
  platformio.ini
  src/
    main.cpp          ← from docs/firmware/lora-ptt/codec2_ptt_template.ino
  lib/
    codec2/           ← vendor Codec2 (or prebuilt lib)
```

Example **`platformio.ini`** for ESP32-S3:

```ini
[env:esp32s3_ptt]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
upload_speed = 921600
board_build.partitions = default_8MB.csv
lib_deps =
    jgromes/RadioLib@^7.1.2
    bblanchon/ArduinoJson@^7.2.0
build_flags =
    -D CORE_DEBUG_LEVEL=1
    -D LORA_FREQ_MHZ=915.0
    -D NODE_ID=\"SW-01\"
    -D LORA_CHANNEL=3
    -D CODEC2_MODE=1200
    -D ENABLE_AES_ENCRYPTION=true
    -D LORA_AES_KEY_HEX=\"00112233445566778899aabbccddeeff\"
monitor_filters = esp32_exception_decoder
```

### 3.2 Build & upload (PlatformIO)

```bash
cd apps/hardware/esp32_lora_ptt
pio run -e esp32s3_ptt
pio run -e esp32s3_ptt -t upload
pio device monitor -e esp32s3_ptt
```

### 3.3 Esptool (manual flash)

Find the built binary (PlatformIO):

- `.pio/build/esp32s3_ptt/bootloader.bin`
- `.pio/build/esp32s3_ptt/partitions.bin`
- `.pio/build/esp32s3_ptt/firmware.bin`

**Linux / Orange Pi:**

```bash
python3 -m esptool --chip esp32s3 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

**Windows (PowerShell):**

```powershell
python -m esptool --chip esp32s3 --port COM5 --baud 921600 `
  write_flash -z 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
```

Replace `COM5` / `/dev/ttyUSB0` with your USB serial port.

---

## 4. Orange Pi 5 Pro / Cyberdeck SBC setup

### 4.1 OS packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git minicom
python3 -m pip install --user pyserial httpx
```

### 4.2 Serial permissions (ttyUSB / ttyACM)

```bash
sudo usermod -aG dialout $USER
# Log out and back in, then:
ls -l /dev/ttyUSB* /dev/ttyACM*
```

If permission denied persists:

```bash
sudo chmod a+rw /dev/ttyUSB0
```

### 4.3 Environment for LoRa bridge

In repo root `.env` or `apps/api/.env`:

```env
LORA_BRIDGE_SERIAL_PORT=/dev/ttyUSB0
LORA_BRIDGE_BAUD_RATE=115200
LORA_BRIDGE_API_BASE_URL=http://127.0.0.1:8000
LORA_BRIDGE_DEFAULT_NODE_ID=SW-01
LORA_ENCRYPTION_KEY=00112233445566778899aabbccddeeff
```

On Windows gateway use `COM3` (default in `app/config.py`).

### 4.4 Run LoRa bridge service

With API stack up (`docker compose up -d`):

```bash
cd apps/api
python -m app.hardware.lora_bridge
```

Verify gateway status:

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:8000/api/v1/hardware/gateway-status
```

### 4.5 Cyberdeck UI on Orange Pi (optional kiosk)

```bash
cd apps/dashboard
flutter run -d linux
# Navigate to /cyberdeck after login
```

Or use web console on port 3000: `cd apps/web && npm run dev` → `http://<pi-ip>:3000/cyberdeck`.

---

## 5. Field test validation protocol

### Phase A — Bench (lab)

| Step | Action | Pass criteria |
| --- | --- | --- |
| A1 | Flash ESP32-S3, open serial monitor | Boot banner, no panic loops |
| A2 | Hold PTT 2 s | TX LED / log `transmitVoiceBurst` |
| A3 | Bridge reads serial line | Redis/API `gateway-status` → `serial_connected: true` |
| A4 | Send text from Cyberdeck UI | `POST .../ptt/text` → 201, log entry in Redis |

### Phase B — RF link (short range 10–50 m)

| Step | Action | Pass criteria |
| --- | --- | --- |
| B1 | Match frequency & SF/BW on both radios | Same `LORA_FREQ_MHZ`, compatible SF |
| B2 | PTT voice burst x10 | Gateway receives packets, no CRC storm |
| B3 | Measure RSSI/SNR | See §5.2 |

### Phase C — Field (100 m+ line-of-sight)

Document GPS waypoint, terrain, weather. Repeat B2 at distance steps (25 m, 50 m, 100 m).

---

## 5.1 Packet latency & Codec2 audio quality (1200 bit/s)

**Codec2 1200** target: ~40 ms frames, ~6 bytes/frame (mode dependent). Budget end-to-end:

| Segment | Typical target |
| --- | --- |
| Encode + pack | < 15 ms |
| LoRa airtime (SF7, 50 B) | 50–120 ms |
| Gateway serial + bridge | < 30 ms |
| **Round-trip PTT (edge → gateway ACK)** | **< 500 ms lab**, **< 1.5 s field** |

**Audio quality checklist (subjective MOS-style):**

1. Quiet room: speech intelligible, consonants clear.
2. Moderate wind: acceptable with mic foam; note SNR drop.
3. Compare Codec2 **1200** vs **1300** — log which mode is flashed (`CODEC2_MODE`).

**Latency script** (gateway timestamp vs edge serial log):

```bash
python3 docs/hardware/scripts/measure_ptt_latency.py --port /dev/ttyUSB0 --baud 115200
```

---

## 5.2 RSSI / SNR measurement (Cyberdeck UI)

1. Open **Flutter** `/cyberdeck` or **web** `/cyberdeck`.
2. Confirm **Node Mesh Tracker** lists `CDK-01`, `CDK-02`, `SW-01` (live API) or demo nodes.
3. Select target node → note **RSSI** (dBm) and **SNR** (dB).
4. Walk test: refresh every 15 s; record RSSI drop vs distance.

**API (automation):**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/hardware/cyberdeck/mesh | jq '.nodes[] | {label,rssi,snr,battery_pct}'
```

**Signal bands (UI colors):**

| RSSI | Quality |
| --- | --- |
| > -85 dBm | Strong (green) |
| -85 to -105 dBm | Marginal (amber) |
| < -105 dBm | Weak (red) |

---

## 6. Test scripts reference

| Script | Purpose |
| --- | --- |
| [`scripts/flash_esp32_s3.ps1`](scripts/flash_esp32_s3.ps1) | Windows esptool flash helper |
| [`scripts/flash_esp32_s3.sh`](scripts/flash_esp32_s3.sh) | Linux / Orange Pi esptool helper |
| [`scripts/measure_ptt_latency.py`](scripts/measure_ptt_latency.py) | Serial line timestamps → latency stats |
| [`scripts/orangepi_bridge_setup.sh`](scripts/orangepi_bridge_setup.sh) | dialout group + dependency check |
| [`scripts/field_test_checklist.sh`](scripts/field_test_checklist.sh) | Printable pass/fail gate for field day |

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No serial in bridge | Wrong port / permissions | `dialout`, `LORA_BRIDGE_SERIAL_PORT` |
| `lora_link: disconnected` | ESP not sending JSON lines | Check firmware UART format matches `parser.py` |
| Garbled audio | I2S pin swap / sample rate | 16 kHz mono; verify WS/BCLK |
| RSSI flat | Demo mesh only | Deploy live telemetry ingest + GPS |
| Encrypt failures | Key mismatch | Align `LORA_AES_KEY_HEX` and `LORA_ENCRYPTION_KEY` |

---

## 8. Sign-off template

| Field | Value |
| --- | --- |
| Date | |
| Location | |
| Firmware git SHA | |
| Edge node ID | |
| Gateway SBC | Orange Pi 5 Pro / other |
| Max range LOS (m) | |
| RSSI @ max range | |
| Codec2 mode | 1200 / 1300 |
| Tester | |

**Approved for ops:** ☐ Yes ☐ No — notes: ___________________
