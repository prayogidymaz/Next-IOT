#include "screens/mesh_ui_sync.h"

#include "screens/alert_center.h"
#include "screens/irrigation_control.h"
#include "screens/sensor_monitor.h"
#include "screens/watch_face.h"

void next_os_mesh_ui_sync_refresh(void) {
    next_os_watch_face_refresh_from_mesh();
    next_os_sensor_monitor_refresh_from_mesh();
    next_os_irrigation_control_refresh_from_mesh();
    next_os_alert_center_refresh_from_mesh();
}
