#pragma once

#include <stdint.h>

struct NextIotConfig {
  const char* wifi_ssid;
  const char* wifi_password;
  const char* broker_host;
  uint16_t broker_port;
  bool use_tls;
  const char* ca_cert_pem;
  const char* tenant_id;
  const char* device_id;
  const char* access_token;
  uint16_t keepalive_seconds;
  uint16_t reconnect_delay_ms;
  bool enable_ota;
  const char* device_profile_json;
};
