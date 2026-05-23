#include "modes/SenscopePrototype.hpp"

#include "prototypes/senscope/SenscopePrototypeDirection.hpp"
#include "prototypes/senscope/SenscopePrototypeResolver.hpp"
#include "prototypes/senscope/SenscopePrototypeSelfTest.hpp"
#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

namespace {

constexpr uint8_t kAnalogNeutral = 128;
constexpr uint8_t kAnalogMin = 0;
constexpr uint8_t kAnalogMax = 255;
constexpr bool kRunSenscopePrototypeConstructorSelfTest = false;
constexpr senscope::prototype::SenscopePrototypeModifierCombinationMask
    kSenscopePrototypeNoActiveModifiers = 0;

senscope::prototype::SenscopePrototypeDirectionRoleMask
BuildSenscopePrototypeDirectionRoleMask(const InputState &inputs) {
    using namespace senscope::prototype;

    SenscopePrototypeDirectionRoleMask direction_roles = 0;
    if (inputs.lf3) {
        direction_roles |= kSenscopePrototypeDirectionRoleLeft;
    }
    if (inputs.lf1) {
        direction_roles |= kSenscopePrototypeDirectionRoleRight;
    }
    if (inputs.lf2) {
        direction_roles |= kSenscopePrototypeDirectionRoleDown;
    }
    if (inputs.rf4) {
        direction_roles |= kSenscopePrototypeDirectionRoleUp;
    }

    return direction_roles;
}

bool TryResolveSenscopePrototypeLeftStickCoordinate(
    const InputState &inputs,
    senscope::prototype::SenscopePrototypeRawCoord &resolved_coordinate
) {
    using namespace senscope::prototype;

    const SenscopePrototypeDirectionRequest direction_request = {
        .pre_socd_direction_roles = BuildSenscopePrototypeDirectionRoleMask(inputs),
        .opposite_policy = SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite,
    };

    const SenscopePrototypeDirectionResult direction_result =
        ResolveSenscopePrototypeDirection(direction_request);
    if (direction_result.status != SenscopePrototypeDirectionStatus::Resolved) {
        return false;
    }

    const SenscopePrototypeResolverRequest resolver_request = {
        .active_modifier_mask = kSenscopePrototypeNoActiveModifiers,
        .resolved_direction_key = static_cast<uint8_t>(direction_result.resolved_direction_key),
        .fallback_policy = SenscopePrototypeResolverFallbackPolicy::RequireExactComboProfile,
    };

    const SenscopePrototypeResolverResult resolver_result =
        ResolveSenscopePrototypeExampleLeftStickRawCoordinate(resolver_request);
    if (resolver_result.status != SenscopePrototypeResolverStatus::Resolved) {
        return false;
    }

    resolved_coordinate = resolver_result.raw_coordinate;
    return true;
}

} // namespace

SenscopePrototype::SenscopePrototype() : ControllerMode() {
    if constexpr (kRunSenscopePrototypeConstructorSelfTest) {
        // Keep self-test available for explicit debug/test bring-up paths.
        (void)RunPrototypeStaticSmokeCheck();
    }
}

bool SenscopePrototype::RunPrototypeStaticSmokeCheck() {
    const senscope::prototype::SenscopePrototypeSelfTestResult self_test_result =
        senscope::prototype::RunSenscopePrototypeSelfTest();
    return self_test_result.status == senscope::prototype::SenscopePrototypeSelfTestStatus::Passed;
}

void SenscopePrototype::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    (void)inputs;

    // G11b inert shell behavior: emit neutral digital outputs only.
    outputs.buttons = 0;
}

void SenscopePrototype::UpdateAnalogOutputs(
    const InputState &inputs,
    OutputState &outputs,
    CommunicationBackendId backend_id
) {
    (void)backend_id;

    // Keep prototype runtime scope left-stick-only; right stick and triggers stay neutral.
    UpdateDirections(
        false,
        false,
        false,
        false,
        false,
        false,
        false,
        false,
        kAnalogMin,
        kAnalogNeutral,
        kAnalogMax,
        outputs
    );
    outputs.triggerLAnalog = 0;
    outputs.triggerRAnalog = 0;

    senscope::prototype::SenscopePrototypeRawCoord resolved_coordinate = {
        .x = kAnalogNeutral,
        .y = kAnalogNeutral,
    };
    if (!TryResolveSenscopePrototypeLeftStickCoordinate(inputs, resolved_coordinate)) {
        return;
    }

    outputs.leftStickX = resolved_coordinate.x;
    outputs.leftStickY = resolved_coordinate.y;
}
