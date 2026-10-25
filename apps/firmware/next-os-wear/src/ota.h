#ifndef NEXT_OS_OTA_H
#define NEXT_OS_OTA_H

#include <stddef.h>

bool next_os_ota_trigger_update(const char *url, const char *expected_sha256_hex);
void next_os_ota_loop(void);

#endif /* NEXT_OS_OTA_H */
