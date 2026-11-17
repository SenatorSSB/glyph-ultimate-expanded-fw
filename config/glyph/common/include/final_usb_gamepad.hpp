#pragma once

#include <config.pb.h>

// Classify protocols, not the physical USB-C connector. Configurator retains
// its early CDC attachment; retro-console signalling must not reconnect USB.
inline bool requires_final_usb_gamepad_reenumeration(CommunicationBackendId backend) {
    switch (backend) {
        case COMMS_BACKEND_XINPUT:
        case COMMS_BACKEND_DINPUT:
        case COMMS_BACKEND_NINTENDO_SWITCH:
            return true;
        default:
            return false;
    }
}
