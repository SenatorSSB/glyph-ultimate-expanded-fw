#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>

typedef struct _Config Config;
typedef struct _UltimateProfile UltimateProfile;

class Print {
 public:
  virtual int availableForWrite() { return 64; }
  virtual ~Print() = default;
  virtual size_t write(uint8_t value) = 0;
  virtual size_t write(const uint8_t *data, size_t size) = 0;
};

class Stream : public Print {
 public:
  virtual int available() = 0;
  virtual int read() = 0;
  virtual int peek() = 0;
  virtual void flush() = 0;
  size_t readBytes(uint8_t *data, size_t length) {
    size_t read_count = 0;
    while (read_count < length) {
      const int value = read();
      if (value < 0) break;
      data[read_count++] = static_cast<uint8_t>(value);
    }
    return read_count;
  }
};

extern uint32_t host_millis;
inline uint32_t millis() { return host_millis; }
inline void delay(unsigned long amount) { host_millis += amount; }
inline size_t strlcpy(char *destination, const char *source, size_t size) {
  const size_t source_length = std::strlen(source);
  if (size != 0) {
    const size_t copied = source_length < size - 1 ? source_length : size - 1;
    std::memcpy(destination, source, copied);
    destination[copied] = '\0';
  }
  return source_length;
}

struct InputState {};
class InputSource {};
class CommunicationBackend {
 public:
  CommunicationBackend(InputState &, InputSource **, size_t) {}
  virtual ~CommunicationBackend() = default;
  virtual void SendReport() = 0;
};

struct TinyUSBDeviceStub { void setID(uint16_t, uint16_t) {} };
inline TinyUSBDeviceStub TinyUSBDevice;
inline void reboot_firmware() {}
inline void reboot_bootloader() {}

#define FIRMWARE_NAME "host"
#define FIRMWARE_VERSION "host"
#define DEVICE_NAME "host"
