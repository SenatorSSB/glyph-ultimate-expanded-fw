// Phase 7A D2B retention anchor.
//
// This translation unit references the compiled payload byte array directly so the
// linker keeps the payload in the firmware image. The symbol is intentionally
// otherwise unused and no parser, resolver, or runtime path consumes it.

#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"

static_assert(
    UltimateRuntimeConfigCompiledPayload::kPhase7ACompiledPayloadSize == 530,
    "D2B retained payload anchor must retain the full payload byte sequence"
);

extern "C" {
__asm__(
    ".section .rodata.phase7a_d2b_payload,\"aR\",%progbits\n"
    ".balign 4\n"
    ".global kPhase7AD2BRetainedPayloadAnchor\n"
    ".type kPhase7AD2BRetainedPayloadAnchor, %object\n"
    "kPhase7AD2BRetainedPayloadAnchor:\n"
    ".incbin \"docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin\"\n"
    ".size kPhase7AD2BRetainedPayloadAnchor, 530\n"
    ".previous\n"
);
}
