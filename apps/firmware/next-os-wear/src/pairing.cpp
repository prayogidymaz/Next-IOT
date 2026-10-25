#include "pairing.h"

#include "wifi.h"

/**
 * QR/BLE claim penuh — Week 11-12. Saat ini credential dari config.h / NVS WiFi.
 */
bool next_os_pairing_needs_setup(void) {
#if defined(NEXT_OS_HARDWARE)
    return !next_os_wifi_has_stored_credentials();
#else
    return false;
#endif
}

void next_os_pairing_show_waiting_screen(void) {
    /* Placeholder: layar "WAITING FOR SETUP" + animasi dots */
}
