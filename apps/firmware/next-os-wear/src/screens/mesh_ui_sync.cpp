#include "screens/mesh_ui_sync.h"

#include "screens/alert_center.h"
#include "screens/cctv_alert.h"
#include "screens/irrigation_control.h"
#include "screens/mesh_graph.h"
#include "screens/ndvi_heatmap.h"
#include "screens/screen_manager.h"
#include "screens/sensor_monitor.h"
#include "screens/terminal_feed.h"
#include "screens/watch_face.h"

void next_os_mesh_ui_sync_refresh(void) {
    const next_os_screen_id_t active = next_os_screen_manager_get_current();
    switch (active) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_os_watch_face_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_FARMING_SENSOR:
        next_os_sensor_monitor_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_FARMING_IRRIGATION:
        next_os_irrigation_control_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        next_os_alert_center_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_FARMING_CCTV:
        next_os_cctv_alert_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_MESH_GRAPH:
        next_os_mesh_graph_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_FARMING_NDVI:
        next_os_ndvi_heatmap_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_MESH_TERMINAL:
        next_os_terminal_feed_refresh_from_mesh();
        break;
    default:
        break;
    }
}
