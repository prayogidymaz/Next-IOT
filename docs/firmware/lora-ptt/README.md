# LoRa Push-To-Talk (PTT) — ESP32-S3 Firmware Guide

Target hardware: **ESP32-S3** Cyberdeck or smartwatch form factor with:

- **INMP441** I2S microphone
- **MAX98357A** I2S DAC + speaker
- **SX126x / LLCC68** LoRa radio module
- Optional GPS (NEO-6M / u-blox)

## Audio path — Codec2

Use **Codec2** (700C / 1300 bit/s modes recommended for LoRa bandwidth) to compress PCM frames before LoRa TX.

| Stage | Component |
| --- | --- |
| Capture | INMP441 → I2S RX @ 16 kHz mono |
| Encode | Codec2 `codec2_encode()` → ~40 byte frames (mode dependent) |
| RF | LoRa packet with PTT header + encrypted payload |
| Decode | `codec2_decode()` → I2S TX → MAX98357A |

See `codec2_ptt_template.ino` for Arduino-style skeleton and `PACKET_STRUCTURE.md` for wire format.

## Security

- Align with Next-IoT `LORA_ENCRYPTION_KEY` / AES-GCM envelope used by `lora_bridge.py`.
- Text/beacon frames should set `flags.encrypted = 1`.

## Next-IoT integration

- Bridge publishes telemetry to `POST /api/v1/telemetry`.
- Operator UI: Flutter `/cyberdeck` and web `/cyberdeck`.
- Dispatch APIs: `/api/v1/hardware/cyberdeck/ptt/text`, `/ptt/beacon`.

## Field test (Option 3)

See **[Real Hardware Field Test Guide](../../hardware/field_test_guide.md)** for ESP32-S3 + Orange Pi 5 Pro wiring, flash, and RSSI/latency protocol.
