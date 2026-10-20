#pragma once
#include "modes/UltimateNativeProfile.hpp"
#include "core/ControllerMode.hpp"

namespace ultimate_native {
// Fixed finite frame state. Canonical immutable program bytes are the semantic
// input; no parser, allocation, filesystem or publication occurs in Evaluate.
struct FrameState {
    const PreparedView *program;
    uint32_t generation;
    bool roles[96] = {};
    bool cardinal_activations[8] = {};
    int8_t x=0,y=0,cx=0,cy=0;
    uint32_t buttons=0;
    uint16_t table_priority=256,ls_priority=256,rs_priority=256,
             left_trigger_priority=256,right_trigger_priority=256;
    uint8_t selected_table=0;
    bool ls_route_bypass=false;
};
void Neutral(OutputState &);
bool Evaluate(const PreparedView &, const ResolvedInputContext &, ControllerMode &, OutputState &);
} // namespace ultimate_native
