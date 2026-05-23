#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_OUTPUT_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_OUTPUT_HPP

#include "prototypes/senscope/SenscopePrototypeDigital.hpp"
#include "prototypes/senscope/SenscopePrototypeDirection.hpp"
#include "prototypes/senscope/SenscopePrototypeForce.hpp"
#include "prototypes/senscope/SenscopePrototypeResolver.hpp"
#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeOutputStatus : uint8_t {
    Composed = 0,
    DirectionFailed,
    ForceFailed,
    DigitalFailed,
    TableResolverFailed,
    NoLeftStickOutput,
};

enum class SenscopePrototypeOutputDiagnosticCode : uint8_t {
    None = 0,
    DirectionUnknownRoleBitsMasked,
    ForceAmbiguousHighestPriorityMatch,
    ForceInvalidDirectionKey,
    ForceInvalidRuleDigitalOutputs,
    ForceInvalidRuleHorizontalPolicy,
    ForceUnsupportedRuleForm,
    DigitalInvalidDirectOutputMask,
    DigitalInvalidRuleOutputMask,
    TableResolverNoMatchingComboProfile,
    TableResolverProfileInvalid,
    TableResolverAmbiguousComboProfile,
    TableResolverComboTableIndexOutOfRange,
    TableResolverTableDisabled,
    TableResolverMissingDirectionEntry,
    TableResolverInvalidDirectionKey,
};

constexpr uint8_t kSenscopePrototypeOutputInvalidIndex = 0xFF;

struct SenscopePrototypeOutputRequest {
    SenscopePrototypePhysicalButtonMask active_physical_button_mask = 0;
    SenscopePrototypeDigitalOutputMask direct_digital_output_mask = 0;
    SenscopePrototypeDirectionRoleMask pre_socd_direction_roles = 0;
    SenscopePrototypeDirectionOppositePolicy direction_opposite_policy =
        SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
    SenscopePrototypeModifierCombinationMask active_modifier_mask = 0;
    SenscopePrototypeResolverFallbackPolicy resolver_fallback_policy =
        SenscopePrototypeResolverFallbackPolicy::AllowHighestPrioritySubset;
    SenscopePrototypeForceHorizontalXChoices force_horizontal_x_choices = {};
};

struct SenscopePrototypeOutputPacket {
    SenscopePrototypeRawCoord left_stick_raw_coordinate = {};
    SenscopePrototypeDigitalOutputMask digital_output_mask = 0;
    bool has_left_stick = false;
    bool has_force_override = false;
    bool used_table_resolver = false;
    bool used_digital_composition = false;
    uint8_t selected_force_rule_index = kSenscopePrototypeOutputInvalidIndex;
    uint8_t selected_combo_profile_index = kSenscopePrototypeOutputInvalidIndex;
    uint8_t selected_left_stick_table_index = kSenscopePrototypeOutputInvalidIndex;
    SenscopePrototypeDirectionKey resolved_direction_key = SenscopePrototypeDirectionKey::D5;
    SenscopePrototypeDirectionRoleMask post_socd_direction_roles = 0;
};

struct SenscopePrototypeOutputResult {
    SenscopePrototypeOutputStatus status = SenscopePrototypeOutputStatus::NoLeftStickOutput;
    SenscopePrototypeOutputDiagnosticCode diagnostic_code =
        SenscopePrototypeOutputDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
    SenscopePrototypeOutputPacket output_packet = {};

    SenscopePrototypeDirectionResult direction_result = {};
    SenscopePrototypeForceResult force_result = {};
    SenscopePrototypeDigitalResult digital_result = {};
    SenscopePrototypeResolverResult resolver_result = {};
};

SenscopePrototypeOutputResult ComposeSenscopePrototypeOutput(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeOutputRequest &request
) noexcept;

SenscopePrototypeOutputResult
ComposeSenscopePrototypeExampleOutput(const SenscopePrototypeOutputRequest &request) noexcept;

} // namespace senscope::prototype

#endif
