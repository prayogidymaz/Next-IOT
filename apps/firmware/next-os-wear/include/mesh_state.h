/**
 * State mesh in-memory — KPI, sensor, irigasi, alert buffer (RAM).
 */
#ifndef NEXT_OS_MESH_STATE_H
#define NEXT_OS_MESH_STATE_H

#include "config.h"

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

typedef struct {
    char timestamp[16];
    char title[48];
    char subtitle[64];
    uint8_t pest_pct;
    bool live;
} next_os_mesh_cctv_t;

typedef struct {
    uint8_t cells[NEXT_OS_MESH_NDVI_CELLS];
    float avg_ndvi;
    uint8_t stress_zones;
    char timestamp[16];
} next_os_mesh_ndvi_t;

typedef struct {
    uint8_t live_nodes;
    uint8_t dispatch_nodes;
    uint8_t idle_nodes;
    bool drn_dispatch_pulse;
} next_os_mesh_topology_t;

typedef struct {
    char time[12];
    char domain[16];
    char event_type[32];
    char payload[72];
    char correlation_id[32];
} next_os_mesh_log_entry_t;

typedef struct {
    char correlation_id[32];
    char workflow_name[32];
    uint8_t step;
    uint8_t total;
    bool active;
    bool failed;
} next_os_mesh_workflow_t;

typedef enum {
    NEXT_OS_MESH_NODE_HUB = 0,
    NEXT_OS_MESH_NODE_S2,
    NEXT_OS_MESH_NODE_S3,
    NEXT_OS_MESH_NODE_CAM,
    NEXT_OS_MESH_NODE_DRN,
    NEXT_OS_MESH_NODE_SPR,
    NEXT_OS_MESH_NODE_GT,
    NEXT_OS_MESH_NODE_COUNT,
} next_os_mesh_node_id_t;

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

void next_os_mesh_state_update_cctv(const next_os_mesh_cctv_t *cctv);
next_os_mesh_cctv_t next_os_mesh_state_cctv(void);

void next_os_mesh_state_update_ndvi(const next_os_mesh_ndvi_t *ndvi);
next_os_mesh_ndvi_t next_os_mesh_state_ndvi(void);
void next_os_mesh_state_randomize_ndvi(void);

void next_os_mesh_state_update_topology(const next_os_mesh_topology_t *topo);
next_os_mesh_topology_t next_os_mesh_state_topology(void);

void next_os_mesh_state_push_log(const next_os_mesh_log_entry_t *entry);
uint8_t next_os_mesh_state_log_count(void);
bool next_os_mesh_state_log_at(uint8_t reverse_index, next_os_mesh_log_entry_t *out);
uint8_t next_os_mesh_state_log_revision(void);

void next_os_mesh_state_touch_node_by_name(const char *node_name);
uint32_t next_os_mesh_state_node_last_ms(next_os_mesh_node_id_t node);
uint8_t next_os_mesh_state_recent_event_count(void);

void next_os_mesh_state_update_workflow(const next_os_mesh_workflow_t *workflow);
next_os_mesh_workflow_t next_os_mesh_state_workflow(void);

#endif /* NEXT_OS_MESH_STATE_H */
