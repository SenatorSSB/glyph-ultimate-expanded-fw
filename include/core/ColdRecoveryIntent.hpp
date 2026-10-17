#pragma once
#include <cstdint>

namespace ColdRecoveryIntent {
// CRT2: distinct from MDST mode destination and scratch3 diagnostic namespaces.
constexpr uint32_t kMagic = 0x43525432u;
constexpr uint32_t kTimerReason = 1u;

inline bool Arm(volatile uint32_t *scratch) {
    if (scratch[0] != 0 || scratch[1] != 0 || scratch[2] != 0) return false;
    scratch[2] = kMagic;
    return scratch[2] == kMagic;
}

inline bool Consume(volatile uint32_t *scratch, uint32_t reason) {
    if (scratch[2] != kMagic) return false;
    // Clear our tag even if malformed/stale. Unknown/mode tags are untouched.
    scratch[2] = 0;
    return scratch[2] == 0 && reason == kTimerReason &&
        scratch[0] == 0 && scratch[1] == 0;
}
}
