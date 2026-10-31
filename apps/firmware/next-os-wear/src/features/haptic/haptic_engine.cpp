#include "features/haptic/haptic_engine.h"

#include "haptic.h"

#include <Arduino.h>
#include <cstdio>

#if defined(NEXT_OS_HARDWARE)
#include <driver/ledc.h>
#endif

namespace {

constexpr int kHapticPwmPin = 2;
HapticEngine g_engine;

}  // namespace

void HapticEngine::init() {
#if defined(NEXT_OS_HARDWARE)
    ledcSetup(0, 2000, 8);
    ledcAttachPin(kHapticPwmPin, 0);
#endif
    (void)std::printf("[HAPTIC] Engine init\n");
}

void HapticEngine::set_battery_percent(int percent) {
    m_battery_percent = percent;
}

void HapticEngine::drive_motor_ms(unsigned int ms, bool strong) {
#if defined(NEXT_OS_HARDWARE)
    const int duty = strong ? 200 : 128;
    ledcWrite(0, duty);
    delay(ms);
    ledcWrite(0, 0);
#else
    nextos_haptic_intensity_t intensity = NEXTOS_HAPTIC_LIGHT;
    if (strong) {
        intensity = NEXTOS_HAPTIC_STRONG;
    }
    nextos_haptic_pulse(intensity);
    (void)ms;
    (void)std::printf("[HAPTIC] Pattern buzz %ums strong=%d\n", ms, strong ? 1 : 0);
#endif
}

void HapticEngine::play_pattern(HapticPattern pattern) {
    if (m_battery_percent < 20 && pattern == HapticPattern::ALERT_HIGH) {
        (void)std::printf("[HAPTIC] Skipping ALERT_HIGH (battery %d%%)\n", m_battery_percent);
        pattern = HapticPattern::ALERT_MEDIUM;
    }

    switch (pattern) {
    case HapticPattern::ALERT_LOW:
        drive_motor_ms(50, false);
        break;
    case HapticPattern::NOTIFICATION:
        drive_motor_ms(30, false);
        break;
    case HapticPattern::SUCCESS:
        drive_motor_ms(50, false);
        drive_motor_ms(50, false);
        break;
    case HapticPattern::ERROR:
        drive_motor_ms(300, true);
        break;
    case HapticPattern::ALERT_MEDIUM:
        drive_motor_ms(100, true);
        drive_motor_ms(100, true);
        break;
    case HapticPattern::ALERT_HIGH:
        drive_motor_ms(200, true);
        drive_motor_ms(200, true);
        drive_motor_ms(200, true);
        break;
    }
}

HapticEngine &next_os_haptic_engine(void) {
    return g_engine;
}
