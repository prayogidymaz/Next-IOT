#include <NextIotClient.h>
#include <NextIotConfig.h>

NextIotConfig config = {
    .wifi_ssid = "MyWifi",
    .wifi_password = "mypassword",
    .broker_host = "192.168.1.100",
    .broker_port = 1883,
    .use_tls = false,
    .ca_cert_pem = nullptr,
    .tenant_id = "YOUR_TENANT_ID",
    .device_id = "YOUR_DEVICE_ID",
    .access_token = "YOUR_ACCESS_TOKEN",
    .keepalive_seconds = 30,
    .reconnect_delay_ms = 5000,
    .enable_ota = false,
    .device_profile_json = nullptr,
};

NextIotClient client(config);

void setup() {
  Serial.begin(115200);
  client.begin();
}

void loop() {
  client.loop();
  static unsigned long last = 0;
  if (millis() - last > 10000) {
    last = millis();
    client.publishTelemetry("temperature", 25.5f);
  }
}
