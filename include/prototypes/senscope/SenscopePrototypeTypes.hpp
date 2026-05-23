#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_TYPES_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_TYPES_HPP

#include <array>
#include <cstddef>
#include <cstdint>
#include <tuple>

namespace senscope::prototype {

constexpr std::size_t kSenscopePrototypeDirectionEntryCount = 9;
constexpr std::size_t kSenscopePrototypeDirectionFiveIndex = 4;
constexpr std::size_t kSenscopePrototypeModifierRoleCount = 3;

// Conservative scaffold-only maxima for G11a. These are intentionally non-final.
constexpr std::size_t kSenscopePrototypeMaxComboProfiles = 8;
constexpr std::size_t kSenscopePrototypeMaxLeftStickTables = 8;
constexpr std::size_t kSenscopePrototypeMaxForceOverrideRules = 4;
constexpr std::size_t kSenscopePrototypeMaxDigitalMultiOutputRules = 4;
constexpr std::size_t kSenscopePrototypeMaxLayerRoleMaps = 4;
constexpr std::size_t kSenscopePrototypeMaxValidationDiagnostics = 32;

struct SenscopePrototypeRawCoord {
    uint8_t x = 128;
    uint8_t y = 128;
};

enum class SenscopePrototypeDirectionKey : uint8_t {
    D1 = 1,
    D2 = 2,
    D3 = 3,
    D4 = 4,
    D5 = 5,
    D6 = 6,
    D7 = 7,
    D8 = 8,
    D9 = 9,
};

using SenscopePrototypeDigitalOutputMask = uint32_t;
using SenscopePrototypePhysicalButtonMask = uint64_t;
using SenscopePrototypeLogicalRoleMask = uint64_t;
using SenscopePrototypeDirectionRoleMask = uint8_t;
using SenscopePrototypeModifierId = uint8_t;
using SenscopePrototypeModifierCombinationMask = uint8_t;

constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputA = 1u << 0;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputB = 1u << 1;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputX = 1u << 2;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputY = 1u << 3;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputL = 1u << 4;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputR = 1u << 5;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputZL = 1u << 6;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputZR = 1u << 7;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputStart = 1u << 8;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputDpadUp = 1u << 9;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputDpadDown = 1u << 10;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputDpadLeft = 1u << 11;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeOutputDpadRight = 1u << 12;
constexpr SenscopePrototypeDigitalOutputMask kSenscopePrototypeKnownDigitalOutputsMask =
    kSenscopePrototypeOutputA |
    kSenscopePrototypeOutputB |
    kSenscopePrototypeOutputX |
    kSenscopePrototypeOutputY |
    kSenscopePrototypeOutputL |
    kSenscopePrototypeOutputR |
    kSenscopePrototypeOutputZL |
    kSenscopePrototypeOutputZR |
    kSenscopePrototypeOutputStart |
    kSenscopePrototypeOutputDpadUp |
    kSenscopePrototypeOutputDpadDown |
    kSenscopePrototypeOutputDpadLeft |
    kSenscopePrototypeOutputDpadRight;

constexpr SenscopePrototypeDirectionRoleMask kSenscopePrototypeDirectionRoleLeft = 1u << 0;
constexpr SenscopePrototypeDirectionRoleMask kSenscopePrototypeDirectionRoleRight = 1u << 1;
constexpr SenscopePrototypeDirectionRoleMask kSenscopePrototypeDirectionRoleDown = 1u << 2;
constexpr SenscopePrototypeDirectionRoleMask kSenscopePrototypeDirectionRoleUp = 1u << 3;

constexpr SenscopePrototypeLogicalRoleMask kSenscopePrototypeLogicalRoleLayerModeHeld = 1ull << 0;

struct SenscopePrototypeComboProfile {
    bool enabled = false;
    SenscopePrototypeModifierCombinationMask modifiers = 0;
    uint8_t priority = 0;
    uint8_t left_stick_table_index = 0;
};

using SenscopePrototypeComboProfilesArray =
    std::array<SenscopePrototypeComboProfile, kSenscopePrototypeMaxComboProfiles>;

struct SenscopePrototypeDirectionalStickTable9 {
    bool enabled = false;
    std::array<bool, kSenscopePrototypeDirectionEntryCount> entry_present = {};
    std::array<SenscopePrototypeRawCoord, kSenscopePrototypeDirectionEntryCount> entries = {};
};

using SenscopePrototypeLeftStickTablesArray =
    std::array<SenscopePrototypeDirectionalStickTable9, kSenscopePrototypeMaxLeftStickTables>;

enum class SenscopePrototypeForceUpBForm : uint8_t {
    FixedExactCoordinate = 0,
    ForcedUpwardYWithPostSocdHorizontalX = 1,
};

struct SenscopePrototypeForceStickOverrideRule {
    bool enabled = false;
    SenscopePrototypePhysicalButtonMask trigger_mask = 0;
    uint8_t priority = 0;
    SenscopePrototypeForceUpBForm form = SenscopePrototypeForceUpBForm::FixedExactCoordinate;
    SenscopePrototypeRawCoord fixed_coordinate = {};
    uint8_t forced_upward_y = 128;
    bool use_post_socd_horizontal_x = false;
    SenscopePrototypeDigitalOutputMask digital_outputs = 0;
};

using SenscopePrototypeForceOverrideRulesArray =
    std::array<SenscopePrototypeForceStickOverrideRule, kSenscopePrototypeMaxForceOverrideRules>;

struct SenscopePrototypeDigitalMultiOutputRule {
    bool enabled = false;
    SenscopePrototypePhysicalButtonMask condition_mask = 0;
    SenscopePrototypeDigitalOutputMask outputs = 0;
};

using SenscopePrototypeDigitalMultiOutputRulesArray =
    std::array<SenscopePrototypeDigitalMultiOutputRule, kSenscopePrototypeMaxDigitalMultiOutputRules>;

struct SenscopePrototypeLayerRoleMap {
    bool enabled = false;
    SenscopePrototypePhysicalButtonMask held_condition_mask = 0;
    SenscopePrototypeLogicalRoleMask role_outputs = 0;
    SenscopePrototypeDirectionRoleMask direction_outputs = 0;
};

using SenscopePrototypeLayerRoleMapsArray =
    std::array<SenscopePrototypeLayerRoleMap, kSenscopePrototypeMaxLayerRoleMaps>;

struct SenscopePrototypeProfile {
    const char *mode_name = "SenscopePrototype";
    bool left_stick_only = true;
    uint8_t modifier_role_count = kSenscopePrototypeModifierRoleCount;
    SenscopePrototypeComboProfilesArray combo_profiles = {};
    SenscopePrototypeLeftStickTablesArray left_stick_tables = {};
    SenscopePrototypeForceOverrideRulesArray force_override_rules = {};
    SenscopePrototypeDigitalMultiOutputRulesArray digital_multi_output_rules = {};
    SenscopePrototypeLayerRoleMapsArray layer_role_maps = {};
};

enum class SenscopePrototypeValidationSeverity : uint8_t {
    Error = 0,
    Todo = 1,
    Unknown = 2,
};

enum class SenscopePrototypeValidationCode : uint8_t {
    None = 0,
    ModifierRoleCountMismatch,
    LeftStickOnlyFlagDisabled,
    ModifierMaskOutOfRange,
    ComboTableIndexOutOfRange,
    ComboTableNotEnabled,
    ComboExactDuplicateSamePriority,
    ComboExactDuplicateDifferentPriority,
    EqualPriorityComboSubsetAmbiguity,
    UndefinedComboFallbackUnknownReachability,
    ForceRuleEmptyTriggerMask,
    ForceRuleMissingDigitalOutputs,
    ForceRuleInvalidHorizontalPolicy,
    EqualPrioritySameTargetForceRuleConflict,
    DigitalRuleEmptyConditionMask,
    DigitalRuleEmptyOutputs,
    DigitalRuleUnknownOutputBit,
    LayerRoleMapEmptyHeldCondition,
    LayerRoleMapNoRoleOutputs,
    DirectionTableEmpty,
};

struct SenscopePrototypeValidationDiagnostic {
    SenscopePrototypeValidationSeverity severity = SenscopePrototypeValidationSeverity::Error;
    SenscopePrototypeValidationCode code = SenscopePrototypeValidationCode::None;
    uint8_t index_a = 0;
    uint8_t index_b = 0;
    uint16_t detail = 0;
};

struct SenscopePrototypeValidationResult {
    bool is_valid = true;
    bool has_todo_or_unknown = false;
    std::size_t diagnostic_count = 0;
    std::array<SenscopePrototypeValidationDiagnostic, kSenscopePrototypeMaxValidationDiagnostics> diagnostics = {};
};

const SenscopePrototypeProfile &GetSenscopePrototypeExampleProfile();
SenscopePrototypeValidationResult
ValidateSenscopePrototypeProfile(const SenscopePrototypeProfile &profile) noexcept;

static_assert(kSenscopePrototypeDirectionEntryCount == 9, "G11a prototype direction count must be 9.");
static_assert(kSenscopePrototypeModifierRoleCount == 3, "G11a prototype modifier-role count must be 3.");
static_assert(
    sizeof(SenscopePrototypeModifierCombinationMask) * 8u >= kSenscopePrototypeModifierRoleCount,
    "Modifier combination mask must cover all prototype modifier roles."
);
static_assert(
    std::tuple_size<SenscopePrototypeComboProfilesArray>::value == kSenscopePrototypeMaxComboProfiles,
    "Combo profile table size mismatch."
);
static_assert(
    std::tuple_size<SenscopePrototypeLeftStickTablesArray>::value == kSenscopePrototypeMaxLeftStickTables,
    "Left-stick table size mismatch."
);
static_assert(
    std::tuple_size<SenscopePrototypeForceOverrideRulesArray>::value == kSenscopePrototypeMaxForceOverrideRules,
    "Force-override table size mismatch."
);
static_assert(
    std::tuple_size<SenscopePrototypeDigitalMultiOutputRulesArray>::value ==
        kSenscopePrototypeMaxDigitalMultiOutputRules,
    "Digital multi-output table size mismatch."
);
static_assert(
    std::tuple_size<SenscopePrototypeLayerRoleMapsArray>::value == kSenscopePrototypeMaxLayerRoleMaps,
    "Layer-role map table size mismatch."
);

} // namespace senscope::prototype

#endif
