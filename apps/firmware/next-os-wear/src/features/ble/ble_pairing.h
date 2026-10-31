#pragma once

#include <cstdint>

/** Next-IoT companion BLE GATT server (phone app pairs as central). */
void next_os_ble_init(void);
void next_os_ble_loop(void);
bool next_os_ble_is_paired(void);

#if defined(NEXT_OS_SIMULATOR)
void next_os_ble_simulate_pair_toggle(void);
#endif
