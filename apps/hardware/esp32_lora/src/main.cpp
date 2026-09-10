/**
 * ESP32 LoRa Gateway — reads GPS NMEA + telemetry, emits compact JSON over LoRa TX.
 * Target boards: Heltec WiFi LoRa 32 V3 / LilyGO T-Beam (SX1262 or SX127x).
 *
 * USB serial output mirrors each LoRa payload for the Python lora_bridge worker.
 */

#include <Arduino.h>
#include <ArduinoJson.h>
#include <TinyGPSPlus.h>

#ifndef NODE_ID
#define NODE_ID "DRONE-01"
#endif

#ifndef LORA_FREQ_MHZ
#define LORA_FREQ_MHZ 915.0
#endif

#ifndef LORA_TX_INTERVAL_MS
#define LORA_TX_INTERVAL_MS 1000
#endif

static const uint8_t GPS_RX_PIN = 34;
static const uint8_t GPS_TX_PIN = 12;

HardwareSerial GPSSerial(1);
TinyGPSPlus gps;

// Placeholder radio hooks — replace with RadioLib / Heltec LoRa API for your board.
static float lastRssi = -90.0f;
static float lastSnr = 8.0f;

struct TelemetryFrame {
  double lat;
  double lon;
  double alt;
  float battery;
  float rssi;
  float snr;
};

static TelemetryFrame readTelemetry() {
  TelemetryFrame frame{};
  if (gps.location.isValid()) {
    frame.lat = gps.location.lat();
    frame.lon = gps.location.lng();
  } else {
    frame.lat = -6.2088;
    frame.lon = 106.8456;
  }
  frame.alt = gps.altitude.isValid() ? gps.altitude.meters() : 60.0;
  frame.battery = 88.0f;
  frame.rssi = lastRssi;
  frame.snr = lastSnr;
  return frame;
}

static String buildJsonPayload(const TelemetryFrame& frame) {
  JsonDocument doc;
  doc["node_id"] = NODE_ID;
  doc["lat"] = frame.lat;
  doc["lon"] = frame.lon;
  doc["alt"] = frame.alt;
  doc["battery"] = frame.battery;
  doc["rssi"] = frame.rssi;
  doc["snr"] = frame.snr;

  String out;
  serializeJson(doc, out);
  return out;
}

static void transmitLoRa(const String& payload) {
  // TODO: integrate RadioLib / Heltec LoRaWan for SX1262/SX1276 on your board.
  // Example: radio.transmit((uint8_t*)payload.c_str(), payload.length());
  lastRssi += 0.1f;
  if (lastRssi > -60.0f) lastRssi = -90.0f;
}

static void pumpGps() {
  while (GPSSerial.available() > 0) {
    gps.encode(GPSSerial.read());
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);
  GPSSerial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  Serial.println("# ESP32 LoRa Gateway starting");
  Serial.print("# node_id=");
  Serial.println(NODE_ID);
  Serial.print("# lora_freq_mhz=");
  Serial.println(LORA_FREQ_MHZ);
}

void loop() {
  pumpGps();

  static unsigned long lastTx = 0;
  const unsigned long now = millis();
  if (now - lastTx < LORA_TX_INTERVAL_MS) {
    return;
  }
  lastTx = now;

  const TelemetryFrame frame = readTelemetry();
  const String payload = buildJsonPayload(frame);

  transmitLoRa(payload);
  Serial.println(payload);
}
