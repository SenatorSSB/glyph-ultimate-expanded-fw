#ifndef GLYPH_CONFIGURATOR_SETCONFIG_HOST_STUBS_HPP
#define GLYPH_CONFIGURATOR_SETCONFIG_HOST_STUBS_HPP

#include <cstddef>
#include <cstdint>
#include <cstdio>

#ifdef EOF
#undef EOF
#endif

class Print {
  public:
    virtual ~Print() = default;
    virtual size_t write(uint8_t value) = 0;
    virtual size_t write(const uint8_t *buffer, size_t size) = 0;
};

class Stream : public Print {
  public:
    virtual int available() = 0;
    virtual int read() = 0;
    virtual int peek() = 0;
    virtual void flush() = 0;
};

namespace packetio {

class COBSStream : public Stream {
  public:
    static constexpr int EOF = -1;
    static constexpr int EOP = -2;

    explicit COBSStream(Stream &stream) : _stream(stream) {}
    int available() override { return _stream.available(); }
    int read() override { return _stream.read(); }
    int peek() override { return _stream.peek(); }
    void flush() override { _stream.flush(); }
    size_t write(uint8_t value) override { return _stream.write(value); }
    size_t write(const uint8_t *buffer, size_t size) override {
        return _stream.write(buffer, size);
    }
    void next() {}

  private:
    Stream &_stream;
};

class COBSPrint : public Print {
  public:
    explicit COBSPrint(Stream &stream) : _stream(stream) {}
    size_t write(uint8_t value) override { return _stream.write(value); }
    size_t write(const uint8_t *buffer, size_t size) override {
        return _stream.write(buffer, size);
    }
    bool end() { return true; }

  private:
    Stream &_stream;
};

}  // namespace packetio

using pb_size_t = size_t;

enum Command {
    CMD_UNSPECIFIED = 0,
    CMD_GET_DEVICE_INFO = 1,
    CMD_SET_DEVICE_INFO = 2,
    CMD_GET_CONFIG = 3,
    CMD_SET_CONFIG = 4,
    CMD_ERROR = 5,
    CMD_SUCCESS = 6,
    CMD_REBOOT_FIRMWARE = 7,
    CMD_REBOOT_BOOTLOADER = 8,
};

enum CommunicationBackendId {
    COMMS_BACKEND_UNSPECIFIED = 0,
    COMMS_BACKEND_CONFIGURATOR = 8,
};

enum GameModeId {
    MODE_UNSPECIFIED = 0,
    MODE_MELEE = 1,
    MODE_KEYBOARD = 6,
    MODE_CUSTOM = 7,
};

struct GameModeConfig {
    GameModeId mode_id;
    char name[18];
    uint32_t embedded_values[24];
    uint32_t custom_mode_config;
    uint8_t keyboard_mode_config;
    uint8_t rgb_config;
};

struct CommunicationBackendConfig {
    CommunicationBackendId backend_id;
    uint8_t default_mode_config;
    uint32_t embedded_values[4];
};

struct CustomModeConfig {
    uint8_t id;
    uint32_t digital_button_mappings[18];
    uint32_t embedded_values[24];
};

struct KeyboardModeConfig {
    uint8_t id;
    uint32_t buttons_to_keycodes[60];
};

struct RgbConfig {
    uint32_t embedded_values[64];
};

struct Config {
    pb_size_t game_mode_configs_count;
    GameModeConfig game_mode_configs[30];
    pb_size_t communication_backend_configs_count;
    CommunicationBackendConfig communication_backend_configs[15];
    pb_size_t custom_modes_count;
    CustomModeConfig custom_modes[10];
    pb_size_t keyboard_modes_count;
    KeyboardModeConfig keyboard_modes[10];
    pb_size_t rgb_configs_count;
    RgbConfig rgb_configs[30];
    uint8_t default_backend_config;
    uint8_t default_usb_backend_config;
    uint8_t rgb_brightness;
    uint32_t trailing_options[8];
};

#define Config_init_default Config{}

struct DeviceInfo {
    char firmware_name[26];
    char firmware_version[31];
    char device_name[31];
};

inline constexpr int Config_msg = 0;
inline constexpr int DeviceInfo_msg = 0;
#define Config_fields (&Config_msg)
#define DeviceInfo_fields (&DeviceInfo_msg)

struct pb_istream_t {
    const char *errmsg;
};

struct pb_ostream_t {
    size_t bytes_written;
};

pb_istream_t as_pb_istream(Stream &stream);
pb_ostream_t as_pb_ostream(Print &output);
bool pb_decode(pb_istream_t *stream, const void *fields, void *destination);
inline bool pb_encode(pb_ostream_t *, const void *, const void *) { return true; }
inline bool pb_get_encoded_size(size_t *size, const void *, const void *) {
    *size = 0;
    return true;
}

struct InputState {};
class InputSource {};
class InputMode {};
enum InputScanSpeed { INPUT_SCAN_SPEED_STUB = 0 };
struct OutputState {};

class CommunicationBackend {
  public:
    CommunicationBackend(InputState &, InputSource **, size_t) {}
    virtual ~CommunicationBackend() = default;
    virtual void SendReport() = 0;
};

class Persistence {
  public:
    bool SaveConfig(Config &config);
    bool LoadConfig(Config &) { return false; }
    bool CheckSavedConfig() { return true; }
    size_t LoadConfigRaw(Print &, bool = true) { return 0; }
};

extern Persistence persistence;

struct TinyUSBDeviceStub {
    void setID(uint16_t, uint16_t) {}
};

inline TinyUSBDeviceStub TinyUSBDevice;
inline void reboot_firmware() {}
inline void reboot_bootloader() {}
inline void delay(unsigned long) {}

#ifndef FIRMWARE_NAME
#define FIRMWARE_NAME "host-test"
#endif
#ifndef FIRMWARE_VERSION
#define FIRMWARE_VERSION "host-test"
#endif
#ifndef DEVICE_NAME
#define DEVICE_NAME "host-test"
#endif

#endif
