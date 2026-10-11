#pragma once

#include <cstddef>
#include <cstdint>

// Persisted Ultimate-profile shape. RuntimeTableId remains the source of the
// actual table identifiers; these values bound the persisted representation.
constexpr uint8_t kUltimateProfileSchemaVersion = 1;
constexpr size_t kUltimateProfileTableCount = 28;
constexpr size_t kUltimateProfileCoordinateCount = 9;
