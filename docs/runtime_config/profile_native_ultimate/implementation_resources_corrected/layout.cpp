#include "modes/UltimateNativeEvaluator.hpp"
#include "core/ProfileStore.hpp"
#define SIZE(name,type) char name[sizeof(type)]
SIZE(native_view_bytes,ultimate_native::PreparedView);
SIZE(native_owned_bytes,ultimate_native::OwnedProgram);
SIZE(native_candidate_bytes,ultimate_native::CandidateWorkspace);
char native_active_plus_candidate_bytes[sizeof(ultimate_native::OwnedProgram)+sizeof(ultimate_native::CandidateWorkspace)];
SIZE(native_frame_bytes,ultimate_native::FrameState);
SIZE(context_bytes,ResolvedInputContext);
char preprocessing_copy_bytes[2*sizeof(InputState)];
SIZE(profile_store_bytes,ProfileStore);
SIZE(config_bytes,Config);SIZE(mode_bytes,GameModeConfig);SIZE(profile_bytes,UltimateProfile);
SIZE(request_bytes,ProfileStoreRequest);SIZE(response_bytes,ProfileStoreResponse);
static_assert(sizeof(ultimate_native::PreparedView)<=560,"view cap");
static_assert(sizeof(ultimate_native::OwnedProgram)+sizeof(ultimate_native::CandidateWorkspace)<=7800,"active+candidate cap");
static_assert(sizeof(ultimate_native::FrameState)<=144,"frame cap");
