# Hardware BOM (Smart Agriculture)

| Node | MCU | Radio | Sensors | Target price |
|------|-----|-------|---------|--------------|
| Soil moisture | ESP32-S3 | SX1262 LoRaWAN | Capacitive moisture + DS18B20 | Rp 300k–600k |
| Weather | ESP32-S3 | SX1262 | BME280 + anemometer + rain gauge | Rp 800k–1.2jt |
| Irrigation | ESP32 | SX1262 | Relay + solenoid | Rp 400k–700k |
| NPK/pH | ESP32-S3 | SX1262 | RS485 NPK + pH probe | Rp 1–1.5jt |

Battery: 2×AA Li-SOCl2 or LiFePO4 + solar for weather nodes. Sleep target &lt; 50 µA.
