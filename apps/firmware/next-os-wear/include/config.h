/**
 * Konfigurasi perangkat — isi credential asli via build flag atau secrets lokal.
 * JANGAN commit password produksi ke git.
 */
#ifndef NEXT_OS_CONFIG_H
#define NEXT_OS_CONFIG_H

#define NEXT_OS_DEVICE_NAME "nextwatch-dev"
#define NEXT_OS_FIRMWARE_VERSION "1.0.0-dev"

/* WiFi placeholder (ganti di secrets atau platformio build_flags) */
#ifndef NEXT_OS_WIFI_SSID
#define NEXT_OS_WIFI_SSID "NEXT-IOT-LAB"
#endif
#ifndef NEXT_OS_WIFI_PASSWORD
#define NEXT_OS_WIFI_PASSWORD "ganti-di-sini"
#endif

/* MQTT / API placeholder — di-wire Week 7-10 */
#ifndef NEXT_OS_MQTT_BROKER
#define NEXT_OS_MQTT_BROKER "192.168.1.10"
#endif
#define NEXT_OS_MQTT_PORT 1883
#define NEXT_OS_MQTT_USERNAME ""
#define NEXT_OS_MQTT_PASSWORD ""

#define NEXT_OS_API_BASE_URL "http://192.168.1.10:8000"

/* Layar T-Watch S3 round */
#define NEXT_OS_DISPLAY_WIDTH 240
#define NEXT_OS_DISPLAY_HEIGHT 240

#endif /* NEXT_OS_CONFIG_H */
