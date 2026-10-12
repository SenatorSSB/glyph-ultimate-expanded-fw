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

struct ConfigValidationError { const char *message = "invalid"; size_t length = 7; };

class Persistence {
 public:
  bool CheckSavedConfig() { return true; }
  size_t LoadConfigRaw(Print &, bool = true) { return 0; }
  bool ValidateConfig(const Config &, ConfigValidationError &) const { return true; }
  bool SaveConfig(Config &) { ++save_calls; return true; }
  uint32_t ConfigGeneration(const Config &) const { return 17; }
  unsigned save_calls = 0;
};
extern Persistence persistence;

class ProfileStore {
 public:
  static constexpr uint8_t kCompactConfigFormat = 1;
  enum class Status : uint8_t { Ok, NotFound, Invalid, Conflict, Full, IoFailure, UnknownOutcome, Referenced };
  struct Entry { uint32_t id; uint32_t revision; uint32_t payload_version; uint32_t rank; char name[18]; };
  struct TransactionResult { Status status = Status::NotFound; uint32_t id = 0; uint32_t revision = 0; uint32_t generation = 0; };
  bool IsReady() const { return true; }
  uint32_t Generation() const { return 23; }
  size_t Count() const { return 0; }
  const Entry *EntryAt(size_t) const { return nullptr; }
  Status Read(uint32_t, UltimateProfile &, uint32_t * = nullptr) const { return Status::NotFound; }
  TransactionResult Create(const UltimateProfile &, const char *, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult Update(uint32_t, const UltimateProfile &, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult Duplicate(uint32_t, uint32_t, const char *, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult Rename(uint32_t, const char *, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult Reorder(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult Delete(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t) { ++mutation_calls; return {}; }
  TransactionResult QueryTransaction(uint32_t, uint32_t) const { return {}; }
  unsigned mutation_calls = 0;
};
extern ProfileStore profile_store;

struct TinyUSBDeviceStub { void setID(uint16_t, uint16_t) {} };
inline TinyUSBDeviceStub TinyUSBDevice;
inline void reboot_firmware() {}
inline void reboot_bootloader() {}

#define FIRMWARE_NAME "host"
#define FIRMWARE_VERSION "host"
#define DEVICE_NAME "host"
