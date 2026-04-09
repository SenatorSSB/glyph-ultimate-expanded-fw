#include "modes/FgcMode.hpp"


#define ANALOG_STICK_MIN 0
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 255

FgcMode::FgcMode() : ControllerMode() {}

void FgcMode::SetConfig(GameModeConfig &config) {
    InputMode::SetConfig(config);
}

void FgcMode::HandleSocd(InputState &inputs) {
    InputMode::HandleSocd(inputs);
}

void FgcMode::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    // Directions
    outputs.dpadLeft = inputs.lf3;
    outputs.dpadRight = inputs.lf1;
    outputs.dpadDown = inputs.lf2;
    outputs.dpadUp = inputs.lt1;

    // Menu keys
    outputs.start = inputs.mb7;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;
    outputs.leftStickClick = inputs.lt2;
    outputs.rightStickClick = inputs.rt1;

    // Right hand bottom row
    outputs.a = inputs.rf1;
    outputs.b = inputs.rf2;
    outputs.triggerRDigital = inputs.rf3;
    outputs.triggerLDigital = inputs.rf4;

    // Right hand top row
    outputs.x = inputs.rf5;
    outputs.y = inputs.rf6;
    outputs.buttonR = inputs.rf7;
    outputs.buttonL = inputs.rf8;
}

void FgcMode::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    OutputState outputBuffer = OutputState();

    UpdateDirections(
        inputs.lf8, // Left
        inputs.lf6, // Right
        inputs.lf7, // Down
        inputs.lt6, // Up
        inputs.rt3, // C-Left
        inputs.rt5, // C-Right
        inputs.rt2, // C-Down
        inputs.rt4, // C-Up
        ANALOG_STICK_MIN,
        ANALOG_STICK_NEUTRAL,
        ANALOG_STICK_MAX,
        outputs
    );

    outputs.leftStickX = 128 + (directions.x * 120);
    outputs.leftStickY = 128 + (directions.y * 120);;
    outputs.rightStickX = 128 + (directions.cx * 120);;
    outputs.rightStickY = 128 + (directions.cy * 120);;
    outputs.triggerLAnalog = outputs.triggerLDigital ? 255 : 0;
    outputs.triggerRAnalog = outputs.triggerRDigital ? 255 : 0;
}