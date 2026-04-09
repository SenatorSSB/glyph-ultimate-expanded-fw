#include "modes/ProjectM.hpp"

#define ANALOG_STICK_MIN 28
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 228

ProjectM::ProjectM() : ControllerMode() {
    _horizontal_socd = false;
}

void ProjectM::SetConfig(GameModeConfig &config, const ProjectMOptions options) {
    InputMode::SetConfig(config);
    _options = options;
}

void ProjectM::HandleSocd(InputState &inputs) {
    _horizontal_socd = inputs.lf3 && inputs.lf1;
    InputMode::HandleSocd(inputs);
}

void ProjectM::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    outputs.a = inputs.rt1;
    outputs.b = inputs.rf1;
    outputs.x = inputs.rf2;
    outputs.y = inputs.rf6;
    // True Z press vs macro lightshield + A.
    if (_options.true_z_press || inputs.lt1) {
        outputs.buttonR = inputs.rf3;
    } else {
        outputs.buttonR = false;
        outputs.a = inputs.rt1 || inputs.rf3;
    }
    if (inputs.nunchuk_connected) {
        outputs.triggerLDigital = inputs.nunchuk_z;
    } else {
        outputs.triggerLDigital = inputs.lf4;
    }
    outputs.triggerRDigital = inputs.rf5;

    outputs.start = inputs.mb7;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;
    /*
    outputs.leftStickClick = inputs.mb3;
    outputs.rightStickClick = inputs.mb2;
    outputs.buttonL = inputs.rf9;
    */
    outputs.dpadUp = 0;
    outputs.dpadDown = 0;
    outputs.dpadLeft = 0;
    outputs.dpadRight = 0;

    // Activate D-Pad layer by holding Mod X + Mod Y or Nunchuk C button.
    if ((inputs.lt1 && inputs.lt2) || inputs.nunchuk_c) {
        outputs.dpadUp = inputs.rt4;
        outputs.dpadDown = inputs.rt2;
        outputs.dpadLeft = inputs.rt3;
        outputs.dpadRight = inputs.rt5;
    }

    // Don't override dpad up if it's already pressed using the MX + MY dpad
    // layer.
    outputs.dpadUp |= inputs.rf8;
    outputs.dpadDown |= inputs.rf7;
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
}

void ProjectM::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
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
        outputs
    );

    bool shield_button_pressed = inputs.lf4 || inputs.rf5;

    if (directions.diagonal) {
        if (directions.y == 1) {
            outputs.leftStickX = 128 + (directions.x * 83);
            outputs.leftStickY = 128 + (directions.y * 93);
        }
    }

    /* Mod X */
    if (inputs.lt1) {
        if (directions.horizontal) {
            outputs.leftStickX = 128 + (directions.x * 70);
        }
        if (directions.vertical) {
            outputs.leftStickY = 128 + (directions.y * 60);
        }

        if (directions.cx != 0) {
            outputs.rightStickX = 128 + (directions.cx * 65);
            outputs.rightStickY = 128 + (directions.y * 23);
        }

        if (directions.diagonal) {
            // Default MX Diagonal
            outputs.leftStickX = 128 + (directions.x * 70);
            outputs.leftStickY = 128 + (directions.y * 34);

            if (inputs.rf1) {
                outputs.leftStickX = 128 + (directions.x * 85);
                outputs.leftStickY = 128 + (directions.y * 31);
            }

            // Airdodge angle
            if (inputs.rf5) {
                if (_options.has_custom_airdodge) {
                    outputs.leftStickX = 128 + (directions.x * _options.custom_airdodge.x);
                    outputs.leftStickY = 128 + (directions.y * _options.custom_airdodge.y);
                } else {
                    outputs.leftStickX = 128 + (directions.x * 82);
                    outputs.leftStickY = 128 + (directions.y * 35);
                }
            }

            if (inputs.rt4) {
                outputs.leftStickX = 128 + (directions.x * 77);
                outputs.leftStickY = 128 + (directions.y * 55);
            }

            if (inputs.rt2) {
                outputs.leftStickX = 128 + (directions.x * 82);
                outputs.leftStickY = 128 + (directions.y * 36);
            }

            if (inputs.rt3) {
                outputs.leftStickX = 128 + (directions.x * 84);
                outputs.leftStickY = 128 + (directions.y * 50);
            }

            if (inputs.rt5) {
                outputs.leftStickX = 128 + (directions.x * 72);
                outputs.leftStickY = 128 + (directions.y * 61);
            }
        }
    }

    /* Mod Y */
    if (inputs.lt2) {
        if (directions.horizontal) {
            outputs.leftStickX = 128 + (directions.x * 35);
        }
        if (directions.vertical) {
            outputs.leftStickY = 128 + (directions.y * 70);
        }

        if (directions.diagonal) {
            outputs.leftStickX = 128 + (directions.x * 28);
            outputs.leftStickY = 128 + (directions.y * 58);

            if (inputs.rf1) {
                outputs.leftStickX = 128 + (directions.x * 28);
                outputs.leftStickY = 128 + (directions.y * 85);
            }

            if (inputs.rf5) {
                outputs.leftStickX = 128 + (directions.x * 51);
                outputs.leftStickY = 128 + (directions.y * 82);
            }

            if (inputs.rt4) {
                outputs.leftStickX = 128 + (directions.x * 55);
                outputs.leftStickY = 128 + (directions.y * 77);
            }

            if (inputs.rt2) {
                outputs.leftStickX = 128 + (directions.x * 34);
                outputs.leftStickY = 128 + (directions.y * 82);
            }

            if (inputs.rt3) {
                outputs.leftStickX = 128 + (directions.x * 40);
                outputs.leftStickY = 128 + (directions.y * 84);
            }

            if (inputs.rt5) {
                outputs.leftStickX = 128 + (directions.x * 62);
                outputs.leftStickY = 128 + (directions.y * 72);
            }
        }
    }

    // C-stick ASDI Slideoff angle overrides any other C-stick modifiers (such as
    // angled fsmash).
    // We don't apply this for c-up + c-left/c-right in case we want to implement
    // C-stick nair somehow.
    if (directions.cx != 0 && directions.cy == -1) {
        // 3000 9875 = 30 78
        outputs.rightStickX = 128 + (directions.cx * 35);
        outputs.rightStickY = 128 + (directions.cy * 98);
    }

    // Horizontal SOCD overrides X-axis modifiers (for ledgedash maximum jump
    // trajectory).
    if (!_options.disable_ledgedash_socd_override && _horizontal_socd && !directions.vertical &&
        !shield_button_pressed) {
        outputs.leftStickX = 128 + (directions.x * 100);
    }

    uint8_t triggerLAnalog = 0;
    uint8_t triggerRAnalog = 0;

    if (inputs.rf9) {
        triggerRAnalog = 49;
    }

    // Send lightshield input if we are using Z = lightshield + A macro.
    if (inputs.rf3 && !(inputs.lt1 || _options.true_z_press)) {
        triggerRAnalog = 49;
    }

    if (outputs.triggerLDigital) {
       triggerLAnalog = 140;
    }

    if (outputs.triggerRDigital) {
       triggerRAnalog = 140;
    }

    outputs.triggerLAnalog = triggerLAnalog;
    outputs.triggerRAnalog = triggerRAnalog;

    // Shut off C-stick when using D-Pad layer.
    if ((inputs.lt1 && inputs.lt2) || inputs.nunchuk_c) {
        outputs.rightStickX = 128;
        outputs.rightStickY = 128;
    }

    // Nunchuk overrides left stick.
    if (inputs.nunchuk_connected) {
        outputs.leftStickX = inputs.nunchuk_x;
        outputs.leftStickY = inputs.nunchuk_y;
    }
}
