#include "mesh_state.h"

#include <lvgl.h>

#include <cstdio>
#include <cstring>
#include <ctime>

static uint8_t s_farm_count = 0;
static uint8_t s_alert_count = 0;
static uint8_t s_irig_count = 0;
static next_os_mesh_sensor_t s_sensor = {68, 6.4F, 24, 72};
static next_os_mesh_irrig_t s_irrig = {true, "14:23", "Flow 2.4 L/min • Plot A", "VALVE A1"};

static next_os_mesh_alert_t s_alerts[NEXT_OS_MESH_ALERT_BUFFER_SIZE];
static uint8_t s_alert_head = 0;
static uint8_t s_alert_size = 0;

static next_os_mesh_cctv_t s_cctv = {"07:38:44", "Ulat grayak terdeteksi", "Plot B • Edge AI YOLO v8", 87,
                                     true};
static next_os_mesh_ndvi_t s_ndvi {};
static next_os_mesh_topology_t s_topology = {5, 1, 2, false};

static next_os_mesh_log_entry_t s_log[NEXT_OS_MESH_EVENT_LOG_SIZE];
static uint8_t s_log_head = 0;
static uint8_t s_log_size = 0;
static uint8_t s_log_revision = 0;

static uint32_t s_node_last_ms[NEXT_OS_MESH_NODE_COUNT] = {0};
static uint8_t s_recent_event_count = 0;
static next_os_mesh_workflow_t s_workflow {};

static void mesh_seed_ndvi(void) {
    static const uint8_t seed[NEXT_OS_MESH_NDVI_CELLS] = {
        4, 4, 3, 3, 2, 2, 1, 1, 4, 4, 3, 3, 2, 2, 1, 0, 3, 3, 3, 2, 2, 2, 1, 1,
        3, 3, 2, 2, 2, 1, 1, 0, 2, 2, 2, 1, 1, 1, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0,
        1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    };
    for (uint8_t i = 0; i < NEXT_OS_MESH_NDVI_CELLS; i++) {
        s_ndvi.cells[i] = seed[i];
    }
    s_ndvi.avg_ndvi = 0.68F;
    s_ndvi.stress_zones = 2;
    (void)std::snprintf(s_ndvi.timestamp, sizeof(s_ndvi.timestamp), "%s", "07:42");
}

void next_os_mesh_state_init(void) {
    s_farm_count = 3;
    s_alert_count = 2;
    s_irig_count = 1;
    s_alert_head = 0;
    s_alert_size = 0;
    s_log_head = 0;
    s_log_size = 0;
    mesh_seed_ndvi();

    next_os_mesh_log_entry_t boot_log {};
    (void)std::snprintf(boot_log.time, sizeof(boot_log.time), "%s", "07:41:02");
    (void)std::snprintf(boot_log.domain, sizeof(boot_log.domain), "%s", "ui");
    (void)std::snprintf(boot_log.event_type, sizeof(boot_log.event_type), "%s", "boot.ready");
    (void)std::snprintf(boot_log.payload, sizeof(boot_log.payload), "%s", "mesh feed online");
    next_os_mesh_state_push_log(&boot_log);
}

void next_os_mesh_state_set_farm_count(uint8_t count) {
    s_farm_count = count;
}

void next_os_mesh_state_set_alert_count(uint8_t count) {
    s_alert_count = count;
}

void next_os_mesh_state_set_irig_count(uint8_t count) {
    s_irig_count = count;
}

uint8_t next_os_mesh_state_farm_count(void) {
    return s_farm_count;
}

uint8_t next_os_mesh_state_alert_count(void) {
    return s_alert_count;
}

uint8_t next_os_mesh_state_irig_count(void) {
    return s_irig_count;
}

void next_os_mesh_state_update_sensor(const next_os_mesh_sensor_t *reading) {
    if (reading == nullptr) {
        return;
    }
    s_sensor = *reading;
}

next_os_mesh_sensor_t next_os_mesh_state_sensor(void) {
    return s_sensor;
}

void next_os_mesh_state_update_irrig(const next_os_mesh_irrig_t *irrig) {
    if (irrig == nullptr) {
        return;
    }
    s_irrig = *irrig;
}

next_os_mesh_irrig_t next_os_mesh_state_irrig(void) {
    return s_irrig;
}

void next_os_mesh_state_push_alert(const next_os_mesh_alert_t *alert) {
    if (alert == nullptr) {
        return;
    }
    const uint8_t idx =
        static_cast<uint8_t>((s_alert_head + s_alert_size) % NEXT_OS_MESH_ALERT_BUFFER_SIZE);
    s_alerts[idx] = *alert;
    if (s_alert_size < NEXT_OS_MESH_ALERT_BUFFER_SIZE) {
        s_alert_size++;
    } else {
        s_alert_head = static_cast<uint8_t>((s_alert_head + 1U) % NEXT_OS_MESH_ALERT_BUFFER_SIZE);
    }
}

bool next_os_mesh_state_top_alert(next_os_mesh_alert_t *out) {
    if (out == nullptr || s_alert_size == 0) {
        return false;
    }
    const uint8_t latest =
        static_cast<uint8_t>((s_alert_head + s_alert_size - 1U) % NEXT_OS_MESH_ALERT_BUFFER_SIZE);
    *out = s_alerts[latest];
    return true;
}

void next_os_mesh_state_update_cctv(const next_os_mesh_cctv_t *cctv) {
    if (cctv == nullptr) {
        return;
    }
    s_cctv = *cctv;
}

next_os_mesh_cctv_t next_os_mesh_state_cctv(void) {
    return s_cctv;
}

void next_os_mesh_state_update_ndvi(const next_os_mesh_ndvi_t *ndvi) {
    if (ndvi == nullptr) {
        return;
    }
    s_ndvi = *ndvi;
}

next_os_mesh_ndvi_t next_os_mesh_state_ndvi(void) {
    return s_ndvi;
}

void next_os_mesh_state_randomize_ndvi(void) {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < NEXT_OS_MESH_NDVI_CELLS; i++) {
        s_ndvi.cells[i] = static_cast<uint8_t>((i * 7U + s_log_size * 3U) % 5U);
        sum += s_ndvi.cells[i];
    }
    s_ndvi.avg_ndvi = static_cast<float>(sum) / static_cast<float>(NEXT_OS_MESH_NDVI_CELLS * 4U);
    s_ndvi.stress_zones = static_cast<uint8_t>(2U + (s_log_size % 2U));
    const std::time_t now = std::time(nullptr);
    std::tm lt {};
#if defined(_WIN32)
    if (now != static_cast<std::time_t>(-1) && localtime_s(&lt, &now) == 0) {
        (void)std::snprintf(s_ndvi.timestamp, sizeof(s_ndvi.timestamp), "%02d:%02d",
                            lt.tm_hour, lt.tm_min);
    }
#else
    std::tm *p = std::localtime(&now);
    if (p != nullptr) {
        lt = *p;
        (void)std::snprintf(s_ndvi.timestamp, sizeof(s_ndvi.timestamp), "%02d:%02d",
                            lt.tm_hour, lt.tm_min);
    }
#endif
}

void next_os_mesh_state_update_topology(const next_os_mesh_topology_t *topo) {
    if (topo == nullptr) {
        return;
    }
    s_topology = *topo;
}

next_os_mesh_topology_t next_os_mesh_state_topology(void) {
    return s_topology;
}

static next_os_mesh_node_id_t mesh_node_from_name(const char *node_name) {
    if (node_name == nullptr) {
        return NEXT_OS_MESH_NODE_HUB;
    }
    if (strcmp(node_name, "S2") == 0) {
        return NEXT_OS_MESH_NODE_S2;
    }
    if (strcmp(node_name, "S3") == 0) {
        return NEXT_OS_MESH_NODE_S3;
    }
    if (strcmp(node_name, "CAM") == 0) {
        return NEXT_OS_MESH_NODE_CAM;
    }
    if (strcmp(node_name, "DRN") == 0) {
        return NEXT_OS_MESH_NODE_DRN;
    }
    if (strcmp(node_name, "SPR") == 0) {
        return NEXT_OS_MESH_NODE_SPR;
    }
    if (strcmp(node_name, "GT") == 0) {
        return NEXT_OS_MESH_NODE_GT;
    }
    return NEXT_OS_MESH_NODE_HUB;
}

void next_os_mesh_state_touch_node_by_name(const char *node_name) {
    const next_os_mesh_node_id_t id = mesh_node_from_name(node_name);
    s_node_last_ms[id] = lv_tick_get();
    if (s_recent_event_count < 255) {
        s_recent_event_count++;
    }
}

uint32_t next_os_mesh_state_node_last_ms(next_os_mesh_node_id_t node) {
    if (node >= NEXT_OS_MESH_NODE_COUNT) {
        return 0;
    }
    return s_node_last_ms[node];
}

uint8_t next_os_mesh_state_recent_event_count(void) {
    return s_recent_event_count;
}

void next_os_mesh_state_update_workflow(const next_os_mesh_workflow_t *workflow) {
    if (workflow == nullptr) {
        return;
    }
    s_workflow = *workflow;
}

next_os_mesh_workflow_t next_os_mesh_state_workflow(void) {
    return s_workflow;
}

void next_os_mesh_state_push_log(const next_os_mesh_log_entry_t *entry) {
    if (entry == nullptr) {
        return;
    }
    const uint8_t idx =
        static_cast<uint8_t>((s_log_head + s_log_size) % NEXT_OS_MESH_EVENT_LOG_SIZE);
    s_log[idx] = *entry;
    if (s_log_size < NEXT_OS_MESH_EVENT_LOG_SIZE) {
        s_log_size++;
    } else {
        s_log_head = static_cast<uint8_t>((s_log_head + 1U) % NEXT_OS_MESH_EVENT_LOG_SIZE);
    }
    s_log_revision++;
}

uint8_t next_os_mesh_state_log_count(void) {
    return s_log_size;
}

uint8_t next_os_mesh_state_log_revision(void) {
    return s_log_revision;
}

bool next_os_mesh_state_log_at(uint8_t reverse_index, next_os_mesh_log_entry_t *out) {
    if (out == nullptr || reverse_index >= s_log_size) {
        return false;
    }
    const uint8_t pos =
        static_cast<uint8_t>((s_log_head + s_log_size - 1U - reverse_index) % NEXT_OS_MESH_EVENT_LOG_SIZE);
    *out = s_log[pos];
    return true;
}
