#pragma once

#include <HTTPClient.h>

class OTAUpdater {
 public:
  bool checkAndUpdate(const char* apiBase, const char* deviceType, const char* currentVersion);
};
