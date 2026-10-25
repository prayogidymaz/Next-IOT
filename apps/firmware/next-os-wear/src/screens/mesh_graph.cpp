#include "screens/mesh_graph.h"

#include "mesh_state.h"
#include "screens/common.h"
#include "theme.h"

#include <cstdio>

static lv_obj_t *s_nodes[NEXT_OS_MESH_NODE_COUNT] = {nullptr};
static lv_obj_t *s_drn_ring = nullptr;
static lv_timer_t *s_poll_timer = nullptr;

static bool graph_node_recent(next_os_mesh_node_id_t id) {
    const uint32_t last = next_os_mesh_state_node_last_ms(id);
    if (last == 0) {
        return false;
    }
    return lv_tick_elaps(last) < 30000U;
}

void next_os_mesh_graph_dispose(void) {
    if (s_poll_timer != nullptr) {
        lv_timer_delete(s_poll_timer);
        s_poll_timer = nullptr;
    }
    for (uint8_t i = 0; i < NEXT_OS_MESH_NODE_COUNT; i++) {
        s_nodes[i] = nullptr;
    }
    s_drn_ring = nullptr;
}

static void graph_on_delete(lv_event_t *event) {
    if (lv_event_get_code(event) != LV_EVENT_DELETE) {
        return;
    }
    next_os_mesh_graph_dispose();
}

static void graph_poll_cb(lv_timer_t *timer) {
    (void)timer;
    next_os_mesh_graph_refresh_from_mesh();
}

static lv_obj_t *graph_create_node(lv_obj_t *parent, int32_t x, int32_t y, int32_t r,
                                   lv_color_t border, const char *label) {
    lv_obj_t *n = lv_obj_create(parent);
    lv_obj_set_size(n, static_cast<int32_t>(r * 2), static_cast<int32_t>(r * 2));
    lv_obj_set_pos(n, x - r, y - r);
    lv_obj_set_style_radius(n, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(n, next_os_color_dark(), 0);
    lv_obj_set_style_border_color(n, border, 0);
    lv_obj_set_style_border_width(n, 2, 0);
    lv_obj_t *l = lv_label_create(n);
    lv_label_set_text(l, label);
    lv_obj_set_style_text_font(l, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(l, next_os_color_cream(), 0);
    lv_obj_center(l);
    return n;
}

static void graph_line(lv_obj_t *parent, int32_t x1, int32_t y1, int32_t x2, int32_t y2,
                       lv_color_t color) {
    static lv_point_precise_t pts[2];
    pts[0].x = static_cast<lv_value_precise_t>(x1);
    pts[0].y = static_cast<lv_value_precise_t>(y1);
    pts[1].x = static_cast<lv_value_precise_t>(x2);
    pts[1].y = static_cast<lv_value_precise_t>(y2);
    lv_obj_t *line = lv_line_create(parent);
    lv_line_set_points(line, pts, 2);
    lv_obj_set_style_line_color(line, color, 0);
    lv_obj_set_style_line_width(line, 2, 0);
}

void next_os_mesh_graph_refresh_from_mesh(void) {
    const next_os_mesh_topology_t topo = next_os_mesh_state_topology();
    const uint8_t load = next_os_mesh_state_recent_event_count();
    const int32_t edge_w = load > 4 ? 3 : 2;

    for (uint8_t i = 0; i < NEXT_OS_MESH_NODE_COUNT; i++) {
        if (!nextos_ui_obj_alive(s_nodes[i])) {
            continue;
        }
        const bool recent = graph_node_recent(static_cast<next_os_mesh_node_id_t>(i));
        lv_obj_set_style_border_color(s_nodes[i], recent ? next_os_color_olive() : next_os_color_light_grey(), 0);
        lv_obj_set_style_border_width(s_nodes[i], edge_w, 0);
    }

    if (nextos_ui_obj_alive(s_nodes[NEXT_OS_MESH_NODE_DRN])) {
        lv_obj_set_style_border_color(
            s_nodes[NEXT_OS_MESH_NODE_DRN],
            topo.drn_dispatch_pulse ? next_os_color_clay() : next_os_color_olive(), 0);
    }
    if (nextos_ui_obj_alive(s_drn_ring)) {
        lv_obj_set_style_border_opa(s_drn_ring, topo.drn_dispatch_pulse ? LV_OPA_60 : LV_OPA_TRANSP, 0);
    }
}

void next_os_mesh_graph_create(lv_obj_t *root) {
    next_os_mesh_graph_dispose();
    next_os_apply_black_screen_style(root);
    lv_obj_add_event_cb(root, graph_on_delete, LV_EVENT_DELETE, nullptr);

    lv_obj_t *header = next_os_common_create_inset_header_row(root, 22);
    lv_obj_t *icon = lv_label_create(header);
    lv_label_set_text(icon, LV_SYMBOL_WIFI);
    lv_obj_set_style_text_color(icon, next_os_color_olive(), 0);
    lv_obj_align(icon, LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_t *ht = lv_label_create(header);
    lv_label_set_text(ht, "MESH • 7 NODES");
    lv_obj_set_style_text_color(ht, next_os_color_olive(), 0);
    lv_obj_align(ht, LV_ALIGN_CENTER, 0, 0);
    lv_obj_t *tm = lv_label_create(header);
    lv_label_set_text(tm, "07:42");
    lv_obj_set_style_text_color(tm, next_os_color_muted(), 0);
    lv_obj_align(tm, LV_ALIGN_RIGHT_MID, 0, 0);

    lv_obj_t *canvas_box = lv_obj_create(root);
    lv_obj_set_size(canvas_box, 200, 140);
    lv_obj_align(canvas_box, LV_ALIGN_CENTER, 0, -6);
    lv_obj_set_style_bg_color(canvas_box, next_os_color_dark(), 0);
    lv_obj_set_style_border_color(canvas_box, next_os_color_olive(), 0);
    lv_obj_set_style_border_width(canvas_box, 1, 0);
    lv_obj_set_style_radius(canvas_box, 8, 0);
    next_os_common_disable_scroll(canvas_box);

    const int32_t cx = 100;
    const int32_t cy = 70;
    const int32_t radius = 52;

    graph_line(canvas_box, cx, cy, cx, cy - radius, next_os_color_olive());
    graph_line(canvas_box, cx, cy, cx - radius, cy - 20, next_os_color_olive());
    graph_line(canvas_box, cx, cy, cx + radius, cy - 10, next_os_color_clay());
    graph_line(canvas_box, cx, cy, cx - 40, cy + 40, next_os_color_light_grey());
    graph_line(canvas_box, cx, cy, cx + 36, cy + 44, next_os_color_olive());

    s_nodes[NEXT_OS_MESH_NODE_HUB] = graph_create_node(canvas_box, cx, cy, 18, next_os_color_olive(), "HUB");
    s_nodes[NEXT_OS_MESH_NODE_S2] =
        graph_create_node(canvas_box, cx, cy - radius, 12, next_os_color_light_grey(), "S2");
    s_nodes[NEXT_OS_MESH_NODE_S3] =
        graph_create_node(canvas_box, cx - 20, cy - radius + 8, 12, next_os_color_light_grey(), "S3");
    s_nodes[NEXT_OS_MESH_NODE_CAM] =
        graph_create_node(canvas_box, cx - radius, cy - 20, 12, next_os_color_olive(), "CAM");
    s_nodes[NEXT_OS_MESH_NODE_DRN] =
        graph_create_node(canvas_box, cx + radius, cy - 10, 12, next_os_color_clay(), "DRN");
    s_nodes[NEXT_OS_MESH_NODE_SPR] =
        graph_create_node(canvas_box, cx - 40, cy + 40, 12, next_os_color_olive(), "SPR");
    s_nodes[NEXT_OS_MESH_NODE_GT] =
        graph_create_node(canvas_box, cx + 36, cy + 44, 12, next_os_color_olive(), "GT");

    s_drn_ring = lv_obj_create(canvas_box);
    lv_obj_set_size(s_drn_ring, 36, 36);
    lv_obj_set_pos(s_drn_ring, cx + radius - 18, cy - 10 - 18);
    lv_obj_set_style_radius(s_drn_ring, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_opa(s_drn_ring, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_color(s_drn_ring, next_os_color_clay(), 0);
    lv_obj_set_style_border_width(s_drn_ring, 2, 0);

    for (uint8_t i = 0; i < 4; i++) {
        lv_obj_t *pt = lv_obj_create(canvas_box);
        lv_obj_set_size(pt, 3, 3);
        lv_obj_set_style_radius(pt, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_color(pt, next_os_color_cream(), 0);
        lv_obj_set_pos(pt, static_cast<int32_t>(40 + i * 30), static_cast<int32_t>(20 + (i % 2) * 80));
    }

    const next_os_mesh_topology_t topo = next_os_mesh_state_topology();
    char footer[48];
    (void)std::snprintf(footer, sizeof(footer), "%u LIVE | %u DISPATCH | %u IDLE",
                        static_cast<unsigned>(topo.live_nodes), static_cast<unsigned>(topo.dispatch_nodes),
                        static_cast<unsigned>(topo.idle_nodes));
    lv_obj_t *foot = lv_label_create(root);
    lv_label_set_text(foot, footer);
    lv_obj_set_style_text_font(foot, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(foot, next_os_color_cream(), 0);
    lv_obj_align(foot, LV_ALIGN_BOTTOM_MID, 0, -12);

    next_os_mesh_graph_refresh_from_mesh();
    s_poll_timer = lv_timer_create(graph_poll_cb, 1000, nullptr);
}
