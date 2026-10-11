#pragma once

#include <ArduinoJson.h>

#include "NextIotConfig.h"

void nextiotOtaHandleMessage(const NextIotConfig& config, JsonObject payload);
