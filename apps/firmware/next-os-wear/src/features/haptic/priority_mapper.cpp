#include "features/haptic/haptic_engine.h"

#include <cstring>

HapticPattern next_os_map_alert_to_haptic(const char *alert_type, int priority) {
    if (alert_type == nullptr) {
        return HapticPattern::NOTIFICATION;
    }
    if (std::strcmp(alert_type, "pest_detected") == 0) {
        return HapticPattern::ALERT_HIGH;
    }
    if (std::strcmp(alert_type, "irrigation_started") == 0) {
        return HapticPattern::NOTIFICATION;
    }
    if (std::strcmp(alert_type, "sensor_offline") == 0) {
        return HapticPattern::ALERT_MEDIUM;
    }
    if (std::strcmp(alert_type, "yield_milestone") == 0) {
        return HapticPattern::SUCCESS;
    }
    if (priority >= 3) {
        return HapticPattern::ALERT_HIGH;
    }
    if (priority == 2) {
        return HapticPattern::ALERT_MEDIUM;
    }
    return HapticPattern::NOTIFICATION;
}

void next_os_notification_apply_haptic(const char *alert_type, int priority) {
    const HapticPattern pattern = next_os_map_alert_to_haptic(alert_type, priority);
    next_os_haptic_engine().play_pattern(pattern);
}
