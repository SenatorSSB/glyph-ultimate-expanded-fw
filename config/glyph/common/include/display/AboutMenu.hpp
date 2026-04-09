#ifndef _DISPLAY_ABOUTMENU_HPP
#define _DISPLAY_ABOUTMENU_HPP

#include "display/DisplayMode.hpp"

class AboutMenu : public DisplayMode {
  public:
    AboutMenu(Config &config);
    DisplayModeId GetId();
    void HandleControls(
        IntegratedDisplay *instance,
        const DisplayControls &controls,
        Button button
    );
    void UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display);

  private:
    Config &_config;
};

#endif