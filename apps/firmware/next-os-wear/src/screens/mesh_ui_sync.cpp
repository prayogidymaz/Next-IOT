#include "screens/mesh_ui_sync.h"

#include "screens/alert_center.h"
#include "screens/irrigation_control.h"
#include "screens/screen_manager.h"
#include "screens/sensor_monitor.h"
#include "screens/watch_face.h"

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
    default:
        break;
    }
}
