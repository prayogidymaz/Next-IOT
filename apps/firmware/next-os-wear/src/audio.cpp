#include "audio.h"

#include "user_prefs.h"

#include <cstdio>
#include <cmath>
#include <cstring>
#include <vector>

#ifndef NEXTOS_HAS_SDL_MIXER
#define NEXTOS_HAS_SDL_MIXER 0
#endif

#if NEXTOS_HAS_SDL_MIXER
#include <SDL2/SDL.h>
#include <SDL2/SDL_mixer.h>
#endif

static bool s_audio_ready = false;

#if NEXTOS_HAS_SDL_MIXER

static Mix_Chunk *make_tone_chunk(int hz, int duration_ms) {
    const int sample_rate = 44100;
    const int samples = (sample_rate * duration_ms) / 1000;
    std::vector<int16_t> pcm(static_cast<size_t>(samples));
    for (int i = 0; i < samples; i++) {
        const double t = static_cast<double>(i) / static_cast<double>(sample_rate);
        const double amp = 0.25 * std::sin(2.0 * 3.141592653589793 * static_cast<double>(hz) * t);
        pcm[static_cast<size_t>(i)] = static_cast<int16_t>(amp * 32767.0);
    }
    const Uint32 byte_len = static_cast<Uint32>(pcm.size() * sizeof(int16_t));
    Uint8 *mem = static_cast<Uint8 *>(SDL_malloc(byte_len));
    if (mem == nullptr) {
        return nullptr;
    }
    (void)std::memcpy(mem, pcm.data(), byte_len);
    return Mix_QuickLoad_RAW(mem, byte_len);
}

static void play_tone(int hz, int duration_ms) {
    if (!s_audio_ready) {
        return;
    }
    Mix_Chunk *chunk = make_tone_chunk(hz, duration_ms);
    if (chunk == nullptr) {
        return;
    }
    (void)Mix_PlayChannel(-1, chunk, 0);
    Mix_FreeChunk(chunk);
}

#endif

void nextos_audio_init(void) {
#if NEXTOS_HAS_SDL_MIXER
    if (Mix_OpenAudio(44100, AUDIO_S16SYS, 1, 512) == 0) {
        s_audio_ready = true;
        return;
    }
    (void)std::printf("[AUDIO] SDL_mixer init failed: %s\n", Mix_GetError());
#else
    s_audio_ready = false;
#endif
}

void nextos_audio_beep(nextos_beep_pattern_t pattern) {
    if (!next_os_user_prefs_audio_enabled() || next_os_user_prefs_dnd_enabled()) {
        return;
    }
#if NEXTOS_HAS_SDL_MIXER
    if (!s_audio_ready) {
        return;
    }
    switch (pattern) {
    case NEXTOS_BEEP_ALERT:
        play_tone(440, 100);
        play_tone(440, 100);
        break;
    case NEXTOS_BEEP_SUCCESS:
        play_tone(880, 120);
        break;
    case NEXTOS_BEEP_ERROR:
        play_tone(220, 80);
        play_tone(220, 80);
        play_tone(220, 80);
        break;
    }
#else
    (void)pattern;
#endif
}
