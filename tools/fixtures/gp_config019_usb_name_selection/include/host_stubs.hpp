#pragma once
// Host boundary only. Production bodies are extracted unchanged by the checker.
#include <config.pb.h>
#include <pb_decode.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>

struct RebootStop {};
struct Scratch {
    uint32_t value = 0;
    static inline std::vector<std::string> *events = nullptr;
    unsigned index = 0;
    operator uint32_t() const { return value; }
    Scratch &operator=(uint32_t next) {
        value = next;
        if (events) events->push_back("scratch" + std::to_string(index) + "=" + std::to_string(next));
        return *this;
    }
};
inline std::vector<std::string> events;
inline struct Watchdog { Scratch scratch[2]{{0, 0}, {0, 1}}; } watchdog;
inline Watchdog *watchdog_hw = &watchdog;
inline bool returning_reboot = false, rebooted = false;
inline void tud_disconnect() { events.push_back("disconnect"); }
inline void delay(unsigned value) { events.push_back("delay=" + std::to_string(value)); }
inline void reboot_firmware() { events.push_back("reboot"); if (!returning_reboot) throw RebootStop{}; }
inline bool watchdog_caused_reboot() { return rebooted; }

struct GameMode {
    GameModeConfig *config;
    GameModeConfig *GetConfig() { return config; }
};
struct IntegratedDisplay {
    GameMode *mode;
    GameMode *CurrentGameMode() { return mode; }
};
struct CommunicationBackend {
    GameMode *mode;
    GameMode *CurrentGameMode() { return mode; }
};
struct MenuPage {
    struct MenuItem {
        char text[32]{};
        uint8_t key = 0;
        void (*action)(IntegratedDisplay *, class ConfigMenu *, Config &, uint8_t) = nullptr;
    };
    MenuItem *items = nullptr;
    size_t items_count = 0;
};
class ConfigMenu {};
class DefaultConfigMenu : public ConfigMenu {
  public:
    CommunicationBackend **_backends;
    MenuPage _usb_backends_page;
    explicit DefaultConfigMenu(CommunicationBackend **backends) : _backends(backends) {}
    ~DefaultConfigMenu() { delete[] _usb_backends_page.items; }
    void BuildUsbPage(Config &config); // wrapper around exact constructor USB block
    static void SetUsbBackend(IntegratedDisplay *, ConfigMenu *, Config &, uint8_t);
};
inline const char *backend_name(CommunicationBackendId id) {
    switch (id) {
        case COMMS_BACKEND_XINPUT: return "XInput";
        case COMMS_BACKEND_DINPUT: return "DInput";
        case COMMS_BACKEND_NINTENDO_SWITCH: return "Switch";
        default: return "other";
    }
}
inline size_t strlcpy(char *dest, const char *src, size_t size) {
    const size_t length = std::strlen(src);
    if (size) { const size_t n = std::min(length, size - 1); std::memcpy(dest, src, n); dest[n] = 0; }
    return length;
}

inline std::vector<uint8_t> wire;
inline pb_istream_t as_pb_istream(const std::vector<uint8_t> &bytes) {
    return pb_istream_from_buffer(bytes.data(), bytes.size());
}
struct File {
    bool valid = true;
    explicit operator bool() const { return valid; }
    bool seek(size_t) { return true; }
    size_t available() const { return wire.size(); }
    void close() {}
};
inline pb_istream_t as_pb_istream(File &, size_t) { return as_pb_istream(wire); }
inline struct LittleFsStub { File open(const char *, const char *) { return File{}; } } LittleFS;
class Persistence {
  public:
    unsigned saves = 0;
    Config saved = Config_init_zero;
    const char *config_filename = "host-memory-only";
    size_t config_offset = 8;
    bool CheckSavedConfig(File &) { return true; } // valid header/CRC assumed, never claimed tested
    bool SaveConfig(Config &config) { ++saves; saved = config; return true; }
    bool LoadConfig(Config &);
};
inline Persistence persistence;
// HID constants are inert compile placeholders; keyboard key values are not tested.
constexpr uint8_t HID_KEY_1 = 0;
constexpr uint8_t HID_KEY_2 = 0;
constexpr uint8_t HID_KEY_3 = 0;
constexpr uint8_t HID_KEY_4 = 0;
constexpr uint8_t HID_KEY_5 = 0;
constexpr uint8_t HID_KEY_6 = 0;
constexpr uint8_t HID_KEY_7 = 0;
constexpr uint8_t HID_KEY_8 = 0;
constexpr uint8_t HID_KEY_9 = 0;
constexpr uint8_t HID_KEY_A = 0;
constexpr uint8_t HID_KEY_B = 0;
constexpr uint8_t HID_KEY_C = 0;
constexpr uint8_t HID_KEY_D = 0;
constexpr uint8_t HID_KEY_E = 0;
constexpr uint8_t HID_KEY_F = 0;
constexpr uint8_t HID_KEY_G = 0;
constexpr uint8_t HID_KEY_H = 0;
constexpr uint8_t HID_KEY_I = 0;
constexpr uint8_t HID_KEY_J = 0;
constexpr uint8_t HID_KEY_K = 0;
constexpr uint8_t HID_KEY_L = 0;
constexpr uint8_t HID_KEY_M = 0;
constexpr uint8_t HID_KEY_N = 0;
constexpr uint8_t HID_KEY_O = 0;
constexpr uint8_t HID_KEY_P = 0;
constexpr uint8_t HID_KEY_Q = 0;
constexpr uint8_t HID_KEY_R = 0;
constexpr uint8_t HID_KEY_S = 0;
constexpr uint8_t HID_KEY_T = 0;
constexpr uint8_t HID_KEY_U = 0;
constexpr uint8_t HID_KEY_V = 0;
constexpr uint8_t HID_KEY_W = 0;
constexpr uint8_t HID_KEY_X = 0;
constexpr uint8_t HID_KEY_Y = 0;
constexpr uint8_t HID_KEY_Z = 0;

class ConfiguratorBackend {
  public:
    Config &_config;
    const std::vector<uint8_t> &_in = wire;
    Command result = CMD_ERROR;
    explicit ConfiguratorBackend(Config &config) : _config(config) {}
    bool WritePacket(Command command, uint8_t *, size_t) { result = command; return true; }
    bool HandleSetConfig();
};

struct InputState { uint64_t buttons = 0; };
struct InputSource {};
struct Pinout {};
using backend_config_selector_t = void (*)(CommunicationBackendConfig &, const InputState &, Config &);
using usb_backend_getter_t = void (*)(CommunicationBackendConfig &, const Config &);
using detect_console_t = CommunicationBackendId (*)(const Pinout &);
using primary_backend_initializer_t = void (*)(CommunicationBackend *&, CommunicationBackendId,
    InputState &, InputSource **, size_t, Config &, const Pinout &);
using secondary_backend_initializer_t = size_t (*)(CommunicationBackend **&, CommunicationBackend *&,
    CommunicationBackendId, InputState &, InputSource **, size_t, Config &, const Pinout &);
inline GameModeConfig *selected_mode = nullptr;
inline void set_mode(CommunicationBackend *, GameModeConfig &mode, Config &) { selected_mode = &mode; }
