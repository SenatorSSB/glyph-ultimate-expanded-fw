#include "core/config_validation.hpp"
#include "modes/UltimateProfileConfig.hpp"

#include <cstdint>
#include <cstdio>
#include <cstring>

enum class RuntimeTableId : uint8_t {};
struct StickPoint { uint8_t x; uint8_t y; };
struct RuntimeConfigView {};
constexpr uint8_t ANALOG_STICK_NEUTRAL = 128;
constexpr size_t kRuntimeTableCount = kUltimateProfileTableCount;
constexpr size_t kRuntimeTableCenterIndex = 4;
const RuntimeConfigView &ResolveActiveRuntimeConfig();
StickPoint LookupRuntimeStickPoint(const RuntimeConfigView &, RuntimeTableId, size_t);
const RuntimeConfigView &ResolveActiveRuntimeConfig() {
    static const RuntimeConfigView view{};
    return view;
}
StickPoint LookupRuntimeStickPoint(const RuntimeConfigView &, RuntimeTableId, size_t) {
    return {ANALOG_STICK_NEUTRAL, ANALOG_STICK_NEUTRAL};
}

// The runner substitutes the production LookupConfiguredStickPoint definition here.
// ULTIMATE_LOOKUP_DEFINITION

namespace {
int failures = 0;

void check(bool condition, const char *name) {
    if (!condition) {
        std::fprintf(stderr, "FAIL: %s\n", name);
        ++failures;
    }
}

Config make_config() {
    Config config{};
    config.communication_backend_configs_count = 1;
    config.default_usb_backend_config = 1;
    config.ultimate_profiles_count = 2;
    for (size_t p = 0; p < 2; ++p) {
        UltimateProfile &profile = config.ultimate_profiles[p];
        profile.schema_version = kUltimateProfileSchemaVersion;
        profile.tables_count = kUltimateProfileTableCount;
        for (size_t t = 0; t < kUltimateProfileTableCount; ++t) {
            UltimateProfileTable &table = profile.tables[t];
            const size_t table_id = kUltimateProfileTableCount - 1 - t;
            table.table_id = static_cast<uint8_t>(table_id);
            table.coordinates_count = kUltimateProfileCoordinateCount;
            for (size_t d = 0; d < kUltimateProfileCoordinateCount; ++d) {
                table.coordinates[d].x = static_cast<uint8_t>(20 + p * 80 + table_id * 2 + d);
                table.coordinates[d].y = static_cast<uint8_t>(21 + p * 80 + table_id * 2 + d);
            }
        }
    }
    config.game_mode_configs_count = 2;
    for (size_t i = 0; i < 2; ++i) {
        config.game_mode_configs[i].mode_id = MODE_ULTIMATE;
        config.game_mode_configs[i].ultimate_profile_config = static_cast<uint8_t>(i + 1);
        std::strcpy(config.game_mode_configs[i].name, "duplicate");
    }
    return config;
}

bool valid(const Config &config) {
    ConfigValidationError error{};
    return validate_config_semantics(config, error);
}
}

int main() {
    Config config = make_config();
    check(valid(config), "two complete profiles with duplicate names validate");
    for (size_t p = 0; p < 2; ++p) {
        const UltimateProfile *profile = &config.ultimate_profiles[p];
        for (size_t table = 0; table < kUltimateProfileTableCount; ++table) {
            for (size_t direction = 0; direction < kUltimateProfileCoordinateCount; ++direction) {
                const StickPoint point = LookupConfiguredStickPoint(
                    profile, static_cast<RuntimeTableId>(table), direction);
                const UltimateProfileTable *expected_table = nullptr;
                for (size_t slot = 0; slot < profile->tables_count; ++slot) {
                    if (profile->tables[slot].table_id == table) {
                        expected_table = &profile->tables[slot];
                        break;
                    }
                }
                check(expected_table != nullptr, "test fixture contains each explicit table ID");
                const Coords expected = expected_table->coordinates[direction];
                check(point.x == expected.x && point.y == expected.y,
                      "lookup resolves explicit table ID and all nine directions");
            }
        }
    }
    const StickPoint isolated = LookupConfiguredStickPoint(
        &config.ultimate_profiles[1], static_cast<RuntimeTableId>(7), 3);
    check(isolated.x == config.ultimate_profiles[1].tables[kUltimateProfileTableCount - 1 - 7].coordinates[3].x &&
          isolated.x != config.ultimate_profiles[0].tables[kUltimateProfileTableCount - 1 - 7].coordinates[3].x,
          "selected profile lookup remains isolated");
    const uint8_t selected_profile = config.game_mode_configs[1].ultimate_profile_config;
    check(selected_profile == 2 &&
          LookupConfiguredStickPoint(&config.ultimate_profiles[selected_profile - 1],
              static_cast<RuntimeTableId>(0), 0).x ==
                  config.ultimate_profiles[1].tables[kUltimateProfileTableCount - 1].coordinates[0].x,
          "one-based profile reference selects second profile");

    Config invalid = config;
    invalid.ultimate_profiles[0].schema_version = 2;
    check(!valid(invalid), "unsupported profile schema version rejected");
    invalid = config;
    invalid.ultimate_profiles[0].tables_count = 27;
    check(!valid(invalid), "missing table rejected");
    invalid = config;
    invalid.ultimate_profiles[0].tables[1].table_id = invalid.ultimate_profiles[0].tables[0].table_id;
    check(!valid(invalid), "duplicate table ID rejected");
    invalid = config;
    invalid.ultimate_profiles[0].tables[0].coordinates_count = 8;
    check(!valid(invalid), "missing direction rejected");
    invalid = config;
    invalid.game_mode_configs[1].ultimate_profile_config = 3;
    check(!valid(invalid), "out-of-range one-based profile reference rejected");
    invalid = config;
    invalid.game_mode_configs[1].ultimate_profile_config = 1;
    invalid.game_mode_configs[1].mode_id = MODE_MELEE;
    check(!valid(invalid), "profile reference on non-Ultimate mode rejected");
    invalid = config;
    invalid.ultimate_profiles_count = 3;
    check(!validate_config_extents(invalid), "profile array extent overflow rejected");

    Config legacy{};
    legacy.communication_backend_configs_count = 1;
    legacy.default_usb_backend_config = 1;
    legacy.game_mode_configs_count = 1;
    legacy.game_mode_configs[0].mode_id = MODE_ULTIMATE;
    check(valid(legacy), "legacy Ultimate mode with absent optional profile reference remains valid");

    if (failures) return 1;
    std::puts("PASS: persisted profile validation, references, and 504 coordinate lookups");
    return 0;
}
