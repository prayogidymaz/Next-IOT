#include "screens/hubs/farming_hub.h"

#include "layout.h"
#include "mesh_state.h"
#include "screens/common.h"
#include "screens/screen_manager.h"
#include "theme.h"

#include <cstdio>

void next_os_farming_hub_create(lv_obj_t *root) {
    next_os_apply_screen_style(root);
    next_os_common_create_header_label(root, "Smart Farming");

    const next_os_mesh_sensor_t sensor = next_os_mesh_state_sensor();
    const next_os_mesh_irrig_t ir = next_os_mesh_state_irrig();
    const next_os_mesh_cctv_t cctv = next_os_mesh_state_cctv();
    const next_os_mesh_ndvi_t ndvi = next_os_mesh_state_ndvi();

    char line_sensor[32];
    char line_irrig[40];
    char line_cctv[32];
    char line_ndvi[40];
    (void)std::snprintf(line_sensor, sizeof(line_sensor), "%ld%% moisture", static_cast<long>(sensor.moisture));
    (void)std::snprintf(line_irrig, sizeof(line_irrig), "%s %s", ir.valve_name, ir.countdown);
    (void)std::snprintf(line_cctv, sizeof(line_cctv), "Last motion %s", cctv.timestamp);
    (void)std::snprintf(line_ndvi, sizeof(line_ndvi), "%.2f avg • %u stress",
                        static_cast<double>(ndvi.avg_ndvi), static_cast<unsigned>(ndvi.stress_zones));

    lv_obj_t *list = lv_obj_create(root);
    lv_obj_set_size(list, nextos_content_width(), NEXTOS_IS_ROUND ? 170 : 240);
    lv_obj_align(list, LV_ALIGN_CENTER, 0, 16);
    lv_obj_set_style_bg_opa(list, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(list, 0, 0);
    lv_obj_set_flex_flow(list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(list, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_row(list, 8, 0);
    next_os_common_disable_scroll(list);

    next_os_common_create_hub_row(list, "Sensor Monitor", line_sensor, NEXT_OS_SCREEN_FARMING_SENSOR);
    next_os_common_create_hub_row(list, "Irrigation", line_irrig, NEXT_OS_SCREEN_FARMING_IRRIGATION);
    next_os_common_create_hub_row(list, "CCTV Alert", line_cctv, NEXT_OS_SCREEN_FARMING_CCTV);
    next_os_common_create_hub_row(list, "NDVI Heatmap", line_ndvi, NEXT_OS_SCREEN_FARMING_NDVI);
    next_os_common_create_hub_row(list, "Harvest Calendar", "Fruiting day 42", NEXT_OS_SCREEN_FARMING_HARVEST);
}
