#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_SELFTEST_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_SELFTEST_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <array>
#include <cstddef>
#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeSelfTestStatus : uint8_t {
    Passed = 0,
    Failed,
    ProfileInvalid,
};

enum class SenscopePrototypeSelfTestCaseId : uint8_t {
    ValidationExampleProfile = 0,
    ValidationDuplicateExactComboMaskRejectedOrDiagnosed,
    ValidationDirectionFiveEntryAllowed,
    ValidationDigitalRuleUnknownOutputRejected,
    ValidationForceRuleMissingDigitalOutputRejected,
    ValidationLayerRoleMapEmptyRejected,
    ModifierNoBindingsReturnsZeroMask,
    ModifierSingleBindingSetsBit0,
    ModifierMultipleBindingsSetBits,
    ModifierDuplicateSourcesOrComposeSameBit,
    ModifierInvalidBitIndexRejected,
    ModifierEmptyBindingRejected,
    ModifierRf2Rf3Rf4BindingsPreserveBitSemantics,
    DirectionLeftDownResolvesD1,
    DirectionDownResolvesD2,
    DirectionRightDownResolvesD3,
    DirectionNeutralRoleMaskResolvesD5,
    DirectionRightResolvesD6,
    DirectionLeftUpResolvesD7,
    DirectionLeftRightUpNeutralOnOppositeResolvesD8,
    DirectionRightUpResolvesD9,
    DirectionLeftRightLeftPriorityResolvesD4,
    DirectionDownUpUpPriorityResolvesD8,
    ResolverModifier000DirectionD5ResolvesBaseNeutral,
    ResolverModifier000DirectionD6ResolvesBaseRight,
    ResolverModifier000DirectionD4ResolvesBaseLeft,
    ResolverModifier001DirectionD7ResolvesTable1,
    ResolverExactRequiredUndefinedComboNoMatch,
    ResolverSubsetFallbackDefinedSubsetResolves,
    DigitalNeutralDefaultsToNoOutputs,
    DigitalDirectAWithTriggeredByRuleComposesABY,
    DigitalUnknownDirectOutputBitDiagnostic,
    ForceNoMatchingRuleRemainsDisabled,
    ForceFixedRuleResolvesCoordinateAndB,
    ForceUpwardHorizontalRuleResolvesLeftXAndForcedY,
    ForceEqualPriorityAmbiguityDetected,
    OutputCompositionForceWins,
    OutputCompositionForceSkipsTableResolver,
    OutputCompositionTableResolverUsedWhenNoForce,
    OutputCompositionDigitalFailurePropagates,
    OutputCompositionDirectionFailurePropagates,
    OutputCompositionNoLeftStickWhenNoMatchingCombo,
    OutputCompositionNoLeftStickKeepsNeutralPacketCoordinate,
};

constexpr std::size_t kSenscopePrototypeSelfTestMaxCaseResults = 56;

struct SenscopePrototypeSelfTestCaseResult {
    SenscopePrototypeSelfTestCaseId case_id =
        SenscopePrototypeSelfTestCaseId::ValidationExampleProfile;
    bool passed = false;
};

struct SenscopePrototypeSelfTestResult {
    SenscopePrototypeSelfTestStatus status = SenscopePrototypeSelfTestStatus::Failed;
    std::size_t total_case_count = 0;
    std::size_t passed_case_count = 0;
    std::size_t failed_case_count = 0;
    std::array<SenscopePrototypeSelfTestCaseResult, kSenscopePrototypeSelfTestMaxCaseResults> case_results = {};
};

SenscopePrototypeSelfTestResult RunSenscopePrototypeSelfTest() noexcept;

} // namespace senscope::prototype

#endif
