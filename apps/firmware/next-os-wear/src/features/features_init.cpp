#include "features/features_init.h"

#include "features/ble/ble_pairing.h"
#include "features/ble/notification_handler.h"
#include "features/haptic/haptic_engine.h"
#include "features/offline/sync_manager.h"
#include "features/watch_face/face_switcher.h"

void next_os_features_init(void) {
    next_os_ble_init();
    next_os_notification_handler_init();
    next_os_haptic_engine().init();
    next_os_sync_manager_init();
    next_os_face_switcher_init();
}

void next_os_features_tick(void) {
    next_os_ble_loop();
    next_os_sync_manager_tick();
    next_os_face_switcher_tick();
}

void next_os_features_mount_watch_face(lv_obj_t *parent) {
    next_os_face_switcher_mount(parent);
}
