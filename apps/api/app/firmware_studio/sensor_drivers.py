"""Metric → Arduino sensor driver catalog for Firmware Studio."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SensorDriverSpec:
    library: str
    include_header: str
    global_decl: str
    init_code: str
    read_expr: str


SENSOR_DRIVERS: dict[str, dict[str, SensorDriverSpec]] = {
    "temperature": {
        "dht22": SensorDriverSpec(
            library="adafruit/DHT sensor library@^1.4.6",
            include_header="#include <DHT.h>",
            global_decl="DHT dhtSensor({pin}, DHT22);",
            init_code="dhtSensor.begin();",
            read_expr="dhtSensor.readTemperature()",
        ),
        "bmp280": SensorDriverSpec(
            library="adafruit/Adafruit BMP280 Library@^2.6.8",
            include_header="#include <Adafruit_BMP280.h>",
            global_decl="Adafruit_BMP280 bmpSensor;",
            init_code="if (!bmpSensor.begin(0x76)) { Serial.println(F(\"BMP280 init failed\")); }",
            read_expr="bmpSensor.readTemperature()",
        ),
    },
    "humidity": {
        "dht22": SensorDriverSpec(
            library="adafruit/DHT sensor library@^1.4.6",
            include_header="#include <DHT.h>",
            global_decl="DHT dhtSensor({pin}, DHT22);",
            init_code="dhtSensor.begin();",
            read_expr="dhtSensor.readHumidity()",
        ),
        "sht30": SensorDriverSpec(
            library="adafruit/Adafruit SHT31 Library@^2.2.2",
            include_header="#include <Adafruit_SHT31.h>",
            global_decl="Adafruit_SHT31 shtSensor = Adafruit_SHT31();",
            init_code="shtSensor.begin(0x44);",
            read_expr="shtSensor.readHumidity()",
        ),
    },
    "pressure": {
        "bmp280": SensorDriverSpec(
            library="adafruit/Adafruit BMP280 Library@^2.6.8",
            include_header="#include <Adafruit_BMP280.h>",
            global_decl="Adafruit_BMP280 bmpSensor;",
            init_code="bmpSensor.begin(0x76);",
            read_expr="bmpSensor.readPressure() / 100.0F",
        ),
    },
    "soil_moisture": {
        "analog": SensorDriverSpec(
            library="",
            include_header="",
            global_decl="const int soilPin = {pin};",
            init_code="pinMode(soilPin, INPUT);",
            read_expr="(float)analogRead(soilPin)",
        ),
    },
    "light_lux": {
        "bh1750": SensorDriverSpec(
            library="claws/BH1750@^1.3.0",
            include_header="#include <BH1750.h>",
            global_decl="BH1750 lightSensor;",
            init_code="lightSensor.begin();",
            read_expr="lightSensor.readLightLevel()",
        ),
    },
}


def drivers_for_metric(metric: str) -> dict[str, SensorDriverSpec]:
    return SENSOR_DRIVERS.get(metric, {})


def catalog_public() -> dict[str, list[str]]:
    return {metric: sorted(drivers.keys()) for metric, drivers in SENSOR_DRIVERS.items()}


def resolve_driver(metric: str, driver: str) -> SensorDriverSpec:
    options = drivers_for_metric(metric)
    spec = options.get(driver)
    if spec is None:
        raise ValueError(f"Unknown driver '{driver}' for metric '{metric}'")
    return spec
