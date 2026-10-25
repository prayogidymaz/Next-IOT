#ifndef NEXT_OS_WIFI_H
#define NEXT_OS_WIFI_H

#include <stdint.h>

bool next_os_wifi_begin(void);
bool next_os_wifi_is_connected(void);
void next_os_wifi_loop(void);
void next_os_wifi_disconnect(void);

int32_t next_os_wifi_rssi(void);
bool next_os_wifi_has_stored_credentials(void);
bool next_os_wifi_load_and_connect(uint32_t timeout_ms);

#endif /* NEXT_OS_WIFI_H */
