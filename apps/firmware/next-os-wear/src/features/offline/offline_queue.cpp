#include "features/offline/offline_queue.h"

#include <cstring>

#if defined(NEXT_OS_HARDWARE)
#include <LittleFS.h>
#endif

namespace {

OfflineQueue g_queue;

}  // namespace

void OfflineQueue::init() {
#if defined(NEXT_OS_HARDWARE)
    if (!LittleFS.begin(true)) {
        return;
    }
#endif
    m_head = 0;
    m_count = 0;
}

bool OfflineQueue::enqueue(const OfflineSensorEvent &event) {
    const std::size_t idx = (m_head + m_count) % kMaxEvents;
    if (m_count >= kMaxEvents) {
        m_head = (m_head + 1) % kMaxEvents;
        m_count = kMaxEvents - 1;
    }
    m_events[idx] = event;
    if (m_count < kMaxEvents) {
        m_count += 1;
    }
    return true;
}

bool OfflineQueue::dequeue(OfflineSensorEvent *out) {
    if (out == nullptr || m_count == 0) {
        return false;
    }
    *out = m_events[m_head];
    m_head = (m_head + 1) % kMaxEvents;
    m_count -= 1;
    return true;
}

std::size_t OfflineQueue::size() const {
    return m_count;
}

std::size_t OfflineQueue::capacity() const {
    return kMaxEvents;
}

OfflineQueue &next_os_offline_queue(void) {
    return g_queue;
}
