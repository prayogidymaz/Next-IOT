#pragma once

#include "features/offline/offline_queue.h"

class SyncManager;

SyncManager &next_os_sync_manager(void);
void next_os_sync_manager_init(void);
void next_os_sync_manager_tick(void);
void next_os_sync_manager_set_offline(bool offline);
