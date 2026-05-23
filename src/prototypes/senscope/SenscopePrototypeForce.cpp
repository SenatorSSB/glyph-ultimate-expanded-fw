#include "prototypes/senscope/SenscopePrototypeForce.hpp"

namespace senscope::prototype {

namespace {

enum class SenscopePrototypeHorizontalDirection : uint8_t {
    Left = 0,
    Neutral,
    Right,
};

bool IsDirectionKeyValid(uint8_t direction_key) {
    return direction_key >= static_cast<uint8_t>(SenscopePrototypeDirectionKey::D1) &&
           direction_key <= static_cast<uint8_t>(SenscopePrototypeDirectionKey::D9);
}

bool TryResolveHorizontalDirection(
    uint8_t direction_key,
    SenscopePrototypeHorizontalDirection &horizontal_direction
) {
    if (!IsDirectionKeyValid(direction_key)) {
        return false;
    }

    switch (static_cast<SenscopePrototypeDirectionKey>(direction_key)) {
        case SenscopePrototypeDirectionKey::D1:
        case SenscopePrototypeDirectionKey::D4:
        case SenscopePrototypeDirectionKey::D7:
            horizontal_direction = SenscopePrototypeHorizontalDirection::Left;
            return true;

        case SenscopePrototypeDirectionKey::D2:
        case SenscopePrototypeDirectionKey::D5:
        case SenscopePrototypeDirectionKey::D8:
            horizontal_direction = SenscopePrototypeHorizontalDirection::Neutral;
            return true;

        case SenscopePrototypeDirectionKey::D3:
        case SenscopePrototypeDirectionKey::D6:
        case SenscopePrototypeDirectionKey::D9:
            horizontal_direction = SenscopePrototypeHorizontalDirection::Right;
            return true;

        default:
            return false;
    }
}

uint8_t ResolveHorizontalX(
    const SenscopePrototypeForceHorizontalXChoices &choices,
    SenscopePrototypeHorizontalDirection horizontal_direction
) {
    const uint8_t left_x = choices.use_custom_values ? choices.left_x
                                                     : kSenscopePrototypeForceHorizontalPlaceholderLeftX;
    const uint8_t neutral_x = choices.use_custom_values ? choices.neutral_x
                                                        : kSenscopePrototypeForceHorizontalPlaceholderNeutralX;
    const uint8_t right_x = choices.use_custom_values ? choices.right_x
                                                      : kSenscopePrototypeForceHorizontalPlaceholderRightX;

    switch (horizontal_direction) {
        case SenscopePrototypeHorizontalDirection::Left:
            return left_x;
        case SenscopePrototypeHorizontalDirection::Right:
            return right_x;
        case SenscopePrototypeHorizontalDirection::Neutral:
        default:
            return neutral_x;
    }
}

bool IsRuleTriggered(
    SenscopePrototypePhysicalButtonMask active_buttons,
    const SenscopePrototypeForceStickOverrideRule &rule
) {
    return rule.enabled && rule.trigger_mask != 0 && (active_buttons & rule.trigger_mask) == rule.trigger_mask;
}

} // namespace

SenscopePrototypeForceResult ResolveSenscopePrototypeForceOverride(
    const SenscopePrototypeForceOverrideRulesArray &force_rules,
    const SenscopePrototypeForceRequest &request
) noexcept {
    SenscopePrototypeForceResult result = {};

    bool found_match = false;
    bool ambiguous_match = false;
    uint8_t best_priority = 0;

    for (std::size_t i = 0; i < force_rules.size(); i++) {
        const SenscopePrototypeForceStickOverrideRule &rule = force_rules[i];
        if (!IsRuleTriggered(request.active_physical_button_mask, rule)) {
            continue;
        }

        if (!found_match || rule.priority > best_priority) {
            found_match = true;
            ambiguous_match = false;
            best_priority = rule.priority;
            result.selected_rule_index = static_cast<uint8_t>(i);
            continue;
        }

        if (rule.priority == best_priority) {
            ambiguous_match = true;
        }
    }

    if (!found_match) {
        result.status = SenscopePrototypeForceStatus::NoMatchingRule;
        result.matched = false;
        result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::NoMatchingRule;
        return result;
    }

    if (ambiguous_match) {
        result.status = SenscopePrototypeForceStatus::AmbiguousHighestPriorityMatch;
        result.matched = true;
        result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::EqualPriorityRuleAmbiguity;
        result.diagnostic_detail = best_priority;
        return result;
    }

    const SenscopePrototypeForceStickOverrideRule &selected_rule = force_rules[result.selected_rule_index];
    const SenscopePrototypeDigitalOutputMask unknown_output_bits =
        selected_rule.digital_outputs & ~kSenscopePrototypeKnownDigitalOutputsMask;

    result.matched = true;
    result.digital_output_contribution =
        selected_rule.digital_outputs & kSenscopePrototypeKnownDigitalOutputsMask;

    if (unknown_output_bits != 0) {
        result.status = SenscopePrototypeForceStatus::InvalidRuleDigitalOutputs;
        result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::RuleHasUnknownDigitalOutputBits;
        result.diagnostic_detail = static_cast<uint16_t>(unknown_output_bits);
        return result;
    }

    switch (selected_rule.form) {
        case SenscopePrototypeForceUpBForm::FixedExactCoordinate:
            result.left_stick_raw_coordinate = selected_rule.fixed_coordinate;
            result.status = SenscopePrototypeForceStatus::Resolved;
            result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::None;
            return result;

        case SenscopePrototypeForceUpBForm::ForcedUpwardYWithPostSocdHorizontalX: {
            if (!selected_rule.use_post_socd_horizontal_x) {
                result.status = SenscopePrototypeForceStatus::InvalidRuleHorizontalPolicy;
                result.diagnostic_code =
                    SenscopePrototypeForceDiagnosticCode::RuleRequiresPostSocdHorizontalPolicy;
                return result;
            }

            SenscopePrototypeHorizontalDirection horizontal_direction =
                SenscopePrototypeHorizontalDirection::Neutral;
            if (!TryResolveHorizontalDirection(request.post_socd_direction_key, horizontal_direction)) {
                result.status = SenscopePrototypeForceStatus::InvalidDirectionKey;
                result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::DirectionKeyOutOfRange;
                result.diagnostic_detail = request.post_socd_direction_key;
                return result;
            }

            result.left_stick_raw_coordinate.x =
                ResolveHorizontalX(request.horizontal_x_choices, horizontal_direction);
            result.left_stick_raw_coordinate.y = selected_rule.forced_upward_y;
            result.status = SenscopePrototypeForceStatus::Resolved;
            result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::None;
            return result;
        }

        default:
            result.status = SenscopePrototypeForceStatus::UnsupportedRuleForm;
            result.diagnostic_code = SenscopePrototypeForceDiagnosticCode::RuleFormUnsupported;
            result.diagnostic_detail = static_cast<uint16_t>(selected_rule.form);
            return result;
    }
}

SenscopePrototypeForceResult ResolveSenscopePrototypeProfileForceOverride(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeForceRequest &request
) noexcept {
    return ResolveSenscopePrototypeForceOverride(profile.force_override_rules, request);
}

} // namespace senscope::prototype
