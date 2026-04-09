#ifndef _DISPLAY_OOPSIEMENU_HPP
#define _DISPLAY_OOPSIEMENU_HPP

#include "comms/IntegratedDisplay.hpp"
#include "display/DisplayMode.hpp"

#include <config.pb.h>

typedef struct _BackendItem {
    char text[32];
    CommunicationBackendId backendId;
    //I don't feel like implementing lambdas here rn
    bool retry;
    bool screenOff;
} BackendItem;

const BackendItem backendOptions[] = {
    {
        .text = "Retry",
        .backendId = COMMS_BACKEND_UNSPECIFIED,
        .retry = true,
        .screenOff = false,
    }, 
    {
        .text = "Screen off",
        .backendId = COMMS_BACKEND_UNSPECIFIED,
        .retry = false,
        .screenOff = true,
    },
};

class OopsieMenu : public DisplayMode {
  public:
    OopsieMenu(Config &config, CommunicationBackend **backends, size_t backends_count);
    DisplayModeId GetId();
    void HandleControls(
        IntegratedDisplay *instance,
        const DisplayControls &controls,
        Button button
    );
    void UpdateDisplay(IntegratedDisplay *instance, Adafruit_GFX &display);

  protected:
    Config &_config;
    CommunicationBackend **_backends;
    size_t _backends_count;
    size_t _highlighted_item = 0;
    size_t _backend_options_count = count_of(backendOptions);
    const BackendItem *_backend_options = backendOptions;
};

#endif