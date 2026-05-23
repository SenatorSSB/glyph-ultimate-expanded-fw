#include "prototypes/senscope/SenscopePrototypeResolver.hpp"

namespace senscope::prototype {

namespace {

struct SenscopePrototypeResolverComboSelection {
    bool found = false;
    bool ambiguous = false;
    uint8_t combo_profile_index = kSenscopePrototypeResolverInvalidIndex;
};

SenscopePrototypeResolverResult BuildSenscopePrototypeResolverResult(
    SenscopePrototypeResolverStatus status,
    SenscopePrototypeResolverDiagnosticCode diagnostic_code,
    uint16_t diagnostic_detail = 0
) {
    SenscopePrototypeResolverResult result = {};
    result.status = status;
    result.diagnostic_code = diagnostic_code;
    result.diagnostic_detail = diagnostic_detail;
    return result;
}

bool IsSenscopePrototypeDirectionKeyValid(uint8_t direction_key) {
    return direction_key >= static_cast<uint8_t>(SenscopePrototypeDirectionKey::D1) &&
           direction_key <= static_cast<uint8_t>(SenscopePrototypeDirectionKey::D9);
}

uint8_t ToSenscopePrototypeDirectionIndex(uint8_t direction_key) {
    return static_cast<uint8_t>(direction_key - static_cast<uint8_t>(SenscopePrototypeDirectionKey::D1));
}

SenscopePrototypeResolverComboSelection SelectBestExactSenscopePrototypeComboProfile(
    const SenscopePrototypeProfile &profile,
    SenscopePrototypeModifierCombinationMask active_modifier_mask
) {
    SenscopePrototypeResolverComboSelection selection = {};
    uint8_t best_priority = 0;
    bool has_best = false;

    for (std::size_t i = 0; i < profile.combo_profiles.size(); i++) {
        const SenscopePrototypeComboProfile &combo = profile.combo_profiles[i];
        if (!combo.enabled || combo.modifiers != active_modifier_mask) {
            continue;
        }

        if (!has_best || combo.priority > best_priority) {
            has_best = true;
            best_priority = combo.priority;
            selection.found = true;
            selection.ambiguous = false;
            selection.combo_profile_index = static_cast<uint8_t>(i);
            continue;
        }

        if (combo.priority == best_priority) {
            selection.ambiguous = true;
        }
    }

    return selection;
}

SenscopePrototypeResolverComboSelection SelectBestSubsetSenscopePrototypeComboProfile(
    const SenscopePrototypeProfile &profile,
    SenscopePrototypeModifierCombinationMask active_modifier_mask
) {
    SenscopePrototypeResolverComboSelection selection = {};
    uint8_t best_priority = 0;
    bool has_best = false;

    for (std::size_t i = 0; i < profile.combo_profiles.size(); i++) {
        const SenscopePrototypeComboProfile &combo = profile.combo_profiles[i];
        if (!combo.enabled) {
            continue;
        }
        if ((combo.modifiers & active_modifier_mask) != combo.modifiers) {
            continue;
        }

        if (!has_best || combo.priority > best_priority) {
            has_best = true;
            best_priority = combo.priority;
            selection.found = true;
            selection.ambiguous = false;
            selection.combo_profile_index = static_cast<uint8_t>(i);
            continue;
        }

        if (combo.priority == best_priority) {
            selection.ambiguous = true;
        }
    }

    return selection;
}

} // namespace

SenscopePrototypeResolverResult ResolveSenscopePrototypeLeftStickRawCoordinate(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeResolverRequest &request
) noexcept {
    const SenscopePrototypeValidationResult validation = ValidateSenscopePrototypeProfile(profile);
    if (!validation.is_valid) {
        return BuildSenscopePrototypeResolverResult(
            SenscopePrototypeResolverStatus::ProfileInvalid,
            SenscopePrototypeResolverDiagnosticCode::ProfileValidationFailed,
            static_cast<uint16_t>(validation.diagnostic_count)
        );
    }

    if (!IsSenscopePrototypeDirectionKeyValid(request.resolved_direction_key)) {
        return BuildSenscopePrototypeResolverResult(
            SenscopePrototypeResolverStatus::InvalidDirectionKey,
            SenscopePrototypeResolverDiagnosticCode::DirectionKeyOutOfRange,
            request.resolved_direction_key
        );
    }

    SenscopePrototypeResolverComboSelection selection =
        SelectBestExactSenscopePrototypeComboProfile(profile, request.active_modifier_mask);
    if (selection.found && selection.ambiguous) {
        return BuildSenscopePrototypeResolverResult(
            SenscopePrototypeResolverStatus::AmbiguousComboProfile,
            SenscopePrototypeResolverDiagnosticCode::ExactComboPriorityAmbiguity,
            request.active_modifier_mask
        );
    }

    if (!selection.found) {
        if (request.fallback_policy == SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile) {
            return BuildSenscopePrototypeResolverResult(
                SenscopePrototypeResolverStatus::NoMatchingComboProfile,
                SenscopePrototypeResolverDiagnosticCode::ExactMatchRequiredButNotFound,
                request.active_modifier_mask
            );
        }

        selection = SelectBestSubsetSenscopePrototypeComboProfile(profile, request.active_modifier_mask);
        if (!selection.found) {
            return BuildSenscopePrototypeResolverResult(
                SenscopePrototypeResolverStatus::NoMatchingComboProfile,
                SenscopePrototypeResolverDiagnosticCode::SubsetFallbackNotFound,
                request.active_modifier_mask
            );
        }
        if (selection.ambiguous) {
            return BuildSenscopePrototypeResolverResult(
                SenscopePrototypeResolverStatus::AmbiguousComboProfile,
                SenscopePrototypeResolverDiagnosticCode::SubsetComboPriorityAmbiguity,
                request.active_modifier_mask
            );
        }
    }

    if (selection.combo_profile_index >= profile.combo_profiles.size()) {
        return BuildSenscopePrototypeResolverResult(
            SenscopePrototypeResolverStatus::ComboTableIndexOutOfRange,
            SenscopePrototypeResolverDiagnosticCode::ComboIndexOutOfRange,
            selection.combo_profile_index
        );
    }

    const SenscopePrototypeComboProfile &combo = profile.combo_profiles[selection.combo_profile_index];

    SenscopePrototypeResolverResult table_result = {};
    table_result.selected_combo_profile_index = selection.combo_profile_index;
    table_result.selected_left_stick_table_index = combo.left_stick_table_index;

    if (combo.left_stick_table_index >= profile.left_stick_tables.size()) {
        table_result.status = SenscopePrototypeResolverStatus::ComboTableIndexOutOfRange;
        table_result.diagnostic_code = SenscopePrototypeResolverDiagnosticCode::TableIndexOutOfRange;
        table_result.diagnostic_detail = combo.left_stick_table_index;
        return table_result;
    }

    const SenscopePrototypeDirectionalStickTable9 &table = profile.left_stick_tables[combo.left_stick_table_index];
    if (!table.enabled) {
        table_result.status = SenscopePrototypeResolverStatus::TableDisabled;
        table_result.diagnostic_code = SenscopePrototypeResolverDiagnosticCode::TableDisabled;
        table_result.diagnostic_detail = combo.left_stick_table_index;
        return table_result;
    }

    const uint8_t direction_index = ToSenscopePrototypeDirectionIndex(request.resolved_direction_key);
    if (!table.entry_present[direction_index]) {
        table_result.status = SenscopePrototypeResolverStatus::MissingDirectionEntry;
        table_result.diagnostic_code = SenscopePrototypeResolverDiagnosticCode::DirectionEntryMissing;
        table_result.diagnostic_detail = request.resolved_direction_key;
        return table_result;
    }

    table_result.status = SenscopePrototypeResolverStatus::Resolved;
    table_result.raw_coordinate = table.entries[direction_index];
    table_result.diagnostic_code = SenscopePrototypeResolverDiagnosticCode::None;
    table_result.diagnostic_detail = 0;
    return table_result;
}

SenscopePrototypeResolverResult
ResolveSenscopePrototypeExampleLeftStickRawCoordinate(const SenscopePrototypeResolverRequest &request) noexcept {
    return ResolveSenscopePrototypeLeftStickRawCoordinate(GetSenscopePrototypeExampleProfile(), request);
}

} // namespace senscope::prototype
