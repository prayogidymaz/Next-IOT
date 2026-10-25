#ifndef NEXT_OS_AUDIO_H
#define NEXT_OS_AUDIO_H

typedef enum {
    NEXTOS_BEEP_ALERT = 0,
    NEXTOS_BEEP_SUCCESS = 1,
    NEXTOS_BEEP_ERROR = 2,
} nextos_beep_pattern_t;

void nextos_audio_init(void);
void nextos_audio_beep(nextos_beep_pattern_t pattern);

#endif /* NEXT_OS_AUDIO_H */
