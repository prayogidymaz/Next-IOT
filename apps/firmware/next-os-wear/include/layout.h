/**
 * Responsive layout — round vs square smartwatch form factors.
 */
#ifndef NEXT_OS_LAYOUT_H
#define NEXT_OS_LAYOUT_H

#ifndef NEXTOS_FORM_FACTOR_ROUND
#define NEXTOS_FORM_FACTOR_ROUND 1
#endif

#ifndef NEXTOS_SCREEN_WIDTH
#define NEXTOS_SCREEN_WIDTH 240
#endif

#ifndef NEXTOS_SCREEN_HEIGHT
#define NEXTOS_SCREEN_HEIGHT 240
#endif

#define NEXTOS_IS_ROUND (NEXTOS_FORM_FACTOR_ROUND == 1)
#define NEXTOS_W NEXTOS_SCREEN_WIDTH
#define NEXTOS_H NEXTOS_SCREEN_HEIGHT

constexpr int nextos_safe_padding_top(void) {
    return NEXTOS_IS_ROUND ? 24 : 12;
}

constexpr int nextos_safe_padding_side(void) {
    return NEXTOS_IS_ROUND ? 20 : 10;
}

constexpr int nextos_safe_padding_bottom(void) {
    return NEXTOS_IS_ROUND ? 24 : 12;
}

constexpr int nextos_content_width(void) {
    return NEXTOS_W - 2 * nextos_safe_padding_side();
}

constexpr int nextos_content_height(void) {
    return NEXTOS_H - nextos_safe_padding_top() - nextos_safe_padding_bottom();
}

constexpr float nextos_font_scale(void) {
    return static_cast<float>(NEXTOS_H) / 240.0F;
}

constexpr int nextos_font_scaled(int base_px) {
    return static_cast<int>(static_cast<float>(base_px) * nextos_font_scale());
}

/** Header row below nav buttons (clear 36px corners). */
constexpr int nextos_inset_header_y(void) {
    return NEXTOS_IS_ROUND ? 38 : 28;
}

/** Status row below nav button zone (~32px tall). */
constexpr int nextos_status_header_y(void) {
    return 36;
}

constexpr int nextos_settings_title_y(void) {
    return 42;
}

constexpr int nextos_inset_header_width(void) {
    const int clear = 36;
    return nextos_content_width() - clear;
}

constexpr int nextos_nav_button_size(void) {
    return 28;
}

#endif /* NEXT_OS_LAYOUT_H */
