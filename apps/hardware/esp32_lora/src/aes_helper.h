#pragma once

#include <Arduino.h>

#ifndef ENABLE_AES_ENCRYPTION
#define ENABLE_AES_ENCRYPTION true
#endif

#ifndef LORA_AES_KEY_HEX
#define LORA_AES_KEY_HEX "00112233445566778899aabbccddeeff"
#endif

bool loraAesInit();
String loraEncryptPayload(const String& plaintext);
String loraMaybeEncryptPayload(const String& plaintext);
