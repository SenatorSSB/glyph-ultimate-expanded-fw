#include "prototypes/senscope/SenscopePrototypeModifier.hpp"

namespace senscope::prototype {

namespace {

bool IsBindingTriggered(
    SenscopePrototypePhysicalButtonMask active_physical_button_mask,
    const SenscopePrototypeModifierBinding &binding
) {
    return binding.physical_button_mask != 0 &&
           (active_physical_button_mask & binding.physical_button_mask) == binding.physical_button_mask;
}

} // namespace

SenscopePrototypeModifierResult
BuildSenscopePrototypeActiveModifierMask(const SenscopePrototypeModifierRequest &request) noexcept {
    SenscopePrototypeModifierResult result = {};

    for (std::size_t i = 0; i < request.bindings.size(); i++) {
        const SenscopePrototypeModifierBinding &binding = request.bindings[i];
        if (!binding.enabled) {
            continue;
        }

        if (binding.modifier_bit_index >= kSenscopePrototypeModifierRoleCount) {
            result.status = SenscopePrototypeModifierStatus::InvalidBinding;
            result.diagnostic_binding_index = static_cast<uint8_t>(i);
            result.diagnostic_code =
                SenscopePrototypeModifierDiagnosticCode::BindingModifierBitIndexOutOfRange;
            result.diagnostic_detail = binding.modifier_bit_index;
            return result;
        }

        if (binding.physical_button_mask == 0) {
            result.status = SenscopePrototypeModifierStatus::InvalidBinding;
            result.diagnostic_binding_index = static_cast<uint8_t>(i);
            result.diagnostic_code = SenscopePrototypeModifierDiagnosticCode::BindingPhysicalButtonMaskEmpty;
            return result;
        }
    }

    for (const SenscopePrototypeModifierBinding &binding : request.bindings) {
        if (!binding.enabled) {
            continue;
        }
        if (!IsBindingTriggered(request.active_physical_button_mask, binding)) {
            continue;
        }

        result.active_modifier_mask |=
            static_cast<SenscopePrototypeModifierCombinationMask>(1u << binding.modifier_bit_index);
        result.triggered_binding_count++;
    }

    return result;
}

} // namespace senscope::prototype
