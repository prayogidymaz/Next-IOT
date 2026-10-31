#include "features/watch_face/watch_face_renderer.h"

#include <cstddef>
#include <cstdio>

namespace {

constexpr const char *kFacePaths[] = {
#if defined(NEXT_OS_SIMULATOR)
    "data/faces/classic.json",
    "data/faces/minimal.json",
    "data/faces/farmer.json",
#else
    "/faces/classic.json",
    "/faces/minimal.json",
    "/faces/farmer.json",
#endif
};

constexpr std::size_t kFaceCount = sizeof(kFacePaths) / sizeof(kFacePaths[0]);
std::size_t s_index = 0;
WatchFaceRenderer s_renderer;

}  // namespace

void next_os_face_switcher_init(void) {
    s_index = 0;
    (void)s_renderer.load_from_file(kFacePaths[s_index]);
}

void next_os_face_switcher_mount(lv_obj_t *parent) {
    s_renderer.render_to(parent);
}

void next_os_face_switcher_tick(void) {
    s_renderer.tick();
}

void next_os_face_switcher_next(void) {
    s_index = (s_index + 1) % kFaceCount;
    (void)s_renderer.load_from_file(kFacePaths[s_index]);
}

void next_os_face_switcher_prev(void) {
    s_index = (s_index + kFaceCount - 1) % kFaceCount;
    (void)s_renderer.load_from_file(kFacePaths[s_index]);
    (void)std::printf("[FACE] Switched to index %zu\n", s_index);
}
