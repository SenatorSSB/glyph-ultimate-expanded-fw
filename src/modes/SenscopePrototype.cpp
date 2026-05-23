#include "modes/SenscopePrototype.hpp"

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

namespace {

constexpr uint8_t kAnalogNeutral = 128;
constexpr uint8_t kAnalogMin = 0;
constexpr uint8_t kAnalogMax = 255;

} // namespace

SenscopePrototype::SenscopePrototype() : ControllerMode() {
    // G11b scaffold reference only: validate the compile-time prototype example profile.
    // This does not wire the mode into runtime mode selection.
    (void)ValidateScaffoldExampleProfile();
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
