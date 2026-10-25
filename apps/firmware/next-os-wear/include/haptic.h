#ifndef NEXT_OS_HAPTIC_H
#define NEXT_OS_HAPTIC_H

typedef enum {
    NEXTOS_HAPTIC_LIGHT = 0,
    NEXTOS_HAPTIC_MEDIUM = 1,
    NEXTOS_HAPTIC_STRONG = 2,
} nextos_haptic_intensity_t;

void nextos_haptic_init(void);
void nextos_haptic_pulse(nextos_haptic_intensity_t intensity);

#endif /* NEXT_OS_HAPTIC_H */
