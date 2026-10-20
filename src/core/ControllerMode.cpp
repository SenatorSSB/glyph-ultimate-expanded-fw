#include "core/ControllerMode.hpp"

ControllerMode::ControllerMode() : InputMode() {
    // Set up initial state.
    ResetDirections();
}

void ControllerMode::UpdateOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    // Create a copy of the input state here so remapping can be many-to-one (many physical buttons
    // to one activated button).
    InputState remapped_inputs = inputs;
    HandleRemap(inputs, remapped_inputs);
    InputState post_inputs = remapped_inputs;
    HandleSocd(post_inputs);
    const ResolvedInputContext context{inputs, remapped_inputs, post_inputs};
    UpdatePreprocessedOutputs(context, outputs, backend_id);
}

void ControllerMode::UpdatePreprocessedOutputs(const ResolvedInputContext &context, OutputState &outputs, CommunicationBackendId backend_id) {
    UpdateDigitalOutputs(context.post, outputs);
    UpdateAnalogOutputs(context.post, outputs, backend_id);
}

void ControllerMode::ResetDirections() {
    directions = {
        .horizontal = false,
        .vertical = false,
        .diagonal = false,
        .x = 0,
        .y = 0,
        .cx = 0,
        .cy = 0,
    };
}

void ControllerMode::UpdateDirections(
    bool lsLeft,
    bool lsRight,
    bool lsDown,
    bool lsUp,
    bool rsLeft,
    bool rsRight,
    bool rsDown,
    bool rsUp,
    uint8_t analogStickMin,
    uint8_t analogStickNeutral,
    uint8_t analogStickMax,
    OutputState &outputs
) {
    ResetDirections();

    outputs.leftStickX = analogStickNeutral;
    outputs.leftStickY = analogStickNeutral;
    outputs.rightStickX = analogStickNeutral;
    outputs.rightStickY = analogStickNeutral;

    // Coordinate calculations to make modifier handling simpler.
    if (lsLeft || lsRight) {
        directions.horizontal = true;
        if (lsLeft) {
            directions.x = -1;
            outputs.leftStickX = analogStickMin;
        } else {
            directions.x = 1;
            outputs.leftStickX = analogStickMax;
        }
    }
    if (lsDown || lsUp) {
        directions.vertical = true;
        if (lsDown) {
            directions.y = -1;
            outputs.leftStickY = analogStickMin;
        } else {
            directions.y = 1;
            outputs.leftStickY = analogStickMax;
        }
    }
    if (directions.horizontal && directions.vertical)
        directions.diagonal = true;

    if (rsLeft || rsRight) {
        if (rsLeft) {
            directions.cx = -1;
            outputs.rightStickX = analogStickMin;
        } else {
            directions.cx = 1;
            outputs.rightStickX = analogStickMax;
        }
    }
    if (rsDown || rsUp) {
        if (rsDown) {
            directions.cy = -1;
            outputs.rightStickY = analogStickMin;
        } else {
            directions.cy = 1;
            outputs.rightStickY = analogStickMax;
        }
    }
}
