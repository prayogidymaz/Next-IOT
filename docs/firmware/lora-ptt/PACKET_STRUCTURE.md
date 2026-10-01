# LoRa PTT Packet Structure

All multi-byte integers are **little-endian** unless noted.

## Header (fixed 24 bytes)

| Offset | Size | Field | Description |
| --- | --- | --- | --- |
| 0 | 1 | `version` | Protocol version (`0x01`) |
| 1 | 1 | `msg_type` | `0x01=PTT_VOICE`, `0x02=TEXT`, `0x03=BEACON` |
| 2 | 1 | `flags` | bit0 encrypted, bit1 GPS valid, bit2 emergency |
| 3 | 1 | `channel` | LoRa channel index 1–8 |
| 4 | 4 | `sender_id` | CRC32 of node string ID (or uint32 assigned ID) |
| 8 | 4 | `target_id` | `0xFFFFFFFF` = broadcast mesh |
| 12 | 4 | `latitude_e7` | int32, degrees × 1e7 (optional) |
| 16 | 4 | `longitude_e7` | int32, degrees × 1e7 (optional) |
| 20 | 2 | `seq` | uint16 sequence counter |
| 22 | 2 | `payload_len` | uint16 audio/text bytes following header |

## Voice payload

| Field | Size | Notes |
| --- | --- | --- |
| `codec2_mode` | 1 | e.g. `0x02` = 1300 bit/s |
| `frame_count` | 1 | Number of Codec2 frames in packet |
| `audio[]` | N | Concatenated Codec2 frames (typically 40–80 bytes each) |

## Text payload

| Field | Size | Notes |
| --- | --- | --- |
| `utf8_text` | ≤160 | Encrypted when `flags.encrypted` set |

## Beacon payload

| Field | Size | Notes |
| --- | --- | --- |
| `severity` | 1 | 0 info, 1 warning, 2 critical |
| `battery_pct` | 1 | 0–100 |

## Max airtime guidance

- Keep total packet ≤ **255 bytes** for SF7/SF9 urban mesh unless ADR allows larger.
- PTT voice: send 1–3 Codec2 frames per PTT press; release button sends `msg_type=PTT_VOICE` with `frame_count=0` as TX end marker (optional).
