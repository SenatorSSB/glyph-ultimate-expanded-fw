#pragma once
#include "comms/IntegratedDisplay.hpp"
class DisplayMode {
  public:
    virtual ~DisplayMode() = default;
    virtual DisplayModeId GetId() = 0;
    virtual void HandleControls(IntegratedDisplay *, const DisplayControls &, Button) {}
    virtual void UpdateDisplay(IntegratedDisplay *, Adafruit_GFX &) {}
    virtual void ReturnToDashboard(IntegratedDisplay *) {}
};
