#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <vector>

enum CommunicationBackendId {
    COMMS_BACKEND_UNSPECIFIED = 0,
    COMMS_BACKEND_DINPUT = 1,
    COMMS_BACKEND_XINPUT = 2,
    COMMS_BACKEND_GAMECUBE = 3,
    COMMS_BACKEND_N64 = 4,
    COMMS_BACKEND_NES = 5,
    COMMS_BACKEND_SNES = 6,
};
enum GameModeId {
    MODE_UNSPECIFIED = 0, MODE_MELEE = 1, MODE_PROJECT_M = 2,
    MODE_ULTIMATE = 3, MODE_FGC = 4, MODE_RIVALS_OF_AETHER = 5,
    MODE_KEYBOARD = 6, MODE_CUSTOM = 7, MODE_64 = 8, MODE_RIVALS2 = 9,
};

struct GameModeConfig {
    char name[18]{};
    uint8_t keyboard_mode_config = 0;
    GameModeId mode_id = MODE_UNSPECIFIED;
    uint32_t custom_mode_config = 0;
};

struct CommunicationBackendConfig {
    uint8_t backend_id = 0;
};

struct Config {
    size_t game_mode_configs_count = 0;
    GameModeConfig game_mode_configs[30]{};
    size_t communication_backend_configs_count = 0;
    CommunicationBackendConfig communication_backend_configs[15]{};
    size_t keyboard_modes_count = 0;
    size_t custom_modes_count = 0;
    uint8_t melee_options = 0;
    uint8_t project_m_options = 0;
    uint8_t keyboard_modes[10]{};
    uint8_t custom_modes[10]{};
};

class InputMode {
  public:
    InputMode() = default;
    GameModeConfig *GetConfig();
    void SetConfig(GameModeConfig &config);
  protected:
    GameModeConfig *_config = nullptr;
};

class ControllerMode : public InputMode {};
class KeyboardMode : public InputMode {
  public:
    void SetConfig(GameModeConfig &config, uint8_t) { InputMode::SetConfig(config); }
};
class StubMode : public ControllerMode {
  public:
    void SetConfig(GameModeConfig &config) { InputMode::SetConfig(config); }
    void SetConfig(GameModeConfig &config, uint8_t) { InputMode::SetConfig(config); }
};

class CommunicationBackend {
  public:
    explicit CommunicationBackend(CommunicationBackendId id = COMMS_BACKEND_XINPUT) : id_(id) {}
    CommunicationBackendId BackendId() { return id_; }
    void SetGameMode(InputMode *mode) { mode_ = mode; }
    InputMode *CurrentGameMode() { return mode_; }
  private:
    CommunicationBackendId id_;
    InputMode *mode_ = nullptr;
};

class IntegratedDisplay {
  public:
    explicit IntegratedDisplay(CommunicationBackend *backend = nullptr) : backend_(backend) {}
    InputMode *CurrentGameMode() { return backend_ == nullptr ? nullptr : backend_->CurrentGameMode(); }

  private:
    CommunicationBackend *backend_;
};

class ConfigMenu {};

class DefaultConfigMenu {
  public:
    static void SetUsbBackend(IntegratedDisplay *, ConfigMenu *, Config &, uint8_t);
};

extern std::vector<std::string> effects;

struct ScratchSlot {
    uint32_t value = 0;
    size_t index = 0;
    ScratchSlot &operator=(uint32_t next) {
        value = next;
        effects.emplace_back("scratch:" + std::to_string(index) + "=" + std::to_string(next));
        return *this;
    }
};

struct WatchdogState {
    ScratchSlot scratch[2]{{0, 0}, {0, 1}};
};

extern WatchdogState *watchdog_hw;
extern size_t current_mode_index;
extern KeyboardMode *current_kb_mode;
extern StubMode melee_mode;
extern StubMode projectm_mode;
extern StubMode ultimate_mode;
extern StubMode fgc_mode;
extern StubMode rivals_mode;
extern StubMode rivals2_mode;
extern KeyboardMode keyboard_mode;
extern StubMode custom_mode;
extern StubMode s64_mode;

void set_mode(CommunicationBackend *, ControllerMode *);
void set_mode(CommunicationBackend *, KeyboardMode *);
void set_mode(CommunicationBackend *, GameModeConfig &, Config &);

void tud_disconnect();
void delay(uint32_t milliseconds);
void reboot_firmware();
