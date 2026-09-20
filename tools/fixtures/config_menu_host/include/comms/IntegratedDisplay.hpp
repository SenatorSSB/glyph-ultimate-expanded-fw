#pragma once
#include <cstddef>
#include <cstdint>
#include "config.pb.h"

struct InputState { bool mb1 = false; bool mb2 = false; bool mb3 = false; bool mb4 = false; };
class Adafruit_GFX {
  public:
    void setFont(const void *) {}
    void setTextWrap(bool) {}
    void drawBitmap(int, int, const unsigned char *, int, int, int) {}
    void setCursor(int, int) {}
    void print(const char *) {}
    void print(char) {}
    void println(const char *) {}
    void fillRect(int, int, int, int, int) {}
    void fillScreen(int) {}
};
enum Button { BTN_NONE = 0, BTN_MB1, BTN_MB2, BTN_MB3, BTN_MB4 };
struct DisplayControls { Button back; Button down; Button up; Button enter; };
enum DisplayModeId { DISPLAY_MODE_VIEWER = 0, DISPLAY_MODE_CONFIG = 1, DISPLAY_MODE_RGB_BRIGHTNESS = 2, DISPLAY_MODE_ABOUT = 3, DISPLAY_MODE_BUTTON_HINTS = 4 };
enum DashboardOption { DASHBOARD_MENU_BUTTON_HINTS = 0, DASHBOARD_INPUT_VIEWER = 1 };
class InputMode {
  public:
    explicit InputMode(GameModeConfig *config = nullptr) : config_(config) {}
    GameModeConfig *GetConfig() { return config_; }
  private:
    GameModeConfig *config_;
};
class CommunicationBackend {
  public:
    explicit CommunicationBackend(CommunicationBackendId id, InputMode *mode = nullptr) : id_(id), mode_(mode) {}
    CommunicationBackendId BackendId() { return id_; }
    InputMode *CurrentGameMode() { return mode_; }
    void SetGameMode(InputMode *mode) { mode_ = mode; }
  private:
    CommunicationBackendId id_;
    InputMode *mode_;
};
class IntegratedDisplay {
  public:
    Adafruit_GFX _display;
    InputState inputs;
    InputState &GetInputs() { return inputs; }
    InputMode *CurrentGameMode() { return mode_; }
    void SetGameMode(InputMode *mode) { mode_ = mode; }
    void SetDisplayMode(DisplayModeId mode) { display_mode_ = mode; }
    void Clear() {}
    void UpdateDisplay() {}
    std::uint8_t font_width = 6;
    std::uint8_t font_height = 8;
  private:
    InputMode *mode_ = nullptr;
    DisplayModeId display_mode_ = DISPLAY_MODE_VIEWER;
};
