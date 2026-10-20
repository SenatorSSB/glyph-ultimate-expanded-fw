#include <stdint.h>
#include <stddef.h>
#include "core/state.hpp"
// Concrete ABI witness: owned immutable bytes plus validated nonsemantic offsets.
struct NativePreparedView {
 const uint8_t *body;
 uint32_t generation;
 uint16_t body_length;
 uint16_t condition_token_offsets[96];
 uint8_t all_counts[96],any_counts[96],none_counts[96];
 uint16_t table_offset,source_offset,rule_offset,binding_offset,effect_offset,mask_offset;
 uint16_t mode_gate,ls_digital_gate,rs_digital_gate,dpad_gate;
 uint8_t condition_count,early_condition_count,source_count,rule_count,binding_count,effect_count;
 uint8_t default_table,ls_source,rs_source,dpad_flags;
 uint16_t engine_abi;
 uint8_t body_digest[32];
 bool valid;
};
struct NativeOwnedProgram { uint8_t body[3336];NativePreparedView view; };
struct NativeCandidateWorkspace { NativeOwnedProgram program;uint32_t error_offset;uint8_t error_code; };
struct NativeFrameState {
 const NativePreparedView *program;
 uint32_t generation;
 bool roles[96];
 bool cardinal_activations[8];
 int8_t x,y,cx,cy;
 uint32_t buttons;
 uint16_t table_priority,ls_priority,rs_priority,left_trigger_priority,right_trigger_priority;
 uint8_t selected_table;
 bool ls_route_bypass;
};
struct ResolvedInputContext {const InputState &original,&remapped,&post;};
struct NativeValidationLocals {
 uint32_t defined_roles[3],seen_sources;
 uint32_t table_priorities[8],ls_priorities[8],rs_priorities[8],left_trigger_priorities[8],right_trigger_priorities[8];
 uint16_t offset,tokens_used;
};
char native_view_bytes[sizeof(NativePreparedView)];
char native_owned_bytes[sizeof(NativeOwnedProgram)];
char native_candidate_bytes[sizeof(NativeCandidateWorkspace)];
char native_active_plus_candidate_bytes[sizeof(NativeOwnedProgram)+sizeof(NativeCandidateWorkspace)];
char native_frame_bytes[sizeof(NativeFrameState)];
char native_context_bytes[sizeof(ResolvedInputContext)];
char native_input_copy_bytes[2*sizeof(InputState)];
char native_validation_locals_bytes[sizeof(NativeValidationLocals)];
static_assert(sizeof(NativePreparedView)<=560,"metadata cap");
static_assert(sizeof(NativeOwnedProgram)+sizeof(NativeCandidateWorkspace)<=7800,"workspace cap");
static_assert(sizeof(NativeFrameState)<=144,"frame cap");
static_assert(sizeof(NativeValidationLocals)<=256,"validation-local cap");
