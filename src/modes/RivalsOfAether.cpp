#include "modes/RivalsOfAether.hpp"

#define ANALOG_STICK_MIN 28
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 228

RivalsOfAether::RivalsOfAether() : ControllerMode() {}

void RivalsOfAether::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    outputs.a = inputs.rt1;
    outputs.b = inputs.rf1;
    outputs.x = inputs.rf2;
    outputs.y = inputs.rf6;
    outputs.buttonR = inputs.rf3;
    if (inputs.nunchuk_connected) {
        // Lightshield with C button.
        if (inputs.nunchuk_c) {
            outputs.triggerLAnalog = 49;
        }
        outputs.triggerLDigital = inputs.nunchuk_z;
    } else {
        outputs.triggerLDigital = inputs.lf4;
    }
    outputs.triggerRDigital = inputs.rf5;
    outputs.start = inputs.mb7;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;
    outputs.leftStickClick = inputs.rf7;
    outputs.rightStickClick = inputs.rf8;

    outputs.dpadUp = 0;
    outputs.dpadDown = 0;
    outputs.dpadLeft = 0;
    outputs.dpadRight = 0;
    // Activate D-Pad layer by holding Mod X + Mod Y.
    if (inputs.lt1 && inputs.lt2) {
        outputs.dpadUp = inputs.rt4;
        outputs.dpadDown = inputs.rt2;
        outputs.dpadLeft = inputs.rt3;
        outputs.dpadRight = inputs.rt5;
    }

    outputs.dpadUp |= inputs.lt6;
    outputs.dpadDown |= inputs.lf7;
    outputs.dpadLeft |= inputs.lf8;
    outputs.dpadRight |= inputs.lf6;

    outputs.leftStickLeft = inputs.lf3;
    outputs.leftStickRight = inputs.lf1;
    outputs.leftStickDown = inputs.lf2;
    outputs.leftStickUp = inputs.rf4;

    outputs.rightStickLeft = inputs.rt3;
    outputs.rightStickRight = inputs.rt5;
    outputs.rightStickDown = inputs.rt2;
    outputs.rightStickUp = inputs.rt4;

    outputs.modX = inputs.lt1;
    outputs.modY = inputs.lt2;

    outputs.buttonL = inputs.rf9;

}

void RivalsOfAether::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    // Coordinate calculations to make modifier handling simpler.
    OutputState outputBuffer = OutputState();
    UpdateDirections(
        inputs.lf3, // Left
        inputs.lf1, // Right
        inputs.lf2, // Down
        inputs.rf4, // Up
        inputs.rt3, // C-Left
        inputs.rt5, // C-Right
        inputs.rt2, // C-Down
        inputs.rt4, // C-Up
        ANALOG_STICK_MIN,
        ANALOG_STICK_NEUTRAL,
        ANALOG_STICK_MAX,
        outputBuffer
    );

    bool shield_button_pressed = inputs.lf4 || inputs.rf5;

    // 48 total DI angles, 24 total Up b angles, 16 total airdodge angles

    if (inputs.lt1) {
        if (directions.horizontal) {
            outputBuffer.leftStickX = 128 + (directions.x * 66);
            // MX Horizontal Tilts
            if (inputs.rt1) {
                outputBuffer.leftStickX = 128 + (directions.x * 44);
            }
        }

        if(directions.vertical) {
            outputBuffer.leftStickY = 128 + (directions.y * 44);
            // MX Vertical Tilts
            if (inputs.rt1) {
                outputBuffer.leftStickY = 128 + (directions.y * 67);
            }
        }

        /* Extra DI, Air Dodge, and Up B angles */
        if (directions.diagonal) {
            outputBuffer.leftStickX = 128 + (directions.x * 59);
            outputBuffer.leftStickY = 128 + (directions.y * 23);

            // Angles just for DI and Up B
            if (inputs.rt2) {
                outputBuffer.leftStickX = 128 + (directions.x * 49);
                outputBuffer.leftStickY = 128 + (directions.y * 24);
            }

            // Angles just for DI
            if (inputs.rt3) {
                outputBuffer.leftStickX = 128 + (directions.x * 52);
                outputBuffer.leftStickY = 128 + (directions.y * 31);
            }

            if (inputs.rt4) {
                outputBuffer.leftStickX = 128 + (directions.x * 49);
                outputBuffer.leftStickY = 128 + (directions.y * 35);
            }

            if (inputs.rt5) {
                outputBuffer.leftStickX = 128 + (directions.x * 51);
                outputBuffer.leftStickY = 128 + (directions.y * 43);
            }
        }
    }

    if (inputs.lt2) {
        if (directions.horizontal) {
            outputBuffer.leftStickX = 128 + (directions.x * 44);
        }

        if(directions.vertical) {
            outputBuffer.leftStickY = 128 + (directions.y * 67);
        }

        /* Extra DI, Air Dodge, and Up B angles */
        if (directions.diagonal) {
            outputBuffer.leftStickX = 128 + (directions.x * 44);
            outputBuffer.leftStickY = 128 + (directions.y * 113);

            // Angles just for DI and Up B
            if (inputs.rt2) {
                outputBuffer.leftStickX = 128 + (directions.x * 44);
                outputBuffer.leftStickY = 128 + (directions.y * 90);
            }

            // Angles just for DI
            if (inputs.rt3) {
                outputBuffer.leftStickX = 128 + (directions.x * 44);
                outputBuffer.leftStickY = 128 + (directions.y * 74);
            }

            if (inputs.rt4) {
                outputBuffer.leftStickX = 128 + (directions.x * 45);
                outputBuffer.leftStickY = 128 + (directions.y * 63);
            }

            if (inputs.rt5) {
                outputBuffer.leftStickX = 128 + (directions.x * 47);
                outputBuffer.leftStickY = 128 + (directions.y * 57);
            }
        }
    }

    // Shut off C-stick when using D-Pad layer.
    if (inputs.lt1 && inputs.lt2) {
        outputBuffer.rightStickX = 128;
        outputBuffer.rightStickY = 128;
    }

    // Nunchuk overrides left stick.
    if (inputs.nunchuk_connected) {
        outputBuffer.leftStickX = inputs.nunchuk_x;
        outputBuffer.leftStickY = inputs.nunchuk_y;
    }

    outputs.leftStickX = outputBuffer.leftStickX;
    outputs.leftStickY = outputBuffer.leftStickY;
    outputs.rightStickX = outputBuffer.rightStickX;
    outputs.rightStickY = outputBuffer.rightStickY;
    outputs.triggerLAnalog = outputBuffer.triggerLAnalog;
    outputs.triggerRAnalog = outputBuffer.triggerRAnalog;
}
