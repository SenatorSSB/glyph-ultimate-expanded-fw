#pragma once

#include <cstddef>
#include <cstdint>

// Persisted Ultimate-profile shape. RuntimeTableId remains the source of the
// actual table identifiers; these values bound the persisted representation.
constexpr uint8_t kUltimateProfileSchemaVersionV1 = 1;
constexpr uint8_t kUltimateProfileSchemaVersionV2 = 2;
constexpr uint8_t kUltimateProfileSchemaVersionV3 = 3;
// Kept as the legacy version for Stage-A callers and source compatibility.
constexpr uint8_t kUltimateProfileSchemaVersion = kUltimateProfileSchemaVersionV1;
constexpr size_t kUltimateProfileTableCount = 28;
constexpr size_t kUltimateProfileCoordinateCount = 9;
// These capacities fit the complete current selector correspondence while
// retaining Nanopb's 16-bit message descriptor support; 32/32 exceeds it.
constexpr size_t kUltimateProfileRoleCount = 22;
constexpr size_t kUltimateProfileRoutingSlotCount = 32;
constexpr size_t kUltimateProfileRequiredRoutingSlotCount = 15;
constexpr size_t kUltimateProfileTableRuleCount = 19;
constexpr uint8_t kUltimateProfileButtonTokenMin = 1;
constexpr uint8_t kUltimateProfileButtonTokenMax = 60;
constexpr uint8_t kUltimateProfileRoleTokenMin = 65;
constexpr uint8_t kUltimateProfileRoleTokenMax = 96;
