#include "NextIotOta.h"

#include <HTTPClient.h>
#include <Update.h>
#include <WiFi.h>

void nextiotOtaHandleMessage(const NextIotConfig& config, JsonObject payload) {
  const char* url = payload["file_url"] | "";
  const char* checksum = payload["checksum_sha256"] | "";
  if (url[0] == '\0') {
    return;
  }
  HTTPClient http;
  http.begin(url);
  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    http.end();
    return;
  }
  int len = http.getSize();
  WiFiClient* stream = http.getStreamPtr();
  if (!Update.begin(len > 0 ? len : UPDATE_SIZE_UNKNOWN)) {
    http.end();
    return;
  }
  size_t written = Update.writeStream(*stream);
  if (written == 0 || !Update.end(true)) {
    http.end();
    return;
  }
  http.end();
  (void)checksum;
  delay(500);
  ESP.restart();
}
