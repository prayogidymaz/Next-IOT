#pragma once

#include <cstddef>
#include <cstdint>

struct OfflineSensorEvent {
    int64_t ts_ms;
    char domain[16];
    char payload[128];
};

class OfflineQueue {
public:
    void init();
    bool enqueue(const OfflineSensorEvent &event);
    bool dequeue(OfflineSensorEvent *out);
    std::size_t size() const;
    std::size_t capacity() const;

private:
    static constexpr std::size_t kMaxEvents = 500;
    OfflineSensorEvent m_events[kMaxEvents];
    std::size_t m_head = 0;
    std::size_t m_count = 0;
};

OfflineQueue &next_os_offline_queue(void);
