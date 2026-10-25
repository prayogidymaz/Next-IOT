#include "screens/hubs/mesh_ops_hub.h"

#include "layout.h"
#include "mesh_state.h"
#include "screens/common.h"
#include "screens/screen_manager.h"
#include "theme.h"

#include <cstdio>

void next_os_mesh_ops_hub_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Mesh Ops");

    const next_os_mesh_topology_t topo = next_os_mesh_state_topology();
    const uint8_t logs = next_os_mesh_state_log_count();
    const next_os_mesh_workflow_t wf = next_os_mesh_state_workflow();

    char line_graph[32];
    char line_term[32];
    char line_wf[40];
    (void)std::snprintf(line_graph, sizeof(line_graph), "%u nodes • %u live",
                        static_cast<unsigned>(topo.live_nodes + topo.idle_nodes + topo.dispatch_nodes),
                        static_cast<unsigned>(topo.live_nodes));
    (void)std::snprintf(line_term, sizeof(line_term), "%u events recent", static_cast<unsigned>(logs));
    (void)std::snprintf(line_wf, sizeof(line_wf), "%s %s", wf.workflow_name, wf.active ? "ACTIVE" : "IDLE");

    lv_obj_t *list = lv_obj_create(root);
    lv_obj_set_size(list, nextos_content_width(), NEXTOS_IS_ROUND ? 170 : 240);
    lv_obj_align(list, LV_ALIGN_CENTER, 0, 16);
    lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(list, 0, 0);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_row(list, 8, 0);
    next_os_common_disable_scroll(list);

    next_os_common_create_hub_row(list, "Mesh Graph", line_graph, NEXT_OS_SCREEN_MESH_GRAPH);
    next_os_common_create_hub_row(list, "Terminal Feed", line_term, NEXT_OS_SCREEN_MESH_TERMINAL);
    next_os_common_create_hub_row(list, "Workflow Status", line_wf, NEXT_OS_SCREEN_MESH_WORKFLOW);
    next_os_common_create_hub_row(list, "Device Dispatch", "Manual trigger", NEXT_OS_SCREEN_MESH_DISPATCH);
}
