#include "features/ble/notification_handler.h"

#include <ArduinoJson.h>

#include <cstdio>
#include <cstring>

namespace {

struct ParsedNotification {
    char type[32];
    char title[64];
    char body[128];
    int priority;
};

bool parse_notification(const char *json, std::size_t len, ParsedNotification *out) {
    if (out == nullptr || json == nullptr) {
        return false;
    }
    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, json, len);
    if (err) {
        return false;
    }
    const char *type = doc["type"] | "generic";
    const char *title = doc["title"] | "";
    const char *body = doc["body"] | "";
    const int priority = doc["priority"] | 1;
    (void)std::strncpy(out->type, type, sizeof(out->type) - 1);
    (void)std::strncpy(out->title, title, sizeof(out->title) - 1);
    (void)std::strncpy(out->body, body, sizeof(out->body) - 1);
    out->priority = priority;
    return true;
}

void show_in_notification_center(const ParsedNotification &n) {
    (void)std::printf("[NOTIF] type=%s priority=%d title=%s body=%s\n", n.type, n.priority, n.title, n.body);
}

}  // namespace

void next_os_notification_handler_init(void) {}

void next_os_notification_handler_on_ble_payload(const char *json, std::size_t len) {
    ParsedNotification parsed{};
    if (!parse_notification(json, len, &parsed)) {
        (void)std::printf("[NOTIF] Invalid JSON payload\n");
        return;
    }
    show_in_notification_center(parsed);
}
