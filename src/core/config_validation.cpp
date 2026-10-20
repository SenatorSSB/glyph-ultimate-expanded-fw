#include "core/config_validation.hpp"
#include "core/config_button_validation.hpp"
#include "modes/UltimateProfileConfig.hpp"
#include "modes/UltimateProfileEvaluator.hpp"
#include "core/ProfileStore.hpp"
#include "modes/UltimateNativeProfile.hpp"

#include <cstdio>
#include <cstring>
#include <type_traits>

namespace {

template <typename T, size_t N, typename Count>
bool fits(const T (&)[N], Count count) {
    return static_cast<size_t>(count) <= N;
}

template <typename... Args>
bool reference_error(ConfigValidationError &error, const char *format, Args... args) {
    const int length = std::snprintf(error.message, sizeof(error.message), format, args...);
    error.length = length > 0 && static_cast<size_t>(length) < sizeof(error.message)
        ? static_cast<size_t>(length) : sizeof(error.message) - 1;
    return false;
}

bool is_button_token(uint32_t token) {
    return token >= kUltimateProfileButtonTokenMin && token <= kUltimateProfileButtonTokenMax;
}

bool is_role_token(uint32_t token) {
    return token >= kUltimateProfileRoleTokenMin && token <= kUltimateProfileRoleTokenMax;
}

bool is_required_routing_slot(uint32_t token) {
    switch (token) {
        case BTN_LF4:
        case BTN_RF2:
        case BTN_RF3:
        case BTN_RF4:
        case BTN_RF8:
        case BTN_RF9:
        case BTN_LT2:
        case BTN_LT3:
        case BTN_LT4:
        case BTN_LT5:
        case BTN_RT1:
        case BTN_RT2:
        case BTN_RT3:
        case BTN_RT4:
        case BTN_RT5:
            return true;
        default:
            return false;
    }
}

bool validate_profile_condition(
    const UltimateProfileCondition &condition,
    const bool defined_roles[32],
    const bool routed_buttons[61],
    uint8_t maximum_role_id,
    ConfigValidationError &error,
    uint8_t profile_id
) {
    const uint8_t *lists[] = {condition.all_tokens, condition.any_tokens, condition.none_tokens};
    const size_t counts[] = {
        condition.all_tokens_count,
        condition.any_tokens_count,
        condition.none_tokens_count,
    };
    bool seen_tokens[97] = {};
    for (size_t list = 0; list < 3; ++list) {
        for (size_t index = 0; index < counts[list]; ++index) {
            const uint32_t token = lists[list][index];
            if ((!is_button_token(token) && !is_role_token(token)) || seen_tokens[token] ||
                (is_button_token(token) && !routed_buttons[token])) {
                return reference_error(error, "Ultimate profile %d has an invalid condition token", profile_id);
            }
            seen_tokens[token] = true;
            if (is_role_token(token)) {
                const uint8_t role_id = static_cast<uint8_t>(token - 64);
                if (role_id > maximum_role_id || !defined_roles[role_id - 1]) {
                    return reference_error(error, "Ultimate profile %d has an unresolved role token", profile_id);
                }
            }
        }
    }
    return true;
}

bool validate_ultimate_profile_extents(const UltimateProfile &profile) {
    if (!fits(profile.tables, profile.tables_count) ||
        !fits(profile.roles, profile.roles_count) ||
        !fits(profile.routing_slots, profile.routing_slots_count) ||
        !fits(profile.table_rules, profile.table_rules_count) ||
        !fits(profile.output_program.effects, profile.output_program.effects_count)) return false;
    for (size_t i = 0; i < profile.tables_count; ++i)
        if (!fits(profile.tables[i].coordinates, profile.tables[i].coordinates_count)) return false;
    for (size_t i = 0; i < profile.roles_count; ++i) {
        const auto &role = profile.roles[i];
        if (!role.has_condition || !fits(role.condition.all_tokens, role.condition.all_tokens_count) ||
            !fits(role.condition.any_tokens, role.condition.any_tokens_count) ||
            !fits(role.condition.none_tokens, role.condition.none_tokens_count)) return false;
    }
    for (size_t i = 0; i < profile.table_rules_count; ++i) {
        const auto &rule = profile.table_rules[i];
        if (!rule.has_condition || !fits(rule.condition.all_tokens, rule.condition.all_tokens_count) ||
            !fits(rule.condition.any_tokens, rule.condition.any_tokens_count) ||
            !fits(rule.condition.none_tokens, rule.condition.none_tokens_count)) return false;
    }
    return true;
}

bool validate_ultimate_profile_semantics_impl(const UltimateProfile &profile,
                                              ConfigValidationError &error,
                                              uint8_t profile_id) {
    if (profile.schema_version == ultimate_native::kSchema)
        return ultimate_native::ValidProfile(profile) || reference_error(error, "Ultimate profile %d has an invalid native program", profile_id);
    if (profile.native_payload.funcs.encode || profile.native_payload.arg)
        return reference_error(error, "Ultimate profile %d contains native payload in legacy schema", profile_id);
    if ((profile.schema_version != kUltimateProfileSchemaVersionV1 &&
         profile.schema_version != kUltimateProfileSchemaVersionV2 &&
         profile.schema_version != kUltimateProfileSchemaVersionV3) ||
        profile.tables_count != kUltimateProfileTableCount)
        return reference_error(error, "Ultimate profile %d has an unsupported shape", profile_id);
    if (profile.schema_version == kUltimateProfileSchemaVersionV1 &&
        (profile.roles_count != 0 || profile.routing_slots_count != 0 ||
         profile.default_table_id != 0 || profile.table_rules_count != 0 || profile.has_output_program))
        return reference_error(error, "Ultimate profile %d adds fields to schema version 1", profile_id);
    if (profile.schema_version == kUltimateProfileSchemaVersionV2 && profile.has_output_program)
        return reference_error(error, "Ultimate profile %d adds an output program to schema version 2", profile_id);

    bool seen_table_ids[kUltimateProfileTableCount] = {};
    for (size_t i = 0; i < profile.tables_count; ++i) {
        const UltimateProfileTable &table = profile.tables[i];
        if (table.table_id >= kUltimateProfileTableCount ||
            table.coordinates_count != kUltimateProfileCoordinateCount || seen_table_ids[table.table_id])
            return reference_error(error, "Ultimate profile %d has an invalid table", profile_id);
        seen_table_ids[table.table_id] = true;
    }
    for (size_t table_id = 0; table_id < kUltimateProfileTableCount; ++table_id)
        if (!seen_table_ids[table_id]) return reference_error(error, "Ultimate profile %d is missing a table", profile_id);
    if (profile.schema_version == kUltimateProfileSchemaVersionV1) return true;
    if (profile.roles_count == 0 || profile.routing_slots_count < kUltimateProfileRequiredRoutingSlotCount ||
        profile.table_rules_count == 0 || profile.default_table_id >= kUltimateProfileTableCount)
        return reference_error(error, "Ultimate profile %d has an incomplete version 2 shape", profile_id);

    bool defined_roles[32] = {};
    for (size_t i = 0; i < profile.roles_count; ++i) {
        const UltimateProfileRole &role = profile.roles[i];
        if (role.role_id == 0 || role.role_id > 32 || defined_roles[role.role_id - 1])
            return reference_error(error, "Ultimate profile %d has an invalid role", profile_id);
        defined_roles[role.role_id - 1] = true;
    }
    bool seen_routing_slots[kUltimateProfileButtonTokenMax + 1] = {};
    bool seen_routing_inputs[kUltimateProfileButtonTokenMax + 1] = {};
    for (size_t i = 0; i < profile.routing_slots_count; ++i) {
        const UltimateProfileRoutingSlot &slot = profile.routing_slots[i];
        if (!is_button_token(slot.slot_id) || !is_button_token(slot.input_token) ||
            seen_routing_slots[slot.slot_id] || seen_routing_inputs[slot.input_token])
            return reference_error(error, "Ultimate profile %d has an invalid routing slot", profile_id);
        seen_routing_slots[slot.slot_id] = true;
        seen_routing_inputs[slot.input_token] = true;
    }
    for (uint32_t token = kUltimateProfileButtonTokenMin; token <= kUltimateProfileButtonTokenMax; ++token)
        if (is_required_routing_slot(token) && !seen_routing_slots[token])
            return reference_error(error, "Ultimate profile %d is missing a required routing slot", profile_id);
    for (size_t i = 0; i < profile.roles_count; ++i)
        if (!validate_profile_condition(profile.roles[i].condition, defined_roles, seen_routing_slots,
                static_cast<uint8_t>(profile.roles[i].role_id - 1), error, profile_id)) return false;

    bool seen_priorities[256] = {};
    for (size_t i = 0; i < profile.table_rules_count; ++i) {
        const UltimateProfileTableRule &rule = profile.table_rules[i];
        if (rule.priority == 0 || rule.table_id >= kUltimateProfileTableCount || seen_priorities[rule.priority])
            return reference_error(error, "Ultimate profile %d has an invalid table priority", profile_id);
        seen_priorities[rule.priority] = true;
        if (!validate_profile_condition(rule.condition, defined_roles, seen_routing_slots, 32, error, profile_id)) return false;
    }
    if (profile.schema_version != kUltimateProfileSchemaVersionV3) return true;
    if (!profile.has_output_program || !profile.output_program.enabled ||
        profile.routing_slots_count != kUltimateProfileRoutingSlotCount ||
        profile.output_program.effects_count != UltimateProfileEvaluator::kOutputEffectCount)
        return reference_error(error, "Ultimate profile %d has an incomplete version 3 output program", profile_id);
    const uint8_t required[] = {1,2,3,4,5,17,18,19,20,21,22,23,24,25,26,29,32,33,34,35,36,37,38,41,42,43,44,45,52,53,54,55};
    for (uint8_t slot : required) if (!seen_routing_slots[slot])
        return reference_error(error, "Ultimate profile %d is missing an output input slot", profile_id);
    bool keys[UltimateProfileEvaluator::kOutputEffectCount] = {};
    for (size_t i = 0; i < profile.output_program.effects_count; ++i) {
        const UltimateProfileOutputEffect &effect = profile.output_program.effects[i];
        const int key = UltimateProfileEvaluator::EffectKey(effect);
        if (key < 0 || keys[key] || !UltimateProfileEvaluator::ValidEffectShape(effect))
            return reference_error(error, "Ultimate profile %d has an invalid output effect", profile_id);
        keys[key] = true;
        const uint32_t token = effect.gate_token;
        if ((token == 0 && effect.gate_inverted) ||
            (token != 0 && !((is_button_token(token) && seen_routing_slots[token]) ||
                (is_role_token(token) && defined_roles[token - 65]))))
            return reference_error(error, "Ultimate profile %d has an invalid output gate", profile_id);
    }
    for (bool present : keys) if (!present)
        return reference_error(error, "Ultimate profile %d is missing an output phase", profile_id);
    return true;
}

}  // namespace

bool validate_config_extents(const Config &config) {
    if (!fits(config.game_mode_configs, config.game_mode_configs_count) ||
        !fits(config.communication_backend_configs, config.communication_backend_configs_count) ||
        !fits(config.custom_modes, config.custom_modes_count) ||
        !fits(config.keyboard_modes, config.keyboard_modes_count) ||
        !fits(config.rgb_configs, config.rgb_configs_count) ||
        !fits(config.ultimate_profiles, config.ultimate_profiles_count)) {
        return false;
    }
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (!fits(mode.socd_pairs, mode.socd_pairs_count) ||
            !fits(mode.button_remapping, mode.button_remapping_count) ||
            !fits(mode.activation_binding, mode.activation_binding_count) ||
            !fits(mode.applicable_backends, mode.applicable_backends_count) ||
            !fits(mode.menu_button_icon, mode.menu_button_icon_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        const CommunicationBackendConfig &backend = config.communication_backend_configs[i];
        if (!fits(backend.activation_binding, backend.activation_binding_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.custom_modes_count; ++i) {
        const CustomModeConfig &mode = config.custom_modes[i];
        if (!fits(mode.digital_button_mappings, mode.digital_button_mappings_count) ||
            !fits(mode.stick_direction_mappings, mode.stick_direction_mappings_count) ||
            !fits(mode.analog_trigger_mappings, mode.analog_trigger_mappings_count) ||
            !fits(mode.modifiers, mode.modifiers_count) ||
            !fits(mode.button_combo_mappings, mode.button_combo_mappings_count)) {
            return false;
        }
        for (size_t j = 0; j < mode.modifiers_count; ++j) {
            if (!fits(mode.modifiers[j].buttons, mode.modifiers[j].buttons_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < mode.button_combo_mappings_count; ++j) {
            if (!fits(mode.button_combo_mappings[j].buttons,
                      mode.button_combo_mappings[j].buttons_count)) {
                return false;
            }
        }
    }
    for (size_t i = 0; i < config.keyboard_modes_count; ++i) {
        if (!fits(config.keyboard_modes[i].buttons_to_keycodes,
                  config.keyboard_modes[i].buttons_to_keycodes_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.rgb_configs_count; ++i) {
        if (!fits(config.rgb_configs[i].button_colors, config.rgb_configs[i].button_colors_count)) {
            return false;
        }
    }
    for (size_t i = 0; i < config.ultimate_profiles_count; ++i) {
        const UltimateProfile &profile = config.ultimate_profiles[i];
        if (!fits(profile.tables, profile.tables_count) ||
            !fits(profile.roles, profile.roles_count) ||
            !fits(profile.routing_slots, profile.routing_slots_count) ||
            !fits(profile.table_rules, profile.table_rules_count) ||
            !fits(profile.output_program.effects, profile.output_program.effects_count)) {
            return false;
        }
        for (size_t j = 0; j < profile.output_program.effects_count; ++j) {
            const auto &effect = profile.output_program.effects[j];
            if (!fits(effect.coordinates, effect.coordinates_count)) return false;
        }
        for (size_t j = 0; j < profile.tables_count; ++j) {
            if (!fits(profile.tables[j].coordinates, profile.tables[j].coordinates_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < profile.roles_count; ++j) {
            const UltimateProfileRole &role = profile.roles[j];
            if (!role.has_condition ||
                !fits(role.condition.all_tokens, role.condition.all_tokens_count) ||
                !fits(role.condition.any_tokens, role.condition.any_tokens_count) ||
                !fits(role.condition.none_tokens, role.condition.none_tokens_count)) {
                return false;
            }
        }
        for (size_t j = 0; j < profile.table_rules_count; ++j) {
            const UltimateProfileTableRule &rule = profile.table_rules[j];
            if (!rule.has_condition ||
                !fits(rule.condition.all_tokens, rule.condition.all_tokens_count) ||
                !fits(rule.condition.any_tokens, rule.condition.any_tokens_count) ||
                !fits(rule.condition.none_tokens, rule.condition.none_tokens_count)) {
                return false;
            }
        }
    }
    return true;
}

bool validate_ultimate_profile_semantics(const UltimateProfile &profile, ConfigValidationError &error) {
    error = ConfigValidationError{};
    if (!validate_ultimate_profile_extents(profile)) {
        static const char message[] = "Config contains an invalid button binding";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }
    return validate_ultimate_profile_semantics_impl(profile, error, 1);
}

bool validate_config_semantics(const Config &config, ConfigValidationError &error) {
    error = ConfigValidationError{};
    // Complete bounds precede both semantic callbacks and every nested walk.
    // Keep the existing binding error and its wire length for structural failures.
    if (!validate_config_extents(config) || !validate_config_button_bindings(config)) {
        static const char message[] = "Config contains an invalid button binding";
        std::memcpy(error.message, message, sizeof(message));
        error.length = sizeof(message);
        return false;
    }

    if (!is_valid_usb_default_index(config)) {
        return reference_error(error,
            "Default USB backend index is %d but only %d backend configs are defined",
            static_cast<uint8_t>(config.default_usb_backend_config),
            static_cast<uint8_t>(config.communication_backend_configs_count));
    }

    if (config.default_backend_config > config.communication_backend_configs_count) {
        return reference_error(error,
            "Default backend ID is %d but only %d backend configs are defined",
            static_cast<uint8_t>(config.default_backend_config),
            static_cast<uint8_t>(config.communication_backend_configs_count));
    }
    for (size_t i = 0; i < config.communication_backend_configs_count; ++i) {
        const uint8_t default_mode_id = config.communication_backend_configs[i].default_mode_config;
        if (default_mode_id > config.game_mode_configs_count) {
            return reference_error(error,
                "Default mode ID is %d for backend %d but only %d modes are defined",
                default_mode_id, static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.game_mode_configs_count));
        }
    }

    static_assert(std::is_same<decltype(GameModeConfig::custom_mode_config), uint32_t>::value,
                  "custom reference must retain its authoritative decoded width");
    if (config.ultimate_profile_store_format > ProfileStore::kCompactConfigFormat) {
        return reference_error(error, "%s", "Ultimate profile store format is unsupported");
    }
    if (config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat &&
        (config.ultimate_profile_store_incarnation == 0 || config.ultimate_profiles_count != 0)) {
        return reference_error(error, "%s", "Compact Ultimate profile store config is invalid");
    }
    for (size_t i = 0; i < config.ultimate_profiles_count; ++i) {
        if (config.ultimate_profiles[i].schema_version == ultimate_native::kSchema || config.ultimate_profiles[i].native_payload.funcs.encode || config.ultimate_profiles[i].native_payload.arg)
            return reference_error(error, "%s", "Embedded native profile is forbidden");
        if (!validate_ultimate_profile_semantics_impl(config.ultimate_profiles[i], error,
                static_cast<uint8_t>(i) + 1)) return false;
    }
    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        const GameModeConfig &mode = config.game_mode_configs[i];
        if (mode.ultimate_profile_engine > 1 || (mode.ultimate_profile_engine &&
            (mode.mode_id != MODE_ULTIMATE || !mode.ultimate_profile_id || config.ultimate_profile_store_format != ProfileStore::kCompactConfigFormat)))
            return reference_error(error, "%s", "Native engine reference is invalid");
        const uint8_t keyboard_mode_id = mode.keyboard_mode_config;
        const uint32_t custom_mode_id = mode.custom_mode_config;
        const uint8_t ultimate_profile_id = mode.ultimate_profile_config;
        if (keyboard_mode_id > 0 && mode.mode_id != MODE_KEYBOARD) {
            return reference_error(error,
                "keyboard_mode_id is set for game mode %d but mode_id is not MODE_KEYBOARD",
                static_cast<uint8_t>(i) + 1);
        }
        if (custom_mode_id > 0 && mode.mode_id != MODE_CUSTOM) {
            return reference_error(error,
                "custom_mode_id is set for game mode %d but mode_id is not MODE_CUSTOM",
                static_cast<uint8_t>(i) + 1);
        }
        if (ultimate_profile_id > 0 && mode.mode_id != MODE_ULTIMATE) {
            return reference_error(error,
                "ultimate_profile_id is set for game mode %d but mode_id is not MODE_ULTIMATE",
                static_cast<uint8_t>(i) + 1);
        }
        if (mode.ultimate_profile_id > 0 && mode.mode_id != MODE_ULTIMATE) {
            return reference_error(error,
                "stable Ultimate profile ID is set for game mode %d but mode_id is not MODE_ULTIMATE",
                static_cast<uint8_t>(i) + 1);
        }
        if (config.ultimate_profile_store_format == 0 && mode.ultimate_profile_id != 0) {
            return reference_error(error, "%s", "Legacy Ultimate profile config contains a stable profile ID");
        }
        if (keyboard_mode_id > config.keyboard_modes_count) {
            return reference_error(error,
                "Keyboard mode ID %d is for game mode %d but only %d keyboard modes are defined",
                keyboard_mode_id, static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.keyboard_modes_count));
        }
        if (custom_mode_id > config.custom_modes_count) {
            return reference_error(error,
                "Custom mode ID %lu is for game mode config %d but only %d custom modes are defined",
                static_cast<unsigned long>(custom_mode_id), static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.custom_modes_count));
        }
        if (ultimate_profile_id > config.ultimate_profiles_count) {
            return reference_error(error,
                "Ultimate profile ID %d is for game mode %d but only %d Ultimate profiles are defined",
                ultimate_profile_id, static_cast<uint8_t>(i) + 1,
                static_cast<uint8_t>(config.ultimate_profiles_count));
        }
        if (config.ultimate_profile_store_format == ProfileStore::kCompactConfigFormat &&
            mode.mode_id == MODE_ULTIMATE && ultimate_profile_id != 0) {
            return reference_error(error, "%s", "Compact Ultimate profile config retains legacy index");
        }
    }
    return true;
}
