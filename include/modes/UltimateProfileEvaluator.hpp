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
    if (profile == nullptr || profile->schema_version != kUltimateProfileSchemaVersionV3) return nullptr;
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
    const bool roles[32]
) {
    for (size_t index = 0; index < condition.all_tokens_count; ++index) {
        const uint32_t token = condition.all_tokens[index];
        const bool active = token <= kUltimateProfileButtonTokenMax
            ? IsPressedButtonToken(profile, input_buttons, token)
            : token >= kUltimateProfileRoleTokenMin && token <= kUltimateProfileRoleTokenMax &&
                roles[token - 65];
        if (!active) {
            return false;
        }
    }
    if (condition.any_tokens_count != 0) {
        bool any_active = false;
        for (size_t index = 0; index < condition.any_tokens_count; ++index) {
            const uint32_t token = condition.any_tokens[index];
            const bool active = token <= kUltimateProfileButtonTokenMax
                ? IsPressedButtonToken(profile, input_buttons, token)
                : token >= kUltimateProfileRoleTokenMin && token <= kUltimateProfileRoleTokenMax &&
                    roles[token - 65];
            any_active = any_active || active;
        }
        if (!any_active) {
            return false;
        }
    }
    for (size_t index = 0; index < condition.none_tokens_count; ++index) {
        const uint32_t token = condition.none_tokens[index];
        const bool active = token <= kUltimateProfileButtonTokenMax
            ? IsPressedButtonToken(profile, input_buttons, token)
            : token >= kUltimateProfileRoleTokenMin && token <= kUltimateProfileRoleTokenMax &&
                roles[token - 65];
        if (active) {
            return false;
        }
    }
    return true;
}

inline void EvaluateRoles(const UltimateProfile &profile, uint64_t input_buttons, bool roles[32]) {
    for (size_t role = 0; role < 32; ++role) {
        roles[role] = false;
    }
    if (profile.schema_version != kUltimateProfileSchemaVersionV2 &&
        profile.schema_version != kUltimateProfileSchemaVersionV3) {
        return;
    }
    // Evaluate by role id, not persisted array order. Validation constrains
    // dependencies to lower ids, so this is a deterministic topological walk.
    for (uint8_t role_id = 1; role_id <= 32; ++role_id) {
        for (size_t index = 0; index < profile.roles_count; ++index) {
            const UltimateProfileRole &role = profile.roles[index];
            if (role.role_id == role_id) {
                roles[role_id - 1] = EvaluateCondition(profile, role.condition, input_buttons, roles);
                break;
            }
        }
    }
}

inline RoutingState EvaluateRouting(const UltimateProfile &profile, uint64_t input_buttons) {
    RoutingState routing{};
    if (profile.schema_version != kUltimateProfileSchemaVersionV2 &&
        profile.schema_version != kUltimateProfileSchemaVersionV3) {
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
    if (profile == nullptr || profile->schema_version != kUltimateProfileSchemaVersionV3) {
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

inline uint8_t SelectTable(
    const UltimateProfile *profile,
    uint64_t input_buttons,
    uint8_t legacy_table_id
) {
    if (profile == nullptr || (profile->schema_version != kUltimateProfileSchemaVersionV2 &&
                               profile->schema_version != kUltimateProfileSchemaVersionV3)) {
        return legacy_table_id;
    }

    bool roles[32] = {};
    EvaluateRoles(*profile, input_buttons, roles);
    uint8_t selected_table = static_cast<uint8_t>(profile->default_table_id);
    uint32_t selected_priority = UINT32_MAX;
    for (size_t index = 0; index < profile->table_rules_count; ++index) {
        const UltimateProfileTableRule &rule = profile->table_rules[index];
        if (rule.priority < selected_priority && EvaluateCondition(*profile, rule.condition, input_buttons, roles)) {
            selected_priority = rule.priority;
            selected_table = static_cast<uint8_t>(rule.table_id);
        }
    }
    return selected_table;
}

}  // namespace UltimateProfileEvaluator
