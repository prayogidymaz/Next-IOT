#include "ota.h"

/**
 * Stub OTA — HTTPUpdate + verifikasi SHA256 dari Firmware Studio (Week 7-10).
 */
#if defined(NEXT_OS_HARDWARE)
#include <HTTPUpdate.h>
#include <WiFi.h>

bool next_os_ota_check_and_apply(const char *url) {
    if (url == nullptr || url[0] == '\0') {
        return false;
    }
    WiFiClient client;
    const t_httpUpdate_return ret = httpUpdate.update(client, url);
    return ret == HTTP_UPDATE_OK;
}

#else

bool next_os_ota_check_and_apply(const char *url) {
    (void)url;
    return false;
}

#endif
