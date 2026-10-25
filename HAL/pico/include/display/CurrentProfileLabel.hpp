#pragma once

#include "core/InputMode.hpp"

// Presentation only. Glyph normal display/core1 calls after the boot mutex
// handoff; gameplay directory/activation state is immutable until reboot.
// Configurator (the live writer) must be excluded before reading store state.
const char *current_profile_label(const InputMode *mode, CommunicationBackendId backend);

constexpr const char *dashboard_plate_label(LayoutPlate plate) {
    switch (plate) {
        case LAYOUT_PLATE_UNSPECIFIED: return "";
        case LAYOUT_PLATE_EVERYTHING: return "Full";
        case LAYOUT_PLATE_FGC: return "FGC";
        case LAYOUT_PLATE_SPLIT_FGC: return "Split FGC";
        case LAYOUT_PLATE_PLATFORM_FIGHTER: return "Plat Fighter";
    }
    return "Unknown Plate";
}
