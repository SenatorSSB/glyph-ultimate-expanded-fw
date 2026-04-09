#ifndef _DISPLAY_MENUBUTTONHINTS_HPP
#define _DISPLAY_MENUBUTTONHINTS_HPP

#include "core/CommunicationBackend.hpp"
#include "display/DisplayMode.hpp"

class MenuButtonHints : public DisplayMode {
  public:
    MenuButtonHints(CommunicationBackend **backends, size_t backends_count);
    DisplayModeId GetId();
    void HandleControls(
        IntegratedDisplay *instance,
        const DisplayControls &controls,
        Button button
    );
    void UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display);

    void UpdateButtonHints(IntegratedDisplay *instance);

  protected:
    const char *CurrentlyPressedButtonText();

    CommunicationBackend **_backends;
    const size_t _backends_count;
    CommunicationBackendId _backend_id = COMMS_BACKEND_UNSPECIFIED;

    #ifdef NDEBUG
    absolute_time_t _pressed_output_locked_until = 0;
    #else
    absolute_time_t _pressed_output_locked_until = { ._private_us_since_boot = 0};
    #endif
    const char *_last_pressed_button_text;

    const unsigned char *mb1_bmp = nullptr;
    const unsigned char *mb2_bmp = nullptr;
    const unsigned char *mb3_bmp = nullptr;
    const unsigned char *mb4_bmp = nullptr;
    const unsigned char *mb5_bmp = nullptr;
    const unsigned char *mb6_bmp = nullptr;
    const unsigned char *mb7_bmp = nullptr;
};

#endif