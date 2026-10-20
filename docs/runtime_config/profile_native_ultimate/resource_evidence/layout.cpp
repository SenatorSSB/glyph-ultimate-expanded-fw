#include <config.pb.h>
#include "core/ProfileStore.hpp"
#define P(T) extern "C" char layout_##T[sizeof(T)]; char layout_##T[sizeof(T)];
P(Config) P(GameModeConfig) P(UltimateProfile) P(UltimateProfileTable) P(UltimateProfileCondition) P(UltimateProfileRole) P(UltimateProfileRoutingSlot) P(UltimateProfileTableRule) P(UltimateProfileOutputProgram) P(UltimateProfileOutputEffect) P(ProfileStore) P(ProfileStoreRequest) P(ProfileStoreResponse)
