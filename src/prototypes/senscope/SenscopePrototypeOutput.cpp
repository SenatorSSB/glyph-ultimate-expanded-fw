#include "prototypes/senscope/SenscopePrototypeOutput.hpp"

namespace senscope::prototype {

namespace {

SenscopePrototypeOutputDiagnosticCode MapForceDiagnosticCode(
    SenscopePrototypeForceDiagnosticCode code
) {
    switch (code) {
        case SenscopePrototypeForceDiagnosticCode::EqualPriorityRuleAmbiguity:
            return SenscopePrototypeOutputDiagnosticCode::ForceAmbiguousHighestPriorityMatch;
        case SenscopePrototypeForceDiagnosticCode::DirectionKeyOutOfRange:
            return SenscopePrototypeOutputDiagnosticCode::ForceInvalidDirectionKey;
        case SenscopePrototypeForceDiagnosticCode::RuleHasUnknownDigitalOutputBits:
            return SenscopePrototypeOutputDiagnosticCode::ForceInvalidRuleDigitalOutputs;
        case SenscopePrototypeForceDiagnosticCode::RuleRequiresPostSocdHorizontalPolicy:
            return SenscopePrototypeOutputDiagnosticCode::ForceInvalidRuleHorizontalPolicy;
        case SenscopePrototypeForceDiagnosticCode::RuleFormUnsupported:
            return SenscopePrototypeOutputDiagnosticCode::ForceUnsupportedRuleForm;
        case SenscopePrototypeForceDiagnosticCode::None:
        case SenscopePrototypeForceDiagnosticCode::NoMatchingRule:
        default:
            return SenscopePrototypeOutputDiagnosticCode::None;
    }
}

SenscopePrototypeOutputDiagnosticCode MapDigitalDiagnosticCode(
    SenscopePrototypeDigitalDiagnosticCode code
) {
    switch (code) {
        case SenscopePrototypeDigitalDiagnosticCode::DirectMaskHasUnknownOutputBits:
            return SenscopePrototypeOutputDiagnosticCode::DigitalInvalidDirectOutputMask;
        case SenscopePrototypeDigitalDiagnosticCode::RuleMaskHasUnknownOutputBits:
            return SenscopePrototypeOutputDiagnosticCode::DigitalInvalidRuleOutputMask;
        case SenscopePrototypeDigitalDiagnosticCode::None:
        default:
            return SenscopePrototypeOutputDiagnosticCode::None;
    }
}

SenscopePrototypeOutputDiagnosticCode MapResolverDiagnosticCode(
    SenscopePrototypeResolverDiagnosticCode code
) {
    switch (code) {
        case SenscopePrototypeResolverDiagnosticCode::SubsetFallbackNotFound:
        case SenscopePrototypeResolverDiagnosticCode::ExactMatchRequiredButNotFound:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverNoMatchingComboProfile;
        case SenscopePrototypeResolverDiagnosticCode::ProfileValidationFailed:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverProfileInvalid;
        case SenscopePrototypeResolverDiagnosticCode::ExactComboPriorityAmbiguity:
        case SenscopePrototypeResolverDiagnosticCode::SubsetComboPriorityAmbiguity:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverAmbiguousComboProfile;
        case SenscopePrototypeResolverDiagnosticCode::ComboIndexOutOfRange:
        case SenscopePrototypeResolverDiagnosticCode::TableIndexOutOfRange:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverComboTableIndexOutOfRange;
        case SenscopePrototypeResolverDiagnosticCode::TableDisabled:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverTableDisabled;
        case SenscopePrototypeResolverDiagnosticCode::DirectionEntryMissing:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverMissingDirectionEntry;
        case SenscopePrototypeResolverDiagnosticCode::DirectionKeyOutOfRange:
            return SenscopePrototypeOutputDiagnosticCode::TableResolverInvalidDirectionKey;
        case SenscopePrototypeResolverDiagnosticCode::None:
        default:
            return SenscopePrototypeOutputDiagnosticCode::None;
    }
}

bool ForceResultIsFailure(const SenscopePrototypeForceResult &result) {
    return result.status != SenscopePrototypeForceStatus::NoMatchingRule &&
           result.status != SenscopePrototypeForceStatus::Resolved;
}

bool ResolverResultIsFailure(const SenscopePrototypeResolverResult &result) {
    return result.status != SenscopePrototypeResolverStatus::Resolved &&
           result.status != SenscopePrototypeResolverStatus::NoMatchingComboProfile;
}

} // namespace

SenscopePrototypeOutputResult ComposeSenscopePrototypeOutput(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeOutputRequest &request
) noexcept {
    SenscopePrototypeOutputResult result = {};

    const SenscopePrototypeDirectionRequest direction_request = {
        .pre_socd_direction_roles = request.pre_socd_direction_roles,
        .opposite_policy = request.direction_opposite_policy,
    };
    result.direction_result = ResolveSenscopePrototypeDirection(direction_request);
    result.output_packet.resolved_direction_key = result.direction_result.resolved_direction_key;
    result.output_packet.post_socd_direction_roles = result.direction_result.post_socd_direction_roles;
    if (result.direction_result.status != SenscopePrototypeDirectionStatus::Resolved) {
        result.status = SenscopePrototypeOutputStatus::DirectionFailed;
        result.diagnostic_code = SenscopePrototypeOutputDiagnosticCode::DirectionUnknownRoleBitsMasked;
        result.diagnostic_detail = result.direction_result.diagnostic_detail;
        return result;
    }

    const SenscopePrototypeForceRequest force_request = {
        .active_physical_button_mask = request.active_physical_button_mask,
        .post_socd_direction_key = static_cast<uint8_t>(result.direction_result.resolved_direction_key),
        .horizontal_x_choices = request.force_horizontal_x_choices,
    };
    result.force_result = ResolveSenscopePrototypeProfileForceOverride(profile, force_request);
    result.output_packet.selected_force_rule_index = result.force_result.selected_rule_index;
    result.output_packet.has_force_override = result.force_result.status == SenscopePrototypeForceStatus::Resolved;
    if (ForceResultIsFailure(result.force_result)) {
        result.status = SenscopePrototypeOutputStatus::ForceFailed;
        result.diagnostic_code = MapForceDiagnosticCode(result.force_result.diagnostic_code);
        result.diagnostic_detail = result.force_result.diagnostic_detail;
        return result;
    }

    const SenscopePrototypeDigitalRequest digital_request = {
        .direct_digital_output_mask = request.direct_digital_output_mask,
        .active_physical_button_mask = request.active_physical_button_mask,
    };
    result.digital_result = ComposeSenscopePrototypeProfileDigitalOutputs(profile, digital_request);
    if (result.digital_result.status != SenscopePrototypeDigitalStatus::Composed) {
        result.status = SenscopePrototypeOutputStatus::DigitalFailed;
        result.diagnostic_code = MapDigitalDiagnosticCode(result.digital_result.diagnostic_code);
        result.diagnostic_detail = result.digital_result.diagnostic_detail;
        return result;
    }
    result.output_packet.used_digital_composition = true;
    result.output_packet.digital_output_mask = result.digital_result.composed_digital_output_mask;

    if (result.force_result.status == SenscopePrototypeForceStatus::Resolved) {
        result.output_packet.left_stick_raw_coordinate = result.force_result.left_stick_raw_coordinate;
        result.output_packet.digital_output_mask |= result.force_result.digital_output_contribution;
        result.output_packet.has_left_stick = true;
        result.output_packet.has_force_override = true;
        result.output_packet.used_table_resolver = false;
        result.status = SenscopePrototypeOutputStatus::Composed;
        result.diagnostic_code = SenscopePrototypeOutputDiagnosticCode::None;
        return result;
    }

    const SenscopePrototypeResolverRequest resolver_request = {
        .active_modifier_mask = request.active_modifier_mask,
        .resolved_direction_key = static_cast<uint8_t>(result.direction_result.resolved_direction_key),
        .fallback_policy = request.resolver_fallback_policy,
    };
    result.resolver_result = ResolveSenscopePrototypeLeftStickRawCoordinate(profile, resolver_request);
    result.output_packet.used_table_resolver = true;
    result.output_packet.selected_combo_profile_index = result.resolver_result.selected_combo_profile_index;
    result.output_packet.selected_left_stick_table_index =
        result.resolver_result.selected_left_stick_table_index;

    if (result.resolver_result.status == SenscopePrototypeResolverStatus::Resolved) {
        result.output_packet.left_stick_raw_coordinate = result.resolver_result.raw_coordinate;
        result.output_packet.has_left_stick = true;
        result.status = SenscopePrototypeOutputStatus::Composed;
        result.diagnostic_code = SenscopePrototypeOutputDiagnosticCode::None;
        return result;
    }

    result.diagnostic_code = MapResolverDiagnosticCode(result.resolver_result.diagnostic_code);
    result.diagnostic_detail = result.resolver_result.diagnostic_detail;

    if (result.resolver_result.status == SenscopePrototypeResolverStatus::NoMatchingComboProfile) {
        result.status = SenscopePrototypeOutputStatus::NoLeftStickOutput;
        return result;
    }

    if (ResolverResultIsFailure(result.resolver_result)) {
        result.status = SenscopePrototypeOutputStatus::TableResolverFailed;
        return result;
    }

    result.status = SenscopePrototypeOutputStatus::NoLeftStickOutput;
    return result;
}

SenscopePrototypeOutputResult
ComposeSenscopePrototypeExampleOutput(const SenscopePrototypeOutputRequest &request) noexcept {
    return ComposeSenscopePrototypeOutput(GetSenscopePrototypeExampleProfile(), request);
}

} // namespace senscope::prototype
