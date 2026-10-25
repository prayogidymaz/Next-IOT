#ifndef NEXT_OS_MESH_HANDLER_H
#define NEXT_OS_MESH_HANDLER_H

#include <stddef.h>
#include <stdint.h>

void next_os_mesh_handler_init(void);

void next_os_mesh_handler_on_message(const char *topic, const uint8_t *payload, size_t length);

#endif /* NEXT_OS_MESH_HANDLER_H */
