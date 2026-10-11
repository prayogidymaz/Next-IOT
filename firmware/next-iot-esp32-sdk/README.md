# Next-IOT ESP32 SDK

PlatformIO / Arduino library for ESP32 devices connecting to Next-IOT.

## Quick start

See `examples/basic_telemetry/basic_telemetry.ino`.

## Topics

- Telemetry publish: `tenants/{tenant_id}/devices/{device_id}/telemetry`
- Client attributes: `tenants/{tenant_id}/devices/{device_id}/attributes`
- RPC response: `tenants/{tenant_id}/devices/{device_id}/commands/{request_id}/response`
- Subscribe shared attributes: `.../attributes/shared/update`
- Subscribe RPC: `.../commands/+/request`
- OTA: `.../ota/update`
