/**
 * State mesh in-memory — KPI, sensor, irigasi, alert buffer (RAM).
 */
#ifndef NEXT_OS_MESH_STATE_H
#define NEXT_OS_MESH_STATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    char title[48];
    char subtitle[64];
    char severity[16];
    char ago[16];
    bool unresolved;
} next_os_mesh_alert_t;

typedef struct {
    int32_t moisture;
    float ph;
    int32_t temp_c;
    int32_t humidity;
} next_os_mesh_sensor_t;

typedef struct {
    bool active;
    char countdown[8];
    char flow_label[48];
    char valve_name[32];
} next_os_mesh_irrig_t;

void next_os_mesh_state_init(void);

void next_os_mesh_state_set_farm_count(uint8_t count);
void next_os_mesh_state_set_alert_count(uint8_t count);
void next_os_mesh_state_set_irig_count(uint8_t count);

uint8_t next_os_mesh_state_farm_count(void);
uint8_t next_os_mesh_state_alert_count(void);
uint8_t next_os_mesh_state_irig_count(void);

void next_os_mesh_state_update_sensor(const next_os_mesh_sensor_t *reading);
next_os_mesh_sensor_t next_os_mesh_state_sensor(void);

void next_os_mesh_state_update_irrig(const next_os_mesh_irrig_t *irrig);
next_os_mesh_irrig_t next_os_mesh_state_irrig(void);

void next_os_mesh_state_push_alert(const next_os_mesh_alert_t *alert);
bool next_os_mesh_state_top_alert(next_os_mesh_alert_t *out);

#endif /* NEXT_OS_MESH_STATE_H */
