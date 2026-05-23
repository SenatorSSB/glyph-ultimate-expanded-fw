#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_RESOLVER_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_RESOLVER_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeResolverStatus : uint8_t {
    Resolved = 0,
    ProfileInvalid,
    NoMatchingComboProfile,
    AmbiguousComboProfile,
    ComboTableIndexOutOfRange,
    TableDisabled,
    MissingDirectionEntry,
    InvalidDirectionKey,
};

enum class SenscopePrototypeResolverDiagnosticCode : uint8_t {
    None = 0,
    ProfileValidationFailed,
    ExactMatchRequiredButNotFound,
    ExactComboPriorityAmbiguity,
    SubsetComboPriorityAmbiguity,
    SubsetFallbackNotFound,
    ComboIndexOutOfRange,
    TableIndexOutOfRange,
    TableDisabled,
    DirectionEntryMissing,
    DirectionKeyOutOfRange,
};

enum class SenscopePrototypeResolverFallbackPolicy : uint8_t {
    RequireExactComboProfile = 0,
    AllowHighestPrioritySubset = 1,
};

constexpr uint8_t kSenscopePrototypeResolverInvalidIndex = 0xFF;

struct SenscopePrototypeResolverRequest {
    SenscopePrototypeModifierCombinationMask active_modifier_mask = 0;
    uint8_t resolved_direction_key = static_cast<uint8_t>(SenscopePrototypeDirectionKey::D5);
    SenscopePrototypeResolverFallbackPolicy fallback_policy =
        SenscopePrototypeResolverFallbackPolicy::AllowHighestPrioritySubset;
};

struct SenscopePrototypeResolverResult {
    SenscopePrototypeResolverStatus status = SenscopePrototypeResolverStatus::NoMatchingComboProfile;
    SenscopePrototypeRawCoord raw_coordinate = {};
    uint8_t selected_combo_profile_index = kSenscopePrototypeResolverInvalidIndex;
    uint8_t selected_left_stick_table_index = kSenscopePrototypeResolverInvalidIndex;
    SenscopePrototypeResolverDiagnosticCode diagnostic_code = SenscopePrototypeResolverDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
};

SenscopePrototypeResolverResult ResolveSenscopePrototypeLeftStickRawCoordinate(
    const SenscopePrototypeProfile &profile,
    const SenscopePrototypeResolverRequest &request
) noexcept;

SenscopePrototypeResolverResult
ResolveSenscopePrototypeExampleLeftStickRawCoordinate(const SenscopePrototypeResolverRequest &request) noexcept;

} // namespace senscope::prototype

#endif
