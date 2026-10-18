#pragma once

#include "modes/UltimateProfileConfig.hpp"
#include <config.pb.h>

#include <cstddef>
#include <cstdint>

// Finite persisted roles, routing, table choice and Stage-C effect lookup.
namespace UltimateProfileEvaluator {

constexpr size_t kOutputEffectCount = 12;

inline const UltimateProfileOutputEffect *FindEffect(
    const UltimateProfile *profile, UltimateProfileOutputPhase phase,
    UltimateProfileOutputTarget target
) {
    if (profile == nullptr || (profile->schema_version != kUltimateProfileSchemaVersionV3 &&
        profile->schema_version != kUltimateProfileSchemaVersionV4)) return nullptr;
    for (size_t i = 0; i < profile->output_program.effects_count; ++i) {
        const auto &effect = profile->output_program.effects[i];
        if (effect.phase == phase && effect.target == target) return &effect;
    }
    return nullptr;
}

// One slot per legal phase/target pair. Persisted storage order has no meaning.
inline int EffectKey(const UltimateProfileOutputEffect &e) {
    switch (e.phase) {
        case ULTIMATE_OUTPUT_PHASE_DIGITAL: return e.target == ULTIMATE_OUTPUT_TARGET_DIGITAL ? 0 : -1;
        case ULTIMATE_OUTPUT_PHASE_BASE_TABLE:
            return e.target == ULTIMATE_OUTPUT_TARGET_LEFT_STICK ? 1 :
                e.target == ULTIMATE_OUTPUT_TARGET_RIGHT_STICK ? 2 : -1;
        case ULTIMATE_OUTPUT_PHASE_DIRECTION_A: return e.target == ULTIMATE_OUTPUT_TARGET_LEFT_STICK ? 3 : -1;
        case ULTIMATE_OUTPUT_PHASE_RF6: return e.target == ULTIMATE_OUTPUT_TARGET_LEFT_STICK ? 4 : -1;
        case ULTIMATE_OUTPUT_PHASE_RF7: return e.target == ULTIMATE_OUTPUT_TARGET_LEFT_STICK ? 5 : -1;
        case ULTIMATE_OUTPUT_PHASE_RS_DIAGONAL: return e.target == ULTIMATE_OUTPUT_TARGET_RIGHT_STICK ? 6 : -1;
        case ULTIMATE_OUTPUT_PHASE_RF3_VERTICAL: return e.target == ULTIMATE_OUTPUT_TARGET_RIGHT_STICK ? 7 : -1;
        case ULTIMATE_OUTPUT_PHASE_NULL: return e.target == ULTIMATE_OUTPUT_TARGET_ANALOGUE_NULL ? 8 : -1;
        case ULTIMATE_OUTPUT_PHASE_TRIGGERS:
            return e.target == ULTIMATE_OUTPUT_TARGET_TRIGGER_L ? 9 :
                e.target == ULTIMATE_OUTPUT_TARGET_TRIGGER_R ? 10 : -1;
        case ULTIMATE_OUTPUT_PHASE_DPAD: return e.target == ULTIMATE_OUTPUT_TARGET_DPAD_LEFT_STICK ? 11 : -1;
        default: return -1;
    }
}

inline bool ValidEffectShape(const UltimateProfileOutputEffect &e) {
    const int key = EffectKey(e);
    if (key < 0) return false;
    const bool digital = key == 0, trigger = key == 9 || key == 10;
    if (digital || trigger) {
        return e.direction_source == 0 && e.coordinate_mode == 0 && e.table_id == 0 &&
            e.mode_table_id == 0 && e.fixed_x == 0 && e.fixed_y == 0 && e.coordinates_count == 0 &&
            (digital ? e.value == 0 && !e.suppress &&
                ((e.digital_set_mask | e.digital_clear_mask) & ~uint32_t{0xfff}) == 0 &&
                (e.digital_set_mask & e.digital_clear_mask) == 0 :
                e.digital_set_mask == 0 && e.digital_clear_mask == 0);
    }
    if (e.digital_set_mask != 0 || e.digital_clear_mask != 0 ||
        (key == 11 ? e.value > 7 : e.value != 0) ||
        e.direction_source < 1 || e.direction_source > 4 ||
        (key == 11 && e.direction_source != ULTIMATE_DIRECTION_SOURCE_CENTER)) return false;
    switch (e.coordinate_mode) {
        case ULTIMATE_COORDINATE_SELECTED_TABLE:
            if (key != 1) return false;
            return e.table_id == 0 && e.mode_table_id == 0 && e.coordinates_count == 0 && e.fixed_x == 0 && e.fixed_y == 0;
        case ULTIMATE_COORDINATE_TABLE:
            return e.table_id < kUltimateProfileTableCount && e.mode_table_id < kUltimateProfileTableCount &&
                e.coordinates_count == 0 && e.fixed_x == 0 && e.fixed_y == 0;
        case ULTIMATE_COORDINATE_FIXED:
            return e.table_id == 0 && e.mode_table_id == 0 && e.coordinates_count == 0;
        case ULTIMATE_COORDINATE_INLINE:
            return e.table_id == 0 && e.mode_table_id == 0 && e.coordinates_count == 18 && e.fixed_x == 0 && e.fixed_y == 0;
        default: return false;
    }
}

struct RoutingState {
    bool slots[kUltimateProfileButtonTokenMax + 1] = {};
};

inline bool IsPressedButtonToken(
    const UltimateProfile &profile,
    uint64_t input_buttons,
    uint32_t token
) {
    if (token < kUltimateProfileButtonTokenMin || token > kUltimateProfileButtonTokenMax) {
        return false;
    }
    for (size_t index = 0; index < profile.routing_slots_count; ++index) {
        const UltimateProfileRoutingSlot &slot = profile.routing_slots[index];
        if (slot.slot_id == token) {
            return (input_buttons & (uint64_t{1} << (slot.input_token - 1))) != 0;
        }
    }
    return false;
}

inline bool EvaluateCondition(
    const UltimateProfile &profile,
    const UltimateProfileCondition &condition,
    uint64_t input_buttons,
    const bool roles[32],
    const bool functions[1] = nullptr
) {
    const auto active_token = [&](uint32_t token) {
        if (token <= kUltimateProfileButtonTokenMax) {
            return IsPressedButtonToken(profile, input_buttons, token);
        }
        if (token >= kUltimateProfileRoleTokenMin && token <= kUltimateProfileRoleTokenMax) {
            return roles[token - 65];
        }
        return functions != nullptr && token == kUltimateProfileFunctionTokenX1 && functions[0];
    };
    for (size_t index = 0; index < condition.all_tokens_count; ++index) {
        const uint32_t token = condition.all_tokens[index];
        if (!active_token(token)) {
            return false;
        }
    }
    if (condition.any_tokens_count != 0) {
        bool any_active = false;
        for (size_t index = 0; index < condition.any_tokens_count; ++index) {
            const uint32_t token = condition.any_tokens[index];
            any_active = any_active || active_token(token);
        }
        if (!any_active) {
            return false;
        }
    }
    for (size_t index = 0; index < condition.none_tokens_count; ++index) {
        const uint32_t token = condition.none_tokens[index];
        if (active_token(token)) {
            return false;
        }
    }
    return true;
}

inline void EvaluateRoles(const UltimateProfile &profile, uint64_t input_buttons, bool roles[32],
                          const bool functions[1] = nullptr) {
    for (size_t role = 0; role < 32; ++role) {
        roles[role] = false;
    }
    if (profile.schema_version != kUltimateProfileSchemaVersionV2 &&
        profile.schema_version != kUltimateProfileSchemaVersionV3 &&
        profile.schema_version != kUltimateProfileSchemaVersionV4) {
        return;
    }
    // Evaluate by role id, not persisted array order. Validation constrains
    // dependencies to lower ids, so this is a deterministic topological walk.
    for (uint8_t role_id = 1; role_id <= 32; ++role_id) {
        for (size_t index = 0; index < profile.roles_count; ++index) {
            const UltimateProfileRole &role = profile.roles[index];
            if (role.role_id == role_id) {
                roles[role_id - 1] = EvaluateCondition(profile, role.condition, input_buttons, roles, functions);
                break;
            }
        }
    }
}

inline RoutingState EvaluateRouting(const UltimateProfile &profile, uint64_t input_buttons) {
    RoutingState routing{};
    if (profile.schema_version != kUltimateProfileSchemaVersionV2 &&
        profile.schema_version != kUltimateProfileSchemaVersionV3 &&
        profile.schema_version != kUltimateProfileSchemaVersionV4) {
        return routing;
    }
    for (size_t index = 0; index < profile.routing_slots_count; ++index) {
        const UltimateProfileRoutingSlot &slot = profile.routing_slots[index];
        if (slot.slot_id <= kUltimateProfileButtonTokenMax) {
            routing.slots[slot.slot_id] = (input_buttons & (uint64_t{1} << (slot.input_token - 1))) != 0;
        }
    }
    return routing;
}

// Stage C performs one logical routing pass after the existing remap/SOCD
// preprocessing.  A v3 profile declares every input consumed by the current
// Ultimate output pipeline, so no later phase can accidentally consult the
// physical, pre-routing slot a second time.
inline uint64_t RouteLogicalInputs(const UltimateProfile *profile, uint64_t input_buttons) {
    if (profile == nullptr || (profile->schema_version != kUltimateProfileSchemaVersionV3 &&
        profile->schema_version != kUltimateProfileSchemaVersionV4)) {
        return input_buttons;
    }
    uint64_t routed = 0;
    for (size_t index = 0; index < profile->routing_slots_count; ++index) {
        const UltimateProfileRoutingSlot &slot = profile->routing_slots[index];
        if ((input_buttons & (uint64_t{1} << (slot.input_token - 1))) != 0) {
            routed |= uint64_t{1} << (slot.slot_id - 1);
        }
    }
    return routed;
}

// Binding conditions deliberately bypass routing slots.  They see the same
// remap/SOCD-processed physical snapshot Ultimate receives, before the V3/V4
// logical-routing pass.  This prevents a logical slot from intrinsically
// acquiring X1 meaning.
inline bool EvaluatePhysicalBindingCondition(const UltimateProfileCondition &condition,
                                             uint64_t input_buttons) {
    const auto active = [&](uint32_t token) {
        return token >= kUltimateProfileButtonTokenMin && token <= kUltimateProfileButtonTokenMax &&
            (input_buttons & (uint64_t{1} << (token - 1))) != 0;
    };
    for (size_t i = 0; i < condition.all_tokens_count; ++i) if (!active(condition.all_tokens[i])) return false;
    if (condition.any_tokens_count != 0) {
        bool any = false;
        for (size_t i = 0; i < condition.any_tokens_count; ++i) any = any || active(condition.any_tokens[i]);
        if (!any) return false;
    }
    for (size_t i = 0; i < condition.none_tokens_count; ++i) if (active(condition.none_tokens[i])) return false;
    return true;
}

// A profile-declared function owns exactly one physical carrier.  This helper
// deliberately rechecks the bounded representation at runtime, so malformed
// in-memory state fails closed and cannot suppress an unrelated legacy input.
inline uint8_t ClaimedCarrierToken(const UltimateProfile *profile) {
    if (profile == nullptr || profile->schema_version != kUltimateProfileSchemaVersionV4 ||
        profile->function_bindings_count != 1) return 0;
    const UltimateProfileFunctionBinding &binding = profile->function_bindings[0];
    if (binding.function_class != UltimateControllerFunctionClass_ULTIMATE_CONTROLLER_FUNCTION_STICK_TABLE_MODIFIER ||
        binding.function_instance != UltimateControllerFunctionInstance_ULTIMATE_CONTROLLER_FUNCTION_INSTANCE_X1 ||
        binding.carrier_token < kUltimateProfileButtonTokenMin ||
        binding.carrier_token > kUltimateProfileButtonTokenMax) return 0;
    const UltimateProfileCondition &condition = binding.activation_condition;
    if (condition.all_tokens_count > sizeof(condition.all_tokens) / sizeof(condition.all_tokens[0]) ||
        condition.any_tokens_count > sizeof(condition.any_tokens) / sizeof(condition.any_tokens[0]) ||
        condition.none_tokens_count > sizeof(condition.none_tokens) / sizeof(condition.none_tokens[0]) ||
        (condition.all_tokens_count == 0 && condition.any_tokens_count == 0)) return 0;
    bool seen[kUltimateProfileButtonTokenMax + 1] = {};
    size_t all_matches = 0;
    const uint8_t *lists[] = {condition.all_tokens, condition.any_tokens, condition.none_tokens};
    const size_t counts[] = {condition.all_tokens_count, condition.any_tokens_count, condition.none_tokens_count};
    for (size_t list = 0; list < 3; ++list) {
        for (size_t i = 0; i < counts[list]; ++i) {
            const uint32_t token = lists[list][i];
            if (token < kUltimateProfileButtonTokenMin || token > kUltimateProfileButtonTokenMax || seen[token]) return 0;
            seen[token] = true;
            if (list == 0) all_matches += token == binding.carrier_token;
            else if (token == binding.carrier_token) return 0;
        }
    }
    return all_matches == 1 ? static_cast<uint8_t>(binding.carrier_token) : 0;
}

inline uint64_t ConsumeClaimedCarrier(const UltimateProfile *profile, uint64_t input_buttons) {
    const uint8_t carrier = ClaimedCarrierToken(profile);
    return carrier == 0 ? input_buttons : input_buttons & ~(uint64_t{1} << (carrier - 1));
}

inline void EvaluateFunctions(const UltimateProfile &profile, uint64_t input_buttons, bool functions[1]) {
    functions[0] = false;
    if (profile.schema_version != kUltimateProfileSchemaVersionV4 || profile.function_bindings_count != 1) return;
    const UltimateProfileFunctionBinding &binding = profile.function_bindings[0];
    functions[0] = ClaimedCarrierToken(&profile) != 0 &&
        EvaluatePhysicalBindingCondition(binding.activation_condition, input_buttons);
}

inline uint8_t SelectTable(
    const UltimateProfile *profile,
    uint64_t input_buttons,
    uint8_t legacy_table_id
) {
    if (profile == nullptr || (profile->schema_version != kUltimateProfileSchemaVersionV2 &&
                               profile->schema_version != kUltimateProfileSchemaVersionV3 &&
                               profile->schema_version != kUltimateProfileSchemaVersionV4)) {
        return legacy_table_id;
    }

    bool functions[1] = {};
    EvaluateFunctions(*profile, input_buttons, functions);
    bool roles[32] = {};
    EvaluateRoles(*profile, input_buttons, roles, functions);
    uint8_t selected_table = static_cast<uint8_t>(profile->default_table_id);
    uint32_t selected_priority = UINT32_MAX;
    for (size_t index = 0; index < profile->table_rules_count; ++index) {
        const UltimateProfileTableRule &rule = profile->table_rules[index];
        if (rule.priority < selected_priority && EvaluateCondition(*profile, rule.condition, input_buttons, roles, functions)) {
            selected_priority = rule.priority;
            selected_table = static_cast<uint8_t>(rule.table_id);
        }
    }
    if (profile->schema_version == kUltimateProfileSchemaVersionV4 && functions[0]) {
        const UltimateProfileFunctionBinding &binding = profile->function_bindings[0];
        const uint8_t exclusions[] = {3, 4, 5, 14, 15, 19, 20, 21};
        bool excluded = false;
        for (uint8_t role_id : exclusions) excluded = excluded || roles[role_id - 1];
        if (!excluded) {
            const bool mode = roles[0];
            const uint32_t priority = mode ? binding.mode_priority : binding.base_priority;
            if (priority < selected_priority) {
                selected_priority = priority;
                selected_table = static_cast<uint8_t>(mode ? binding.mode_table_id : binding.base_table_id);
            }
        }
    }
    return selected_table;
}

}  // namespace UltimateProfileEvaluator
