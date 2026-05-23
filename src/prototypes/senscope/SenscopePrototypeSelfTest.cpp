#include "prototypes/senscope/SenscopePrototypeSelfTest.hpp"

#include "prototypes/senscope/SenscopePrototypeDigital.hpp"
#include "prototypes/senscope/SenscopePrototypeDirection.hpp"
#include "prototypes/senscope/SenscopePrototypeForce.hpp"
#include "prototypes/senscope/SenscopePrototypeResolver.hpp"
#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

namespace senscope::prototype {

namespace {

constexpr SenscopePrototypePhysicalButtonMask kExampleDigitalRuleTriggerMask = 1ull << 42;
constexpr SenscopePrototypePhysicalButtonMask kExampleFixedForceRuleTriggerMask = 1ull << 40;
constexpr SenscopePrototypePhysicalButtonMask kExampleHorizontalForceRuleTriggerMask = 1ull << 41;
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

    result.status = result.failed_case_count == 0 ? SenscopePrototypeSelfTestStatus::Passed
                                                   : SenscopePrototypeSelfTestStatus::Failed;
    return result;
}

} // namespace senscope::prototype
