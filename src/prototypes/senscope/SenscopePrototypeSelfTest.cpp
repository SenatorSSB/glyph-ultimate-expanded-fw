#include "prototypes/senscope/SenscopePrototypeSelfTest.hpp"

#include "prototypes/senscope/SenscopePrototypeDigital.hpp"
#include "prototypes/senscope/SenscopePrototypeDirection.hpp"
#include "prototypes/senscope/SenscopePrototypeForce.hpp"
#include "prototypes/senscope/SenscopePrototypeModifier.hpp"
#include "prototypes/senscope/SenscopePrototypeOutput.hpp"
#include "prototypes/senscope/SenscopePrototypeResolver.hpp"
#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

namespace senscope::prototype {

namespace {

constexpr SenscopePrototypePhysicalButtonMask kExampleDigitalRuleTriggerMask = 1ull << 42;
constexpr SenscopePrototypePhysicalButtonMask kExampleFixedForceRuleTriggerMask = 1ull << 40;
constexpr SenscopePrototypePhysicalButtonMask kExampleHorizontalForceRuleTriggerMask = 1ull << 41;
constexpr SenscopePrototypePhysicalButtonMask kModifierBindingSourceMaskA = 1ull << 44;
constexpr SenscopePrototypePhysicalButtonMask kModifierBindingSourceMaskB = 1ull << 45;
constexpr SenscopePrototypePhysicalButtonMask kModifierBindingSourceMaskC = 1ull << 46;
constexpr SenscopePrototypeModifierCombinationMask kExampleModifierMask001 = 0b001;
constexpr SenscopePrototypeModifierCombinationMask kUndefinedExactModifierMask010 = 0b010;
constexpr SenscopePrototypeModifierCombinationMask kSubsetFallbackModifierMask101 = 0b101;
constexpr SenscopePrototypeDigitalOutputMask kUnknownDigitalOutputBit = 1u << 13;

void AddSelfTestCaseResult(
    SenscopePrototypeSelfTestResult &result,
    SenscopePrototypeSelfTestCaseId case_id,
    bool passed
) {
    if (result.total_case_count < result.case_results.size()) {
        result.case_results[result.total_case_count] = {
            .case_id = case_id,
            .passed = passed,
        };
    }

    result.total_case_count++;
    if (passed) {
        result.passed_case_count++;
        return;
    }
    result.failed_case_count++;
}

bool CoordEquals(const SenscopePrototypeRawCoord &coord, uint8_t x, uint8_t y) {
    return coord.x == x && coord.y == y;
}

bool HasValidationCode(
    const SenscopePrototypeValidationResult &validation,
    SenscopePrototypeValidationCode code
) {
    for (std::size_t i = 0; i < validation.diagnostic_count; i++) {
        if (validation.diagnostics[i].code == code) {
            return true;
        }
    }
    return false;
}

} // namespace

SenscopePrototypeSelfTestResult RunSenscopePrototypeSelfTest() noexcept {
    SenscopePrototypeSelfTestResult result = {};
    const SenscopePrototypeProfile &example_profile = GetSenscopePrototypeExampleProfile();

    const SenscopePrototypeValidationResult validation = ValidateSenscopePrototypeProfile(example_profile);
    AddSelfTestCaseResult(
        result,
        SenscopePrototypeSelfTestCaseId::ValidationExampleProfile,
        validation.is_valid
    );
    if (!validation.is_valid) {
        result.status = SenscopePrototypeSelfTestStatus::ProfileInvalid;
        return result;
    }

    {
        SenscopePrototypeProfile profile_with_duplicate_mask = example_profile;
        profile_with_duplicate_mask.combo_profiles[2] = {
            .enabled = true,
            .modifiers = profile_with_duplicate_mask.combo_profiles[1].modifiers,
            .priority = static_cast<uint8_t>(profile_with_duplicate_mask.combo_profiles[1].priority + 1u),
            .left_stick_table_index =
                profile_with_duplicate_mask.combo_profiles[1].left_stick_table_index,
        };
        const SenscopePrototypeValidationResult duplicate_mask_validation =
            ValidateSenscopePrototypeProfile(profile_with_duplicate_mask);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ValidationDuplicateExactComboMaskRejectedOrDiagnosed,
            !duplicate_mask_validation.is_valid &&
                HasValidationCode(
                    duplicate_mask_validation,
                    SenscopePrototypeValidationCode::ComboExactDuplicateDifferentPriority
                )
        );
    }

    {
        const bool direction_five_entry_present =
            example_profile.left_stick_tables[1].enabled &&
            example_profile.left_stick_tables[1].entry_present[kSenscopePrototypeDirectionFiveIndex];
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ValidationDirectionFiveEntryAllowed,
            direction_five_entry_present && validation.is_valid
        );
    }

    {
        SenscopePrototypeProfile profile_with_unknown_digital_output = example_profile;
        profile_with_unknown_digital_output.digital_multi_output_rules[1] = {
            .enabled = true,
            .condition_mask = 1ull << 50,
            .outputs = kUnknownDigitalOutputBit,
        };
        const SenscopePrototypeValidationResult unknown_digital_output_validation =
            ValidateSenscopePrototypeProfile(profile_with_unknown_digital_output);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ValidationDigitalRuleUnknownOutputRejected,
            !unknown_digital_output_validation.is_valid &&
                HasValidationCode(
                    unknown_digital_output_validation,
                    SenscopePrototypeValidationCode::DigitalRuleUnknownOutputBit
                )
        );
    }

    {
        SenscopePrototypeProfile profile_with_missing_force_outputs = example_profile;
        profile_with_missing_force_outputs.force_override_rules[2] = {
            .enabled = true,
            .trigger_mask = 1ull << 51,
            .priority = 127,
            .form = SenscopePrototypeForceUpBForm::FixedExactCoordinate,
            .fixed_coordinate = {128, 200},
            .forced_upward_y = 200,
            .use_post_socd_horizontal_x = false,
            .digital_outputs = 0,
        };
        const SenscopePrototypeValidationResult missing_force_outputs_validation =
            ValidateSenscopePrototypeProfile(profile_with_missing_force_outputs);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ValidationForceRuleMissingDigitalOutputRejected,
            !missing_force_outputs_validation.is_valid &&
                HasValidationCode(
                    missing_force_outputs_validation,
                    SenscopePrototypeValidationCode::ForceRuleMissingDigitalOutputs
                )
        );
    }

    {
        SenscopePrototypeProfile profile_with_empty_layer_role_map = example_profile;
        profile_with_empty_layer_role_map.layer_role_maps[1] = {
            .enabled = true,
            .held_condition_mask = 1ull << 52,
            .role_outputs = 0,
            .direction_outputs = 0,
        };
        const SenscopePrototypeValidationResult empty_layer_role_map_validation =
            ValidateSenscopePrototypeProfile(profile_with_empty_layer_role_map);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ValidationLayerRoleMapEmptyRejected,
            !empty_layer_role_map_validation.is_valid &&
                HasValidationCode(
                    empty_layer_role_map_validation,
                    SenscopePrototypeValidationCode::LayerRoleMapNoRoleOutputs
                )
        );
    }

    {
        const SenscopePrototypeModifierRequest request = {};
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierNoBindingsReturnsZeroMask,
            modifier_result.status == SenscopePrototypeModifierStatus::Resolved &&
                modifier_result.active_modifier_mask == 0 &&
                modifier_result.triggered_binding_count == 0
        );
    }

    {
        SenscopePrototypeModifierRequest request = {};
        request.active_physical_button_mask = kModifierBindingSourceMaskA;
        request.bindings[0] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskA,
            .modifier_bit_index = 0,
        };
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierSingleBindingSetsBit0,
            modifier_result.status == SenscopePrototypeModifierStatus::Resolved &&
                modifier_result.active_modifier_mask == static_cast<SenscopePrototypeModifierCombinationMask>(0b001) &&
                modifier_result.triggered_binding_count == 1
        );
    }

    {
        SenscopePrototypeModifierRequest request = {};
        request.active_physical_button_mask =
            kModifierBindingSourceMaskA | kModifierBindingSourceMaskC;
        request.bindings[0] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskA,
            .modifier_bit_index = 0,
        };
        request.bindings[1] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskB,
            .modifier_bit_index = 1,
        };
        request.bindings[2] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskC,
            .modifier_bit_index = 2,
        };
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierMultipleBindingsSetBits,
            modifier_result.status == SenscopePrototypeModifierStatus::Resolved &&
                modifier_result.active_modifier_mask == static_cast<SenscopePrototypeModifierCombinationMask>(0b101) &&
                modifier_result.triggered_binding_count == 2
        );
    }

    {
        SenscopePrototypeModifierRequest request = {};
        request.active_physical_button_mask = kModifierBindingSourceMaskA;
        request.bindings[0] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskA,
            .modifier_bit_index = 1,
        };
        request.bindings[1] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskA,
            .modifier_bit_index = 1,
        };
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierDuplicateSourcesOrComposeSameBit,
            modifier_result.status == SenscopePrototypeModifierStatus::Resolved &&
                modifier_result.active_modifier_mask == static_cast<SenscopePrototypeModifierCombinationMask>(0b010) &&
                modifier_result.triggered_binding_count == 2
        );
    }

    {
        SenscopePrototypeModifierRequest request = {};
        request.active_physical_button_mask = kModifierBindingSourceMaskA;
        request.bindings[0] = {
            .enabled = true,
            .physical_button_mask = kModifierBindingSourceMaskA,
            .modifier_bit_index = static_cast<uint8_t>(kSenscopePrototypeModifierRoleCount),
        };
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierInvalidBitIndexRejected,
            modifier_result.status == SenscopePrototypeModifierStatus::InvalidBinding &&
                modifier_result.active_modifier_mask == 0 &&
                modifier_result.triggered_binding_count == 0 &&
                modifier_result.diagnostic_binding_index == 0 &&
                modifier_result.diagnostic_code ==
                    SenscopePrototypeModifierDiagnosticCode::BindingModifierBitIndexOutOfRange
        );
    }

    {
        SenscopePrototypeModifierRequest request = {};
        request.bindings[0] = {
            .enabled = true,
            .physical_button_mask = 0,
            .modifier_bit_index = 0,
        };
        const SenscopePrototypeModifierResult modifier_result =
            BuildSenscopePrototypeActiveModifierMask(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ModifierEmptyBindingRejected,
            modifier_result.status == SenscopePrototypeModifierStatus::InvalidBinding &&
                modifier_result.active_modifier_mask == 0 &&
                modifier_result.triggered_binding_count == 0 &&
                modifier_result.diagnostic_binding_index == 0 &&
                modifier_result.diagnostic_code ==
                    SenscopePrototypeModifierDiagnosticCode::BindingPhysicalButtonMaskEmpty
        );
    }

    {
        SenscopePrototypeDirectionRequest request = {};
        request.pre_socd_direction_roles = 0;
        request.opposite_policy = SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
        const SenscopePrototypeDirectionResult direction_result = ResolveSenscopePrototypeDirection(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DirectionNeutralRoleMaskResolvesD5,
            direction_result.status == SenscopePrototypeDirectionStatus::Resolved &&
                direction_result.resolved_direction_key == SenscopePrototypeDirectionKey::D5
        );
    }

    {
        SenscopePrototypeDirectionRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft | kSenscopePrototypeDirectionRoleUp;
        request.opposite_policy = SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
        const SenscopePrototypeDirectionResult direction_result = ResolveSenscopePrototypeDirection(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DirectionLeftUpResolvesD7,
            direction_result.status == SenscopePrototypeDirectionStatus::Resolved &&
                direction_result.resolved_direction_key == SenscopePrototypeDirectionKey::D7
        );
    }

    {
        SenscopePrototypeDirectionRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft |
            kSenscopePrototypeDirectionRoleRight |
            kSenscopePrototypeDirectionRoleUp;
        request.opposite_policy = SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
        const SenscopePrototypeDirectionResult direction_result = ResolveSenscopePrototypeDirection(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DirectionLeftRightUpNeutralOnOppositeResolvesD8,
            direction_result.status == SenscopePrototypeDirectionStatus::Resolved &&
                direction_result.resolved_direction_key == SenscopePrototypeDirectionKey::D8
        );
    }

    {
        SenscopePrototypeDirectionRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft | kSenscopePrototypeDirectionRoleRight;
        request.opposite_policy = SenscopePrototypeDirectionOppositePolicy::LeftPriority;
        const SenscopePrototypeDirectionResult direction_result = ResolveSenscopePrototypeDirection(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DirectionLeftRightLeftPriorityResolvesD4,
            direction_result.status == SenscopePrototypeDirectionStatus::Resolved &&
                direction_result.resolved_direction_key == SenscopePrototypeDirectionKey::D4
        );
    }

    {
        SenscopePrototypeDirectionRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleDown | kSenscopePrototypeDirectionRoleUp;
        request.opposite_policy = SenscopePrototypeDirectionOppositePolicy::UpPriority;
        const SenscopePrototypeDirectionResult direction_result = ResolveSenscopePrototypeDirection(request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DirectionDownUpUpPriorityResolvesD8,
            direction_result.status == SenscopePrototypeDirectionStatus::Resolved &&
                direction_result.resolved_direction_key == SenscopePrototypeDirectionKey::D8
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = 0;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D5);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverModifier000DirectionD5ResolvesBaseNeutral,
            resolver_result.status == SenscopePrototypeResolverStatus::Resolved &&
                resolver_result.selected_combo_profile_index == 0 &&
                resolver_result.selected_left_stick_table_index == 0 &&
                CoordEquals(resolver_result.raw_coordinate, 128, 128)
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = 0;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D6);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverModifier000DirectionD6ResolvesBaseRight,
            resolver_result.status == SenscopePrototypeResolverStatus::Resolved &&
                resolver_result.selected_combo_profile_index == 0 &&
                resolver_result.selected_left_stick_table_index == 0 &&
                CoordEquals(resolver_result.raw_coordinate, 228, 128)
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = 0;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D4);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverModifier000DirectionD4ResolvesBaseLeft,
            resolver_result.status == SenscopePrototypeResolverStatus::Resolved &&
                resolver_result.selected_combo_profile_index == 0 &&
                resolver_result.selected_left_stick_table_index == 0 &&
                CoordEquals(resolver_result.raw_coordinate, 28, 128)
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = kExampleModifierMask001;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D7);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::AllowHighestPrioritySubset;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverModifier001DirectionD7ResolvesTable1,
            resolver_result.status == SenscopePrototypeResolverStatus::Resolved &&
                resolver_result.selected_left_stick_table_index == 1 &&
                CoordEquals(resolver_result.raw_coordinate, 44, 212)
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = kUndefinedExactModifierMask010;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D7);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverExactRequiredUndefinedComboNoMatch,
            resolver_result.status == SenscopePrototypeResolverStatus::NoMatchingComboProfile &&
                resolver_result.diagnostic_code ==
                    SenscopePrototypeResolverDiagnosticCode::ExactMatchRequiredButNotFound
        );
    }

    {
        SenscopePrototypeResolverRequest request = {};
        request.active_modifier_mask = kSubsetFallbackModifierMask101;
        request.resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D7);
        request.fallback_policy = SenscopePrototypeResolverFallbackPolicy::AllowHighestPrioritySubset;
        const SenscopePrototypeResolverResult resolver_result =
            ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ResolverSubsetFallbackDefinedSubsetResolves,
            resolver_result.status == SenscopePrototypeResolverStatus::Resolved &&
                resolver_result.selected_combo_profile_index == 1 &&
                CoordEquals(resolver_result.raw_coordinate, 44, 212)
        );
    }

    {
        SenscopePrototypeDigitalRequest request = {};
        request.direct_digital_output_mask = kSenscopePrototypeOutputA;
        request.active_physical_button_mask = kExampleDigitalRuleTriggerMask;
        const SenscopePrototypeDigitalResult digital_result =
            ComposeSenscopePrototypeProfileDigitalOutputs(example_profile, request);
        const SenscopePrototypeDigitalOutputMask expected_mask =
            kSenscopePrototypeOutputA | kSenscopePrototypeOutputB | kSenscopePrototypeOutputY;
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DigitalDirectAWithTriggeredByRuleComposesABY,
            digital_result.status == SenscopePrototypeDigitalStatus::Composed &&
                digital_result.composed_digital_output_mask == expected_mask &&
                digital_result.triggered_rule_count == 1
        );
    }

    {
        SenscopePrototypeDigitalRequest request = {};
        request.direct_digital_output_mask = kSenscopePrototypeOutputA | kUnknownDigitalOutputBit;
        request.active_physical_button_mask = 0;
        const SenscopePrototypeDigitalResult digital_result =
            ComposeSenscopePrototypeProfileDigitalOutputs(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::DigitalUnknownDirectOutputBitDiagnostic,
            digital_result.status == SenscopePrototypeDigitalStatus::InvalidDirectOutputMask &&
                digital_result.diagnostic_code ==
                    SenscopePrototypeDigitalDiagnosticCode::DirectMaskHasUnknownOutputBits
        );
    }

    {
        SenscopePrototypeForceRequest request = {};
        request.active_physical_button_mask = kExampleFixedForceRuleTriggerMask;
        request.post_socd_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D5);
        const SenscopePrototypeForceResult force_result =
            ResolveSenscopePrototypeProfileForceOverride(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ForceFixedRuleResolvesCoordinateAndB,
            force_result.status == SenscopePrototypeForceStatus::Resolved &&
                force_result.matched &&
                CoordEquals(force_result.left_stick_raw_coordinate, 128, 228) &&
                force_result.digital_output_contribution == kSenscopePrototypeOutputB
        );
    }

    {
        SenscopePrototypeForceRequest request = {};
        request.active_physical_button_mask = kExampleHorizontalForceRuleTriggerMask;
        request.post_socd_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D7);
        const SenscopePrototypeForceResult force_result =
            ResolveSenscopePrototypeProfileForceOverride(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ForceUpwardHorizontalRuleResolvesLeftXAndForcedY,
            force_result.status == SenscopePrototypeForceStatus::Resolved &&
                force_result.matched &&
                force_result.left_stick_raw_coordinate.x ==
                    kSenscopePrototypeForceHorizontalPlaceholderLeftX &&
                force_result.left_stick_raw_coordinate.y == 228 &&
                force_result.digital_output_contribution == kSenscopePrototypeOutputB
        );
    }

    {
        SenscopePrototypeForceOverrideRulesArray modified_force_rules = example_profile.force_override_rules;
        modified_force_rules[2] = modified_force_rules[0];
        modified_force_rules[2].enabled = true;

        SenscopePrototypeForceRequest request = {};
        request.active_physical_button_mask = kExampleFixedForceRuleTriggerMask;
        request.post_socd_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D5);
        const SenscopePrototypeForceResult force_result =
            ResolveSenscopePrototypeForceOverride(modified_force_rules, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::ForceEqualPriorityAmbiguityDetected,
            force_result.status == SenscopePrototypeForceStatus::AmbiguousHighestPriorityMatch &&
                force_result.matched &&
                force_result.diagnostic_code ==
                    SenscopePrototypeForceDiagnosticCode::EqualPriorityRuleAmbiguity
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.active_physical_button_mask = kExampleFixedForceRuleTriggerMask;
        request.direct_digital_output_mask = kSenscopePrototypeOutputA;
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        const SenscopePrototypeDigitalOutputMask expected_output_mask =
            kSenscopePrototypeOutputA | kSenscopePrototypeOutputB;
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionForceWins,
            output_result.status == SenscopePrototypeOutputStatus::Composed &&
                output_result.output_packet.has_force_override &&
                output_result.output_packet.has_left_stick &&
                !output_result.output_packet.used_table_resolver &&
                CoordEquals(output_result.output_packet.left_stick_raw_coordinate, 128, 228) &&
                (output_result.output_packet.digital_output_mask & expected_output_mask) ==
                    expected_output_mask
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.active_physical_button_mask = kExampleFixedForceRuleTriggerMask;
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionForceSkipsTableResolver,
            output_result.status == SenscopePrototypeOutputStatus::Composed &&
                output_result.output_packet.has_force_override &&
                !output_result.output_packet.used_table_resolver
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.active_physical_button_mask = kExampleDigitalRuleTriggerMask;
        request.direct_digital_output_mask = kSenscopePrototypeOutputA;
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft | kSenscopePrototypeDirectionRoleUp;
        request.active_modifier_mask = kExampleModifierMask001;
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionTableResolverUsedWhenNoForce,
            output_result.status == SenscopePrototypeOutputStatus::Composed &&
                !output_result.output_packet.has_force_override &&
                output_result.output_packet.used_table_resolver &&
                output_result.output_packet.used_digital_composition &&
                CoordEquals(output_result.output_packet.left_stick_raw_coordinate, 44, 212) &&
                output_result.digital_result.status == SenscopePrototypeDigitalStatus::Composed
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.direct_digital_output_mask = kUnknownDigitalOutputBit;
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionDigitalFailurePropagates,
            output_result.status == SenscopePrototypeOutputStatus::DigitalFailed &&
                output_result.diagnostic_code ==
                    SenscopePrototypeOutputDiagnosticCode::DigitalInvalidDirectOutputMask
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft | static_cast<SenscopePrototypeDirectionRoleMask>(1u << 7);
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionDirectionFailurePropagates,
            output_result.status == SenscopePrototypeOutputStatus::DirectionFailed &&
                output_result.diagnostic_code ==
                    SenscopePrototypeOutputDiagnosticCode::DirectionUnknownRoleBitsMasked
        );
    }

    {
        SenscopePrototypeOutputRequest request = {};
        request.pre_socd_direction_roles =
            kSenscopePrototypeDirectionRoleLeft | kSenscopePrototypeDirectionRoleUp;
        request.active_modifier_mask = kUndefinedExactModifierMask010;
        request.resolver_fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile;
        const SenscopePrototypeOutputResult output_result =
            ComposeSenscopePrototypeOutput(example_profile, request);
        AddSelfTestCaseResult(
            result,
            SenscopePrototypeSelfTestCaseId::OutputCompositionNoLeftStickWhenNoMatchingCombo,
            output_result.status == SenscopePrototypeOutputStatus::NoLeftStickOutput &&
                output_result.diagnostic_code ==
                    SenscopePrototypeOutputDiagnosticCode::TableResolverNoMatchingComboProfile &&
                output_result.resolver_result.status ==
                    SenscopePrototypeResolverStatus::NoMatchingComboProfile &&
                output_result.resolver_result.diagnostic_code ==
                    SenscopePrototypeResolverDiagnosticCode::ExactMatchRequiredButNotFound
        );
    }

    result.status = result.failed_case_count == 0 ? SenscopePrototypeSelfTestStatus::Passed
                                                   : SenscopePrototypeSelfTestStatus::Failed;
    return result;
}

} // namespace senscope::prototype
