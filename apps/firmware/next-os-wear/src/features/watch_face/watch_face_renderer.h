#pragma once

#include <lvgl.h>

class WatchFaceRenderer {
public:
    bool load_from_file(const char *path);
    void render_to(lv_obj_t *parent);
    void tick();

private:
    char m_name[32] = {};
    lv_obj_t *m_root = nullptr;
    lv_obj_t *m_clock_label = nullptr;
};
