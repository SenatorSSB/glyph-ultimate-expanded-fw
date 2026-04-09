#ifndef _DISPLAY_REMAPMENU_HPP
#define _DISPLAY_REMAPMENU_HPP

#include "display/DisplayMode.hpp"

class RemapMenu : public DisplayMode {
  public:
    RemapMenu();
    DisplayModeId GetId();
    void HandleControls(
        IntegratedDisplay *instance,
        const DisplayControls &controls,
        Button button
    );
    void UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display);
};

#endif