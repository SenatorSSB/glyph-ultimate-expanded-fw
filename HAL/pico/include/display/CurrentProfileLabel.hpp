#pragma once

#include "core/InputMode.hpp"
#include "display/PlateLabel.hpp"

// Presentation only. Glyph normal display/core1 calls after the boot mutex
// handoff; gameplay directory/activation state is immutable until reboot.
// Configurator (the live writer) must be excluded before reading store state.
const char *current_profile_label(const InputMode *mode, CommunicationBackendId backend);
