/**
 * ESP32-S3 LoRa PTT — Codec2 + I2S template (Arduino / PlatformIO)
 * Dependencies: RadioLib, esp_codec_dev or custom I2S driver, libcodec2
 */

#include <Arduino.h>
#include <RadioLib.h>
// #include <codec2.h>

#define I2S_MIC_BCLK  4
#define I2S_MIC_LRCK  5
#define I2S_MIC_DIN   6
#define I2S_SPK_BCLK  15
#define I2S_SPK_LRCK  16
#define I2S_SPK_DOUT  7

#define LORA_NSS   10
#define LORA_DIO1  11
#define LORA_RST   12
#define LORA_BUSY  13

#define PTT_PIN    0
#define NODE_ID    "SW-01"
#define LORA_CHANNEL 3

SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_RST, LORA_BUSY);

// struct c2 *c2 = codec2_create(CODEC2_MODE_1300);
// const int c2_samples = codec2_samples_per_frame(c2);
// const int c2_bytes = codec2_bytes_per_frame(c2);

volatile bool pttActive = false;

struct __attribute__((packed)) PttHeader {
  uint8_t version;
  uint8_t msg_type;
  uint8_t flags;
  uint8_t channel;
  uint32_t sender_id;
  uint32_t target_id;
  int32_t lat_e7;
  int32_t lon_e7;
  uint16_t seq;
  uint16_t payload_len;
};

void onPttPress() { pttActive = true; }
void onPttRelease() { pttActive = false; }

void setup() {
  Serial.begin(115200);
  pinMode(PTT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PTT_PIN), []() {
    pttActive = digitalRead(PTT_PIN) == LOW;
  }, CHANGE);

  // TODO: i2s_mic_begin(); i2s_spk_begin();
  // TODO: radio.begin(); radio.setFrequency(915.0);

  Serial.println("LoRa PTT Codec2 template ready");
}

void transmitVoiceBurst() {
  PttHeader hdr{};
  hdr.version = 0x01;
  hdr.msg_type = 0x01;
  hdr.flags = 0x01; // encrypted
  hdr.channel = LORA_CHANNEL;
  hdr.sender_id = 0x53573100; // placeholder
  hdr.target_id = 0xFFFFFFFF;
  hdr.seq = millis() & 0xFFFF;

  // int16_t pcm[c2_samples];
  // uint8_t codec_bytes[c2_bytes];
  // i2s_read_pcm(pcm, c2_samples);
  // codec2_encode(c2, codec_bytes, pcm);
  // hdr.payload_len = c2_bytes + 2;

  // uint8_t buf[256];
  // memcpy(buf, &hdr, sizeof(hdr));
  // buf[sizeof(hdr)] = 0x02; // codec2 mode 1300
  // buf[sizeof(hdr)+1] = 1;  // one frame
  // memcpy(buf + sizeof(hdr) + 2, codec_bytes, c2_bytes);
  // radio.transmit(buf, sizeof(hdr) + hdr.payload_len);
}

void loop() {
  if (pttActive) {
    transmitVoiceBurst();
    delay(40);
  } else {
    delay(5);
  }
}
