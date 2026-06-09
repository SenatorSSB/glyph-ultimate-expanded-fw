// Phase 7A D2B retention anchor.
//
// This translation unit references the compiled payload byte array directly so the
// linker keeps the payload in the firmware image. The symbol is intentionally
// otherwise unused and no parser, resolver, or runtime path consumes it.

#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"

namespace {

extern "C" __attribute__((used)) const uint8_t* const kPhase7AD2BRetainedPayloadAnchor =
    UltimateRuntimeConfigCompiledPayload::kPhase7ACompiledPayload;

}  // namespace
