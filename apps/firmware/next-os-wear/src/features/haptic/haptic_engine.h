#pragma once

enum class HapticPattern {
    ALERT_LOW,
    ALERT_MEDIUM,
    ALERT_HIGH,
    NOTIFICATION,
    SUCCESS,
    ERROR,
};

class HapticEngine {
public:
    void init();
    void play_pattern(HapticPattern pattern);
    void set_battery_percent(int percent);

private:
    int m_battery_percent = 100;
    void drive_motor_ms(unsigned int ms, bool strong);
};

HapticEngine &next_os_haptic_engine(void);

void next_os_notification_apply_haptic(const char *alert_type, int priority);
