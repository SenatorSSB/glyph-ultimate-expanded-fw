#include "modes/SenscopePrototype.hpp"

#include "prototypes/senscope/SenscopePrototypeSelfTest.hpp"

namespace {

constexpr uint8_t kAnalogNeutral = 128;
constexpr uint8_t kAnalogMin = 0;
constexpr uint8_t kAnalogMax = 255;

} // namespace

SenscopePrototype::SenscopePrototype() : ControllerMode() {
    // G11i compile-visible prototype self-test helper call only. This remains isolated because
    // SenscopePrototype is still unregistered and unselected in mode selection.
    (void)RunPrototypeStaticSmokeCheck();
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
