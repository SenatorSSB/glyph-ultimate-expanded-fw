#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_DIGITAL_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_DIGITAL_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <cstddef>
#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeDigitalStatus : uint8_t {
    Composed = 0,
    InvalidDirectOutputMask,
    InvalidRuleOutputMask,
};

enum class SenscopePrototypeDigitalDiagnosticCode : uint8_t {
    None = 0,
    DirectMaskHasUnknownOutputBits,
    RuleMaskHasUnknownOutputBits,
};

struct SenscopePrototypeDigitalRequest {
    SenscopePrototypeDigitalOutputMask direct_digital_output_mask = 0;
    SenscopePrototypePhysicalButtonMask active_physical_button_mask = 0;
};

struct SenscopePrototypeDigitalResult {
    SenscopePrototypeDigitalStatus status = SenscopePrototypeDigitalStatus::Composed;
    SenscopePrototypeDigitalOutputMask composed_digital_output_mask = 0;
    std::size_t triggered_rule_count = 0;
    uint8_t diagnostic_rule_index = 0xFF;
    SenscopePrototypeDigitalDiagnosticCode diagnostic_code =
        SenscopePrototypeDigitalDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
};

SenscopePrototypeDigitalResult ComposeSenscopePrototypeDigitalOutputs(
    const SenscopePrototypeDigitalMultiOutputRulesArray &digital_rules,
    const SenscopePrototypeDigitalRequest &request
) noexcept;

SenscopePrototypeDigitalResult ComposeSenscopePrototypeProfileDigitalOutputs(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeDigitalRequest &request
) noexcept;

} // namespace senscope::prototype

#endif
