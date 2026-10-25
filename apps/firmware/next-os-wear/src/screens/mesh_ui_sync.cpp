#include "screens/mesh_ui_sync.h"

#include "screens/alert_center.h"
#include "screens/cctv_alert.h"
#include "screens/irrigation_control.h"
#include "screens/irrigation_wave.h"
#include "screens/mesh_graph.h"
#include "screens/ndvi_heatmap.h"
#include "screens/screen_manager.h"
#include "screens/sensor_monitor.h"
#include "screens/sensor_radial.h"
#include "screens/terminal_feed.h"
#include "screens/watch_face.h"
#include "screens/watch_face_square.h"

void next_os_mesh_ui_sync_refresh(void) {
    const next_os_screen_id_t active = next_os_screen_manager_get_current();
    switch (active) {
    case NEXT_OS_SCREEN_WATCH_FACE:
        next_os_watch_face_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_SENSOR_MONITOR:
        next_os_sensor_monitor_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_IRRIGATION:
        next_os_irrigation_control_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_ALERT_CENTER:
        next_os_alert_center_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_CCTV_ALERT:
        next_os_cctv_alert_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_WATCH_FACE_SQUARE:
        next_os_watch_face_square_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_SENSOR_RADIAL:
        next_os_sensor_radial_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_IRRIGATION_WAVE:
        next_os_irrigation_wave_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_MESH_GRAPH:
        next_os_mesh_graph_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_NDVI_HEATMAP:
        next_os_ndvi_heatmap_refresh_from_mesh();
        break;
    case NEXT_OS_SCREEN_TERMINAL_FEED:
        next_os_terminal_feed_refresh_from_mesh();
        break;
    default:
        break;
    }
}
