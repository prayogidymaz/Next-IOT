#include "features/offline/offline_queue.h"

#include "mqtt.h"

#include <cstdio>

class SyncManager {
public:
    void init() {
        next_os_offline_queue().init();
    }

    void set_offline_mode(bool offline) {
        m_offline = offline;
        (void)std::printf("[SYNC] offline=%d queue=%zu\n", offline ? 1 : 0, next_os_offline_queue().size());
    }

    void on_sensor_sample(const OfflineSensorEvent &event) {
        if (m_offline || !next_os_mqtt_is_connected()) {
            (void)next_os_offline_queue().enqueue(event);
            return;
        }
        publish_one(event);
    }

    void tick() {
        if (!next_os_mqtt_is_connected()) {
            m_offline = true;
            return;
        }
        if (m_offline) {
            m_offline = false;
            m_backoff_ms = 500;
        }
        std::size_t batch = 0;
        OfflineSensorEvent ev{};
        while (batch < 10 && next_os_offline_queue().dequeue(&ev)) {
            if (!publish_one(ev)) {
                (void)next_os_offline_queue().enqueue(ev);
                m_backoff_ms = m_backoff_ms < 30000 ? m_backoff_ms * 2 : 30000;
                break;
            }
            batch += 1;
            m_backoff_ms = 500;
        }
    }

private:
    bool m_offline = false;
    unsigned int m_backoff_ms = 500;

    static bool publish_one(const OfflineSensorEvent &event) {
        return next_os_mqtt_publish_mesh_event(event.domain, "sensor_sample", event.payload);
    }
};

namespace {

SyncManager g_sync;

}  // namespace

SyncManager &next_os_sync_manager(void) {
    return g_sync;
}

void next_os_sync_manager_init(void) {
    g_sync.init();
}

void next_os_sync_manager_tick(void) {
    g_sync.tick();
}

void next_os_sync_manager_set_offline(bool offline) {
    g_sync.set_offline_mode(offline);
}
