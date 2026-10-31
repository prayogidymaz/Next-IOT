#include "features/watch_face/watch_face_renderer.h"

#include "theme.h"

#include <ArduinoJson.h>

#include <cstddef>
#include <cstdio>

namespace {

bool read_file_to_string(const char *path, char *buf, std::size_t buf_len) {
    FILE *f = std::fopen(path, "rb");
    if (f == nullptr) {
        return false;
    }
    const std::size_t n = std::fread(buf, 1, buf_len - 1, f);
    std::fclose(f);
    buf[n] = '\0';
    return n > 0;
}

}  // namespace

bool WatchFaceRenderer::load_from_file(const char *path) {
    char json_buf[4096];
    if (!read_file_to_string(path, json_buf, sizeof(json_buf))) {
        (void)std::printf("[FACE] Failed to load %s\n", path);
        return false;
    }
    JsonDocument doc;
    if (deserializeJson(doc, json_buf)) {
        return false;
    }
    const char *name = doc["name"] | "face";
    (void)std::snprintf(m_name, sizeof(m_name), "%s", name);
    (void)std::printf("[FACE] Loaded %s from %s\n", m_name, path);
    return true;
}

void WatchFaceRenderer::render_to(lv_obj_t *parent) {
    if (parent == nullptr) {
        return;
    }
    if (m_root != nullptr) {
        lv_obj_delete(m_root);
    }
    m_root = lv_obj_create(parent);
    lv_obj_set_size(m_root, lv_pct(100), lv_pct(100));
    lv_obj_set_style_bg_opa(m_root, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(m_root, 0, 0);
    lv_obj_set_flex_flow(m_root, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(m_root, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    m_clock_label = lv_label_create(m_root);
    lv_label_set_text(m_clock_label, "12:00");
    lv_obj_set_style_text_color(m_clock_label, NEXTOS_TEXT_PRIMARY, 0);

    lv_obj_t *subtitle = lv_label_create(m_root);
    lv_label_set_text_fmt(subtitle, "%s face", m_name);
    lv_obj_set_style_text_color(subtitle, NEXTOS_TEXT_SECONDARY, 0);
}

void WatchFaceRenderer::tick() {
    if (m_clock_label == nullptr) {
        return;
    }
#if defined(NEXT_OS_SIMULATOR)
    const uint32_t sec = lv_tick_get() / 1000U;
    const uint32_t mm = (sec / 60U) % 60U;
    const uint32_t hh = (sec / 3600U) % 24U;
    lv_label_set_text_fmt(m_clock_label, "%02u:%02u", static_cast<unsigned>(hh), static_cast<unsigned>(mm));
#endif
}
