#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_FORCE_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_FORCE_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeForceStatus : uint8_t {
    NoMatchingRule = 0,
    Resolved,
    AmbiguousHighestPriorityMatch,
    InvalidDirectionKey,
    InvalidRuleDigitalOutputs,
    InvalidRuleHorizontalPolicy,
    UnsupportedRuleForm,
};

enum class SenscopePrototypeForceDiagnosticCode : uint8_t {
    None = 0,
    NoMatchingRule,
    EqualPriorityRuleAmbiguity,
    DirectionKeyOutOfRange,
    RuleHasUnknownDigitalOutputBits,
    RuleRequiresPostSocdHorizontalPolicy,
    RuleFormUnsupported,
};

constexpr uint8_t kSenscopePrototypeForceInvalidRuleIndex = 0xFF;

// Prototype placeholder constants only. These are conservative helper values and
// are not gameplay-semantic claims.
constexpr uint8_t kSenscopePrototypeForceHorizontalPlaceholderLeftX = 96;
constexpr uint8_t kSenscopePrototypeForceHorizontalPlaceholderNeutralX = 128;
constexpr uint8_t kSenscopePrototypeForceHorizontalPlaceholderRightX = 160;

struct SenscopePrototypeForceHorizontalXChoices {
    bool use_custom_values = false;
    uint8_t left_x = kSenscopePrototypeForceHorizontalPlaceholderLeftX;
    uint8_t neutral_x = kSenscopePrototypeForceHorizontalPlaceholderNeutralX;
    uint8_t right_x = kSenscopePrototypeForceHorizontalPlaceholderRightX;
};

struct SenscopePrototypeForceRequest {
    SenscopePrototypePhysicalButtonMask active_physical_button_mask = 0;
    uint8_t post_socd_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D5);
    SenscopePrototypeForceHorizontalXChoices horizontal_x_choices = {};
};

struct SenscopePrototypeForceResult {
    SenscopePrototypeForceStatus status = SenscopePrototypeForceStatus::NoMatchingRule;
    bool matched = false;
    uint8_t selected_rule_index = kSenscopePrototypeForceInvalidRuleIndex;
    SenscopePrototypeRawCoord left_stick_raw_coordinate = {};
    SenscopePrototypeDigitalOutputMask digital_output_contribution = 0;
    SenscopePrototypeForceDiagnosticCode diagnostic_code =
        SenscopePrototypeForceDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
};

SenscopePrototypeForceResult ResolveSenscopePrototypeForceOverride(
    const SenscopePrototypeForceOverrideRulesArray &force_rules,
    const SenscopePrototypeForceRequest &request
) noexcept;

SenscopePrototypeForceResult ResolveSenscopePrototypeProfileForceOverride(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeForceRequest &request
) noexcept;

} // namespace senscope::prototype

#endif
