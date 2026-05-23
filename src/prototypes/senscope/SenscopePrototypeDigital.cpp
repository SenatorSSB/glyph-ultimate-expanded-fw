#include "prototypes/senscope/SenscopePrototypeDigital.hpp"

namespace senscope::prototype {

namespace {

constexpr uint8_t kSenscopePrototypeDigitalInvalidRuleIndex = 0xFF;

bool IsRuleTriggered(
    SenscopePrototypePhysicalButtonMask active_buttons,
    SenscopePrototypePhysicalButtonMask trigger_mask
) {
    return trigger_mask != 0 && (active_buttons & trigger_mask) == trigger_mask;
}

} // namespace

SenscopePrototypeDigitalResult ComposeSenscopePrototypeDigitalOutputs(
    const SenscopePrototypeDigitalMultiOutputRulesArray &digital_rules,
    const SenscopePrototypeDigitalRequest &request
) noexcept {
    SenscopePrototypeDigitalResult result = {};
    result.diagnostic_rule_index = kSenscopePrototypeDigitalInvalidRuleIndex;

    const SenscopePrototypeDigitalOutputMask direct_unknown_bits =
        request.direct_digital_output_mask & ~kSenscopePrototypeKnownDigitalOutputsMask;

    result.composed_digital_output_mask =
        request.direct_digital_output_mask & kSenscopePrototypeKnownDigitalOutputsMask;

    if (direct_unknown_bits != 0) {
        result.status = SenscopePrototypeDigitalStatus::InvalidDirectOutputMask;
        result.diagnostic_code = SenscopePrototypeDigitalDiagnosticCode::DirectMaskHasUnknownOutputBits;
        result.diagnostic_detail = static_cast<uint16_t>(direct_unknown_bits);
        return result;
    }

    for (std::size_t i = 0; i < digital_rules.size(); i++) {
        const SenscopePrototypeDigitalMultiOutputRule &rule = digital_rules[i];
        if (!rule.enabled) {
            continue;
        }
        if (!IsRuleTriggered(request.active_physical_button_mask, rule.condition_mask)) {
            continue;
        }

        const SenscopePrototypeDigitalOutputMask rule_unknown_bits =
            rule.outputs & ~kSenscopePrototypeKnownDigitalOutputsMask;
        if (rule_unknown_bits != 0) {
            result.status = SenscopePrototypeDigitalStatus::InvalidRuleOutputMask;
            result.diagnostic_rule_index = static_cast<uint8_t>(i);
            result.diagnostic_code = SenscopePrototypeDigitalDiagnosticCode::RuleMaskHasUnknownOutputBits;
            result.diagnostic_detail = static_cast<uint16_t>(rule_unknown_bits);
            return result;
        }

        // G11e scope is OR composition only; no suppression/pass-through in this helper.
        result.composed_digital_output_mask |= rule.outputs;
        result.triggered_rule_count++;
    }

    return result;
}

SenscopePrototypeDigitalResult ComposeSenscopePrototypeProfileDigitalOutputs(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeDigitalRequest &request
) noexcept {
    return ComposeSenscopePrototypeDigitalOutputs(profile.digital_multi_output_rules, request);
}

} // namespace senscope::prototype
