#include "ota.h"

#if defined(NEXT_OS_HARDWARE)

#include <HTTPUpdate.h>
#include <WiFi.h>

#include <cstring>

bool next_os_ota_trigger_update(const char *url, const char *expected_sha256_hex) {
    if (url == nullptr || url[0] == '\0') {
        return false;
    }
    (void)expected_sha256_hex;
    /* TODO Week 11: verifikasi SHA256 sebelum apply */
    WiFiClient client;
    const t_httpUpdate_return ret = httpUpdate.update(client, url);
    return ret == HTTP_UPDATE_OK;
}

void next_os_ota_loop(void) {}

#else

bool next_os_ota_trigger_update(const char *url, const char *expected_sha256_hex) {
    (void)url;
    (void)expected_sha256_hex;
    return false;
}

void next_os_ota_loop(void) {}

#endif
