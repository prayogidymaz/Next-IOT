#include "features/ble/ble_pairing.h"

#include <cstdio>
#include <cstring>

#if defined(NEXT_OS_HARDWARE)
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <esp_mac.h>
#endif

namespace {

constexpr const char *kServiceUuid = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
constexpr const char *kCharDeviceInfo = "6e400010-b5a3-f393-e0a9-e50e24dcca9e";
constexpr const char *kCharSensorData = "6e400011-b5a3-f393-e0a9-e50e24dcca9e";
constexpr const char *kCharNotificationRelay = "6e400012-b5a3-f393-e0a9-e50e24dcca9e";
constexpr const char *kCharTimeSync = "6e400013-b5a3-f393-e0a9-e50e24dcca9e";

bool s_paired = false;
char s_device_name[24] = "NextWatch-0000";

void build_device_name(void) {
#if defined(NEXT_OS_HARDWARE)
    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    (void)std::snprintf(s_device_name, sizeof(s_device_name), "NextWatch-%02X%02X", mac[4], mac[5]);
#else
    (void)std::strncpy(s_device_name, "NextWatch-SIM", sizeof(s_device_name) - 1);
#endif
}

}  // namespace

void next_os_ble_init(void) {
    build_device_name();
#if defined(NEXT_OS_HARDWARE)
    BLEDevice::init(s_device_name);
    BLEServer *server = BLEDevice::createServer();
    BLEService *service = server->createService(kServiceUuid);
    service->createCharacteristic(kCharDeviceInfo, BLECharacteristic::PROPERTY_READ);
    service->createCharacteristic(kCharSensorData, BLECharacteristic::PROPERTY_NOTIFY);
    service->createCharacteristic(kCharNotificationRelay, BLECharacteristic::PROPERTY_WRITE);
    service->createCharacteristic(kCharTimeSync, BLECharacteristic::PROPERTY_WRITE);
    service->start();
    BLEAdvertising *adv = BLEDevice::getAdvertising();
    adv->addServiceUUID(kServiceUuid);
    adv->setScanResponse(true);
    BLEDevice::startAdvertising();
    (void)std::printf("[BLE] GATT server started as %s\n", s_device_name);
#else
    (void)kCharDeviceInfo;
    (void)kCharSensorData;
    (void)kCharNotificationRelay;
    (void)kCharTimeSync;
    (void)std::printf("[BLE] Simulator mock GATT (%s)\n", s_device_name);
#endif
}

void next_os_ble_loop(void) {}

bool next_os_ble_is_paired(void) {
    return s_paired;
}

#if defined(NEXT_OS_SIMULATOR)
void next_os_ble_simulate_pair_toggle(void) {
    s_paired = !s_paired;
    (void)std::printf("[BLE] Simulated pair state: %s\n", s_paired ? "paired" : "unpaired");
}
#endif
