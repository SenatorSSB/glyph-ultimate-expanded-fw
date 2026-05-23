#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <limits>

namespace senscope::prototype {

namespace {

constexpr SenscopePrototypeModifierCombinationMask kAllKnownModifierBits =
    (1u << kSenscopePrototypeModifierRoleCount) - 1u;

void AddDiagnostic(
    SenscopePrototypeValidationResult &result,
    SenscopePrototypeValidationSeverity severity,
    SenscopePrototypeValidationCode code,
    uint8_t index_a = 0,
    uint8_t index_b = 0,
    uint16_t detail = 0
) {
    if (result.diagnostic_count < result.diagnostics.size()) {
        result.diagnostics[result.diagnostic_count] = {
            .severity = severity,
            .code = code,
            .index_a = index_a,
            .index_b = index_b,
            .detail = detail,
        };
        result.diagnostic_count++;
    }

    if (severity == SenscopePrototypeValidationSeverity::Error) {
        result.is_valid = false;
    } else {
        result.has_todo_or_unknown = true;
    }
}

bool ProfileIsEnabled(const SenscopePrototypeComboProfile &profile) {
    return profile.enabled;
}

bool ForceRuleIsEnabled(const SenscopePrototypeForceStickOverrideRule &rule) {
    return rule.enabled;
}

bool DigitalRuleIsEnabled(const SenscopePrototypeDigitalMultiOutputRule &rule) {
    return rule.enabled;
}

bool LayerRoleMapIsEnabled(const SenscopePrototypeLayerRoleMap &map) {
    return map.enabled;
}

bool TableHasAtLeastOneEntry(const SenscopePrototypeDirectionalStickTable9 &table) {
    for (bool present : table.entry_present) {
        if (present) {
            return true;
        }
    }
    return false;
}

void ValidateComboProfiles(
    const SenscopePrototypeProfile &profile,
    SenscopePrototypeValidationResult &result
) {
    for (std::size_t i = 0; i < profile.combo_profiles.size(); i++) {
        const SenscopePrototypeComboProfile &combo = profile.combo_profiles[i];
        if (!ProfileIsEnabled(combo)) {
            continue;
        }

        if ((combo.modifiers & ~kAllKnownModifierBits) != 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ModifierMaskOutOfRange,
                static_cast<uint8_t>(i)
            );
        }

        if (combo.left_stick_table_index >= profile.left_stick_tables.size()) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ComboTableIndexOutOfRange,
                static_cast<uint8_t>(i),
                0,
                combo.left_stick_table_index
            );
            continue;
        }

        const SenscopePrototypeDirectionalStickTable9 &table =
            profile.left_stick_tables[combo.left_stick_table_index];
        if (!table.enabled) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ComboTableNotEnabled,
                static_cast<uint8_t>(i),
                0,
                combo.left_stick_table_index
            );
            continue;
        }

        // RawCoord components are uint8_t, so byte-range validity is enforced by type.
        if (!TableHasAtLeastOneEntry(table)) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::DirectionTableEmpty,
                static_cast<uint8_t>(combo.left_stick_table_index)
            );
        }
    }

    for (std::size_t i = 0; i < profile.combo_profiles.size(); i++) {
        const SenscopePrototypeComboProfile &lhs = profile.combo_profiles[i];
        if (!ProfileIsEnabled(lhs)) {
            continue;
        }
        for (std::size_t j = i + 1; j < profile.combo_profiles.size(); j++) {
            const SenscopePrototypeComboProfile &rhs = profile.combo_profiles[j];
            if (!ProfileIsEnabled(rhs)) {
                continue;
            }
            if (lhs.modifiers == rhs.modifiers) {
                AddDiagnostic(
                    result,
                    SenscopePrototypeValidationSeverity::Error,
                    lhs.priority == rhs.priority
                        ? SenscopePrototypeValidationCode::ComboExactDuplicateSamePriority
                        : SenscopePrototypeValidationCode::ComboExactDuplicateDifferentPriority,
                    static_cast<uint8_t>(i),
                    static_cast<uint8_t>(j)
                );
            }
        }
    }

    const SenscopePrototypeModifierCombinationMask max_active_combo =
        (1u << profile.modifier_role_count) - 1u;
    for (SenscopePrototypeModifierCombinationMask active = 1; active <= max_active_combo; active++) {
        bool found_match = false;
        uint8_t best_priority = 0;
        std::size_t best_priority_match_count = 0;

        for (const SenscopePrototypeComboProfile &combo : profile.combo_profiles) {
            if (!ProfileIsEnabled(combo)) {
                continue;
            }
            if ((combo.modifiers & active) != combo.modifiers) {
                continue;
            }

            if (!found_match || combo.priority > best_priority) {
                found_match = true;
                best_priority = combo.priority;
                best_priority_match_count = 1;
                continue;
            }

            if (combo.priority == best_priority) {
                best_priority_match_count++;
            }
        }

        if (best_priority_match_count > 1) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::EqualPriorityComboSubsetAmbiguity,
                active
            );
        }

        if (!found_match) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Todo,
                SenscopePrototypeValidationCode::UndefinedComboFallbackUnknownReachability,
                active
            );
        }
    }
}

void ValidateForceRules(const SenscopePrototypeProfile &profile, SenscopePrototypeValidationResult &result) {
    for (std::size_t i = 0; i < profile.force_override_rules.size(); i++) {
        const SenscopePrototypeForceStickOverrideRule &rule = profile.force_override_rules[i];
        if (!ForceRuleIsEnabled(rule)) {
            continue;
        }

        if (rule.trigger_mask == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ForceRuleEmptyTriggerMask,
                static_cast<uint8_t>(i)
            );
        }

        if (rule.digital_outputs == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ForceRuleMissingDigitalOutputs,
                static_cast<uint8_t>(i)
            );
        }

        if (
            rule.form == SenscopePrototypeForceUpBForm::ForcedUpwardYWithPostSocdHorizontalX &&
            !rule.use_post_socd_horizontal_x
        ) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::ForceRuleInvalidHorizontalPolicy,
                static_cast<uint8_t>(i)
            );
        }
    }

    for (std::size_t i = 0; i < profile.force_override_rules.size(); i++) {
        const SenscopePrototypeForceStickOverrideRule &lhs = profile.force_override_rules[i];
        if (!ForceRuleIsEnabled(lhs)) {
            continue;
        }
        for (std::size_t j = i + 1; j < profile.force_override_rules.size(); j++) {
            const SenscopePrototypeForceStickOverrideRule &rhs = profile.force_override_rules[j];
            if (!ForceRuleIsEnabled(rhs)) {
                continue;
            }

            if (lhs.trigger_mask == rhs.trigger_mask && lhs.priority == rhs.priority) {
                AddDiagnostic(
                    result,
                    SenscopePrototypeValidationSeverity::Error,
                    SenscopePrototypeValidationCode::EqualPrioritySameTargetForceRuleConflict,
                    static_cast<uint8_t>(i),
                    static_cast<uint8_t>(j)
                );
            }
        }
    }
}

void ValidateDigitalRules(
    const SenscopePrototypeProfile &profile,
    SenscopePrototypeValidationResult &result
) {
    for (std::size_t i = 0; i < profile.digital_multi_output_rules.size(); i++) {
        const SenscopePrototypeDigitalMultiOutputRule &rule = profile.digital_multi_output_rules[i];
        if (!DigitalRuleIsEnabled(rule)) {
            continue;
        }

        if (rule.condition_mask == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::DigitalRuleEmptyConditionMask,
                static_cast<uint8_t>(i)
            );
        }
        if (rule.outputs == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::DigitalRuleEmptyOutputs,
                static_cast<uint8_t>(i)
            );
        }
        if ((rule.outputs & ~kSenscopePrototypeKnownDigitalOutputsMask) != 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::DigitalRuleUnknownOutputBit,
                static_cast<uint8_t>(i)
            );
        }
    }
}

void ValidateLayerRoleMaps(
    const SenscopePrototypeProfile &profile,
    SenscopePrototypeValidationResult &result
) {
    for (std::size_t i = 0; i < profile.layer_role_maps.size(); i++) {
        const SenscopePrototypeLayerRoleMap &map = profile.layer_role_maps[i];
        if (!LayerRoleMapIsEnabled(map)) {
            continue;
        }

        if (map.held_condition_mask == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::LayerRoleMapEmptyHeldCondition,
                static_cast<uint8_t>(i)
            );
        }
        if (map.role_outputs == 0 && map.direction_outputs == 0) {
            AddDiagnostic(
                result,
                SenscopePrototypeValidationSeverity::Error,
                SenscopePrototypeValidationCode::LayerRoleMapNoRoleOutputs,
                static_cast<uint8_t>(i)
            );
        }
    }
}

SenscopePrototypeProfile BuildExampleProfile() {
    SenscopePrototypeProfile profile = {};
    profile.mode_name = "SenscopePrototype";
    profile.left_stick_only = true;
    profile.modifier_role_count = kSenscopePrototypeModifierRoleCount;

    profile.left_stick_tables[0].enabled = true;
    profile.left_stick_tables[0].entry_present = {
        true, true, true, true, true, true, true, true, true
    };
    profile.left_stick_tables[0].entries = {
        SenscopePrototypeRawCoord{28, 28},   // 1
        SenscopePrototypeRawCoord{128, 28},  // 2
        SenscopePrototypeRawCoord{228, 28},  // 3
        SenscopePrototypeRawCoord{28, 128},  // 4
        SenscopePrototypeRawCoord{128, 128}, // 5
        SenscopePrototypeRawCoord{228, 128}, // 6
        SenscopePrototypeRawCoord{28, 228},  // 7
        SenscopePrototypeRawCoord{128, 228}, // 8
        SenscopePrototypeRawCoord{228, 228}, // 9
    };

    profile.left_stick_tables[1].enabled = true;
    profile.left_stick_tables[1].entry_present = {
        true, true, true, true, true, true, true, true, true
    };
    profile.left_stick_tables[1].entries = {
        SenscopePrototypeRawCoord{44, 44},   // 1
        SenscopePrototypeRawCoord{128, 44},  // 2
        SenscopePrototypeRawCoord{212, 44},  // 3
        SenscopePrototypeRawCoord{44, 128},  // 4
        SenscopePrototypeRawCoord{128, 128}, // 5
        SenscopePrototypeRawCoord{212, 128}, // 6
        SenscopePrototypeRawCoord{44, 212},  // 7
        SenscopePrototypeRawCoord{128, 212}, // 8
        SenscopePrototypeRawCoord{212, 212}, // 9
    };

    profile.combo_profiles[0] = {
        .enabled = true,
        .modifiers = 0,
        .priority = 1,
        .left_stick_table_index = 0,
    };
    profile.combo_profiles[1] = {
        .enabled = true,
        .modifiers = 0b001,
        .priority = 2,
        .left_stick_table_index = 1,
    };

    profile.force_override_rules[0] = {
        .enabled = true,
        .trigger_mask = 1ull << 40,
        .priority = static_cast<uint8_t>(std::numeric_limits<uint8_t>::max()),
        .form = SenscopePrototypeForceUpBForm::FixedExactCoordinate,
        .fixed_coordinate = {128, 228},
        .forced_upward_y = 228,
        .use_post_socd_horizontal_x = false,
        .digital_outputs = kSenscopePrototypeOutputB,
    };
    profile.force_override_rules[1] = {
        .enabled = true,
        .trigger_mask = 1ull << 41,
        .priority = static_cast<uint8_t>(std::numeric_limits<uint8_t>::max()),
        .form = SenscopePrototypeForceUpBForm::ForcedUpwardYWithPostSocdHorizontalX,
        .fixed_coordinate = {128, 228},
        .forced_upward_y = 228,
        .use_post_socd_horizontal_x = true,
        .digital_outputs = kSenscopePrototypeOutputB,
    };

    profile.digital_multi_output_rules[0] = {
        .enabled = true,
        .condition_mask = 1ull << 42,
        .outputs = kSenscopePrototypeOutputB | kSenscopePrototypeOutputY,
    };

    profile.layer_role_maps[0] = {
        .enabled = true,
        .held_condition_mask = 1ull << 43,
        .role_outputs = kSenscopePrototypeLogicalRoleLayerModeHeld,
        .direction_outputs = kSenscopePrototypeDirectionRoleUp,
    };

    return profile;
}

} // namespace

const SenscopePrototypeProfile &GetSenscopePrototypeExampleProfile() {
    static const SenscopePrototypeProfile kExampleProfile = BuildExampleProfile();
    return kExampleProfile;
}

SenscopePrototypeValidationResult
ValidateSenscopePrototypeProfile(const SenscopePrototypeProfile &profile) noexcept {
    SenscopePrototypeValidationResult result = {};

    if (profile.modifier_role_count != kSenscopePrototypeModifierRoleCount) {
        AddDiagnostic(
            result,
            SenscopePrototypeValidationSeverity::Error,
            SenscopePrototypeValidationCode::ModifierRoleCountMismatch
        );
    }
    if (!profile.left_stick_only) {
        AddDiagnostic(
            result,
            SenscopePrototypeValidationSeverity::Error,
            SenscopePrototypeValidationCode::LeftStickOnlyFlagDisabled
        );
    }

    ValidateComboProfiles(profile, result);
    ValidateForceRules(profile, result);
    ValidateDigitalRules(profile, result);
    ValidateLayerRoleMaps(profile, result);
    return result;
}

} // namespace senscope::prototype
