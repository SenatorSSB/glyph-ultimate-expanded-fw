#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_MODIFIER_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_MODIFIER_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <array>
#include <cstddef>
#include <cstdint>

namespace senscope::prototype {

constexpr std::size_t kSenscopePrototypeMaxModifierBindings = 8;
constexpr uint8_t kSenscopePrototypeModifierInvalidBindingIndex = 0xFF;

enum class SenscopePrototypeModifierStatus : uint8_t {
    Resolved = 0,
    InvalidBinding,
};

enum class SenscopePrototypeModifierDiagnosticCode : uint8_t {
    None = 0,
    BindingModifierBitIndexOutOfRange,
    BindingPhysicalButtonMaskEmpty,
};

struct SenscopePrototypeModifierBinding {
    bool enabled = false;
    SenscopePrototypePhysicalButtonMask physical_button_mask = 0;
    uint8_t modifier_bit_index = 0;
};

using SenscopePrototypeModifierBindingsArray =
    std::array<SenscopePrototypeModifierBinding, kSenscopePrototypeMaxModifierBindings>;

struct SenscopePrototypeModifierRequest {
    SenscopePrototypePhysicalButtonMask active_physical_button_mask = 0;
    SenscopePrototypeModifierBindingsArray bindings = {};
};

struct SenscopePrototypeModifierResult {
    SenscopePrototypeModifierStatus status = SenscopePrototypeModifierStatus::Resolved;
    SenscopePrototypeModifierCombinationMask active_modifier_mask = 0;
    std::size_t triggered_binding_count = 0;
    uint8_t diagnostic_binding_index = kSenscopePrototypeModifierInvalidBindingIndex;
    SenscopePrototypeModifierDiagnosticCode diagnostic_code =
        SenscopePrototypeModifierDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
};

SenscopePrototypeModifierResult
BuildSenscopePrototypeActiveModifierMask(const SenscopePrototypeModifierRequest &request) noexcept;

} // namespace senscope::prototype

#endif
