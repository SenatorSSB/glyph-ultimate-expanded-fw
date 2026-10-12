#pragma once

#include "modes/UltimateProfileConfig.hpp"

#include <cstddef>
#include <cstdint>

// Stage-B evaluator for persisted Ultimate profile version 2. This consumes
// only the finite validated vocabulary and selects a table; it deliberately
// does not introduce output routing or any typed output effects.
namespace UltimateProfileEvaluator {

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
    if (profile.schema_version != kUltimateProfileSchemaVersionV2) {
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
    if (profile.schema_version != kUltimateProfileSchemaVersionV2) {
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

inline uint8_t SelectTable(
    const UltimateProfile *profile,
    uint64_t input_buttons,
    uint8_t legacy_table_id
) {
    if (profile == nullptr || profile->schema_version != kUltimateProfileSchemaVersionV2) {
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
