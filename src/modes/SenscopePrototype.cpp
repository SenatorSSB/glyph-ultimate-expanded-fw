#include "modes/SenscopePrototype.hpp"

#include "prototypes/senscope/SenscopePrototypeDigital.hpp"
#include "prototypes/senscope/SenscopePrototypeDirection.hpp"
#include "prototypes/senscope/SenscopePrototypeForce.hpp"
#include "prototypes/senscope/SenscopePrototypeResolver.hpp"
#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

namespace {

constexpr uint8_t kAnalogNeutral = 128;
constexpr uint8_t kAnalogMin = 0;
constexpr uint8_t kAnalogMax = 255;
constexpr senscope::prototype::SenscopePrototypePhysicalButtonMask kSampleDigitalRuleTriggerMask =
    1ull << 42;
constexpr senscope::prototype::SenscopePrototypePhysicalButtonMask kSampleForceRuleTriggerMask = 1ull << 41;
constexpr senscope::prototype::SenscopePrototypeModifierCombinationMask kSampleModifierMask = 0b001;

} // namespace

SenscopePrototype::SenscopePrototype() : ControllerMode() {
    // G11g compile-visible helper integration only. This remains isolated because
    // SenscopePrototype is still unregistered and unselected in mode selection.
    (void)RunPrototypeStaticSmokeCheck();
}

bool SenscopePrototype::RunPrototypeStaticSmokeCheck() {
    namespace proto = senscope::prototype;

    const proto::SenscopePrototypeValidationResult validation = ValidateScaffoldExampleProfile();
    if (!validation.is_valid) {
        return false;
    }

    proto::SenscopePrototypeDirectionRequest direction_request = {};
    direction_request.pre_socd_direction_roles =
        proto::kSenscopePrototypeDirectionRoleLeft | proto::kSenscopePrototypeDirectionRoleUp;
    direction_request.opposite_policy = proto::SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
    const proto::SenscopePrototypeDirectionResult direction_result =
        proto::ResolveSenscopePrototypeDirection(direction_request);
    if (direction_result.status != proto::SenscopePrototypeDirectionStatus::Resolved ||
        direction_result.resolved_direction_key != proto::SenscopePrototypeDirectionKey::D7) {
        return false;
    }

    const proto::SenscopePrototypeProfile &example_profile = proto::GetSenscopePrototypeExampleProfile();

    proto::SenscopePrototypeResolverRequest resolver_request = {};
    resolver_request.active_modifier_mask = kSampleModifierMask;
    resolver_request.resolved_direction_key =
        static_cast<uint8_t>(direction_result.resolved_direction_key);
    resolver_request.fallback_policy = proto::SenscopePrototypeResolverFallbackPolicy::AllowHighestPrioritySubset;
    const proto::SenscopePrototypeResolverResult resolver_result =
        proto::ResolveSenscopePrototypeLeftStickRawCoordinate(example_profile, resolver_request);
    if (resolver_result.status != proto::SenscopePrototypeResolverStatus::Resolved) {
        return false;
    }

    proto::SenscopePrototypeDigitalRequest digital_request = {};
    digital_request.direct_digital_output_mask = proto::kSenscopePrototypeOutputA;
    digital_request.active_physical_button_mask = kSampleDigitalRuleTriggerMask;
    const proto::SenscopePrototypeDigitalResult digital_result =
        proto::ComposeSenscopePrototypeProfileDigitalOutputs(example_profile, digital_request);
    const proto::SenscopePrototypeDigitalOutputMask expected_digital_mask =
        proto::kSenscopePrototypeOutputA |
        proto::kSenscopePrototypeOutputB |
        proto::kSenscopePrototypeOutputY;
    if (digital_result.status != proto::SenscopePrototypeDigitalStatus::Composed ||
        digital_result.composed_digital_output_mask != expected_digital_mask ||
        digital_result.triggered_rule_count != 1) {
        return false;
    }

    proto::SenscopePrototypeForceRequest force_request = {};
    force_request.active_physical_button_mask = kSampleForceRuleTriggerMask;
    force_request.post_socd_direction_key = static_cast<uint8_t>(direction_result.resolved_direction_key);
    const proto::SenscopePrototypeForceResult force_result =
        proto::ResolveSenscopePrototypeProfileForceOverride(example_profile, force_request);
    if (force_result.status != proto::SenscopePrototypeForceStatus::Resolved ||
        !force_result.matched ||
        force_result.digital_output_contribution != proto::kSenscopePrototypeOutputB) {
        return false;
    }

    return true;
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
    (void)inputs;
    (void)backend_id;

    // G11b inert shell behavior: keep analog outputs centered and triggers neutral.
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
}

senscope::prototype::SenscopePrototypeValidationResult
SenscopePrototype::ValidateScaffoldExampleProfile() {
    return senscope::prototype::ValidateSenscopePrototypeProfile(
        senscope::prototype::GetSenscopePrototypeExampleProfile()
    );
}
