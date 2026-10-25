#include "mesh_state.h"

#include "config.h"

#include <cstring>

static uint8_t s_farm_count = 0;
static uint8_t s_alert_count = 0;
static uint8_t s_irig_count = 0;
static next_os_mesh_sensor_t s_sensor = {68, 6.4F, 24, 72};
static next_os_mesh_irrig_t s_irrig = {true, "14:23", "Flow 2.4 L/min • Plot A", "VALVE A1"};

static next_os_mesh_alert_t s_alerts[NEXT_OS_MESH_ALERT_BUFFER_SIZE];
static uint8_t s_alert_head = 0;
static uint8_t s_alert_size = 0;

void next_os_mesh_state_init(void) {
    s_farm_count = 3;
    s_alert_count = 2;
    s_irig_count = 1;
    s_alert_head = 0;
    s_alert_size = 0;
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
