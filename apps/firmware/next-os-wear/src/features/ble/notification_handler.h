#pragma once

#include <cstddef>

/** Parse phone relay JSON and surface on watch (haptic wired in features/haptic). */
void next_os_notification_handler_init(void);
void next_os_notification_handler_on_ble_payload(const char *json, std::size_t len);
