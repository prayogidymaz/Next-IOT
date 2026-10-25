/**
 * Konfigurasi perangkat — override via build_flags (-D) atau edit lokal (jangan commit secret prod).
 */
#ifndef NEXT_OS_CONFIG_H
#define NEXT_OS_CONFIG_H

#define NEXT_OS_DEVICE_NAME "nextwatch-dev"
#define NEXT_OS_FIRMWARE_VERSION "1.0.0-dev"

/* WiFi dev defaults */
#ifndef NEXT_OS_WIFI_SSID_DEFAULT
#define NEXT_OS_WIFI_SSID_DEFAULT "NEXT-IOT-LAB"
#endif
#ifndef NEXT_OS_WIFI_PASSWORD_DEFAULT
#define NEXT_OS_WIFI_PASSWORD_DEFAULT "ganti-di-sini"
#endif
#ifndef NEXT_OS_WIFI_SSID
#define NEXT_OS_WIFI_SSID NEXT_OS_WIFI_SSID_DEFAULT
#endif
#ifndef NEXT_OS_WIFI_PASSWORD
#define NEXT_OS_WIFI_PASSWORD NEXT_OS_WIFI_PASSWORD_DEFAULT
#endif

/* MQTT / mesh (EMQX) — dev credentials */
#ifndef NEXT_OS_MQTT_BROKER_HOST
#define NEXT_OS_MQTT_BROKER_HOST "192.168.1.10"
#endif
#ifndef NEXT_OS_MQTT_BROKER
#define NEXT_OS_MQTT_BROKER NEXT_OS_MQTT_BROKER_HOST
#endif
#ifndef NEXT_OS_MQTT_BROKER_PORT
#define NEXT_OS_MQTT_BROKER_PORT 1883
#endif
#ifndef NEXT_OS_MQTT_WEBHOOK_SECRET
#define NEXT_OS_MQTT_WEBHOOK_SECRET "dev-webhook-secret"
#endif
#ifndef NEXT_OS_DEVICE_TENANT_ID
#define NEXT_OS_DEVICE_TENANT_ID "tenant-dev"
#endif
#ifndef NEXT_OS_DEVICE_ID
#define NEXT_OS_DEVICE_ID "watch-dev-1"
#endif
#ifndef NEXT_OS_DEVICE_ACCESS_TOKEN
#define NEXT_OS_DEVICE_ACCESS_TOKEN "dev-device-token"
#endif

#define NEXT_OS_MQTT_PORT NEXT_OS_MQTT_BROKER_PORT
#ifndef NEXT_OS_MQTT_USERNAME
#define NEXT_OS_MQTT_USERNAME NEXT_OS_DEVICE_ACCESS_TOKEN
#endif
#ifndef NEXT_OS_MQTT_PASSWORD
#define NEXT_OS_MQTT_PASSWORD ""
#endif

#define NEXT_OS_API_BASE_URL "http://192.168.1.10:8000"

#define NEXT_OS_DISPLAY_WIDTH 240
#define NEXT_OS_DISPLAY_HEIGHT 240

#define NEXT_OS_MESH_ALERT_BUFFER_SIZE 8

#endif /* NEXT_OS_CONFIG_H */
