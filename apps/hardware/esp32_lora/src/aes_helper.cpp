#include "aes_helper.h"

#include "mbedtls/aes.h"

namespace {
constexpr size_t kKeyLen = 16;
constexpr size_t kIvLen = 16;
constexpr size_t kBlockSize = 16;

uint8_t gAesKey[kKeyLen];
bool gAesReady = false;

int hexNibble(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

bool loadKeyFromHex(const char* hex) {
  if (hex == nullptr) return false;
  size_t len = strlen(hex);
  if (len != kKeyLen * 2) return false;
  for (size_t i = 0; i < kKeyLen; ++i) {
    int hi = hexNibble(hex[i * 2]);
    int lo = hexNibble(hex[i * 2 + 1]);
    if (hi < 0 || lo < 0) return false;
    gAesKey[i] = static_cast<uint8_t>((hi << 4) | lo);
  }
  return true;
}

size_t pkcs7Pad(uint8_t* buffer, size_t length) {
  const uint8_t pad = static_cast<uint8_t>(kBlockSize - (length % kBlockSize));
  for (size_t i = 0; i < pad; ++i) {
    buffer[length + i] = pad;
  }
  return length + pad;
}
}  // namespace

bool loraAesInit() {
  gAesReady = loadKeyFromHex(LORA_AES_KEY_HEX);
  return gAesReady;
}

String loraEncryptPayload(const String& plaintext) {
  if (!gAesReady && !loraAesInit()) {
    return plaintext;
  }

  const size_t inputLen = plaintext.length();
  uint8_t* working = static_cast<uint8_t*>(malloc(inputLen + kBlockSize));
  if (working == nullptr) {
    return plaintext;
  }
  memcpy(working, plaintext.c_str(), inputLen);
  const size_t paddedLen = pkcs7Pad(working, inputLen);

  uint8_t iv[kIvLen];
  for (size_t i = 0; i < kIvLen; ++i) {
    iv[i] = static_cast<uint8_t>(esp_random() & 0xFF);
  }

  mbedtls_aes_context aes;
  mbedtls_aes_init(&aes);
  mbedtls_aes_setkey_enc(&aes, gAesKey, 128);

  uint8_t* output = static_cast<uint8_t*>(malloc(kIvLen + paddedLen));
  if (output == nullptr) {
    mbedtls_aes_free(&aes);
    free(working);
    return plaintext;
  }

  memcpy(output, iv, kIvLen);
  uint8_t ivCopy[kIvLen];
  memcpy(ivCopy, iv, kIvLen);
  mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, paddedLen, ivCopy, working, output + kIvLen);
  mbedtls_aes_free(&aes);
  free(working);

  String hexIvCipher;
  hexIvCipher.reserve(4 + (kIvLen + paddedLen) * 2);
  hexIvCipher += "ENC:";
  for (size_t i = 0; i < kIvLen + paddedLen; ++i) {
    char buf[3];
    snprintf(buf, sizeof(buf), "%02x", output[i]);
    hexIvCipher += buf;
  }
  free(output);
  return hexIvCipher;
}

String loraMaybeEncryptPayload(const String& plaintext) {
#if ENABLE_AES_ENCRYPTION
  return loraEncryptPayload(plaintext);
#else
  return plaintext;
#endif
}
