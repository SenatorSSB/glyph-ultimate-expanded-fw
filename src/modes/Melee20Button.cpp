#include "modes/Melee20Button.hpp"

#define ANALOG_STICK_MIN 48
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 208

Melee20Button::Melee20Button() : ControllerMode() {
    _horizontal_socd = false;
}

void Melee20Button::SetConfig(GameModeConfig &config, const MeleeOptions options) {
    InputMode::SetConfig(config);
    _options = options;
}

void Melee20Button::HandleSocd(InputState &inputs) {
    _horizontal_socd = inputs.lf3 && inputs.lf1;
    InputMode::HandleSocd(inputs);
}

void Melee20Button::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {

    outputs.a = inputs.rt1;
    outputs.b = inputs.rf1;
    outputs.x = inputs.rf2;
    outputs.y = inputs.rf6;
    outputs.buttonR = inputs.rf3;
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
    //outputs.leftStickClick = inputs.mb3;
    //outputs.rightStickClick = inputs.mb2;
    //outputs.buttonL = inputs.rf9;

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
    
}

void Melee20Button::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    OutputState outputBuffer = OutputState();

    // Coordinate calculations to make modifier handling simpler.
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

    bool shield_button_pressed = inputs.lf4 || inputs.rf5 || inputs.rf7 || inputs.rf8;
    if (directions.diagonal) {
        // q1/2 = 7000 7000
        outputBuffer.leftStickX = 128 + (directions.x * 56);
        outputBuffer.leftStickY = 128 + (directions.y * 56);
        // L, R, LS, and MS + q3/4 = 7000 6875 (For vanilla shield drop. Gives 44.5
        // degree wavedash). Also used as default q3/4 diagonal if crouch walk option select is
        // enabled.
        if (directions.y == -1 && (shield_button_pressed || _options.crouch_walk_os)) {
            outputBuffer.leftStickX = 128 + (directions.x * 56);
            outputBuffer.leftStickY = 128 + (directions.y * 55);
        }
    }

    /* Mod X */
    if (inputs.lt1) {
        // MX + Horizontal (even if shield is held) = 6625 = 53
        if (directions.horizontal) {
            outputBuffer.leftStickX = 128 + (directions.x * 53);
        }
        // MX + Vertical (even if shield is held) = 5375 = 43
        if (directions.vertical) {
            outputBuffer.leftStickY = 128 + (directions.y * 43);
        }
        if (directions.diagonal && shield_button_pressed) {
            // Use custom airdodge angle if set, otherwise B0XX standard default.
            if (_options.has_custom_airdodge) {
                outputBuffer.leftStickX = 128 + (directions.x * _options.custom_airdodge.x);
                outputBuffer.leftStickY = 128 + (directions.y * _options.custom_airdodge.y);
            } else {
                // MX + L, R, LS, and MS + q1/2/3/4 = 6375 3750 = 51 30
                outputBuffer.leftStickX = 128 + (directions.x * 51);
                outputBuffer.leftStickY = 128 + (directions.y * 30);
            }
        }

        /* Up B angles */
        if (directions.diagonal && !shield_button_pressed) {
            // 22.9638 - 7375 3125 = 59 25
            outputBuffer.leftStickX = 128 + (directions.x * 59);
            outputBuffer.leftStickY = 128 + (directions.y * 25);
            // 27.37104 - 7000 3625 (27.38) = 56 29
            if (inputs.rt2) {
                outputBuffer.leftStickX = 128 + (directions.x * 56);
                outputBuffer.leftStickY = 128 + (directions.y * 29);
            }
            // 31.77828 - 7875 4875 (31.76) = 63 39
            if (inputs.rt3) {
                outputBuffer.leftStickX = 128 + (directions.x * 63);
                outputBuffer.leftStickY = 128 + (directions.y * 39);
            }
            // 36.18552 - 7000 5125 (36.21) = 56 41
            if (inputs.rt4) {
                outputBuffer.leftStickX = 128 + (directions.x * 56);
                outputBuffer.leftStickY = 128 + (directions.y * 41);
            }
            // 40.59276 - 6125 5250 (40.6) = 49 42
            if (inputs.rt5) {
                outputBuffer.leftStickX = 128 + (directions.x * 49);
                outputBuffer.leftStickY = 128 + (directions.y * 42);
            }

            /* Extended Up B Angles */
            if (inputs.rf1) {
                // 22.9638 - 9125 3875 (23.0) = 73 31
                outputBuffer.leftStickX = 128 + (directions.x * 73);
                outputBuffer.leftStickY = 128 + (directions.y * 31);
                // 27.37104 - 8750 4500 (27.2) = 70 36
                if (inputs.rt2) {
                    outputBuffer.leftStickX = 128 + (directions.x * 70);
                    outputBuffer.leftStickY = 128 + (directions.y * 36);
                }
                // 31.77828 - 8500 5250 (31.7) = 68 42
                if (inputs.rt3) {
                    outputBuffer.leftStickX = 128 + (directions.x * 68);
                    outputBuffer.leftStickY = 128 + (directions.y * 42);
                }
                // 36.18552 - 7375 5375 (36.1) = 59 43
                if (inputs.rt4) {
                    outputBuffer.leftStickX = 128 + (directions.x * 59);
                    outputBuffer.leftStickY = 128 + (directions.y * 43);
                }
                // 40.59276 - 6375 5375 (40.1) = 51 43
                if (inputs.rt5) {
                    outputBuffer.leftStickX = 128 + (directions.x * 51);
                    outputBuffer.leftStickY = 128 + (directions.y * 43);
                }
            }
        }

        // Angled fsmash
        if (directions.cx != 0) {
            // 8500 5250 = 68 42
            outputBuffer.rightStickX = 128 + (directions.cx * 68);
            outputBuffer.rightStickY = 128 + (directions.y * 42);
        }
    }

    /* Mod Y */
    if (inputs.lt2) {
        // MY + Horizontal (even if shield is held) = 3375 = 27
        if (directions.horizontal) {
            outputBuffer.leftStickX = 128 + (directions.x * 27);
        }
        // MY + Vertical (even if shield is held) = 7375 = 59
        if (directions.vertical) {
            outputBuffer.leftStickY = 128 + (directions.y * 59);
        }
        if (directions.diagonal && shield_button_pressed) {
            // MY + L, R, LS, and MS + q1/2 = 4750 8750 = 38 70
            outputBuffer.leftStickX = 128 + (directions.x * 38);
            outputBuffer.leftStickY = 128 + (directions.y * 70);
            // MY + L, R, LS, and MS + q3/4 = 5000 8500 = 40 68
            if (directions.y == -1) {
                outputBuffer.leftStickX = 128 + (directions.x * 40);
                outputBuffer.leftStickY = 128 + (directions.y * 68);
            }
        }

        // Turnaround neutral B nerf
        if (inputs.rf1) {
            outputBuffer.leftStickX = 128 + (directions.x * 80);
        }

        /* Up B angles */
        if (directions.diagonal && !shield_button_pressed) {
            // 67.0362 - 3125 7375 = 25 59
            outputBuffer.leftStickX = 128 + (directions.x * 25);
            outputBuffer.leftStickY = 128 + (directions.y * 59);
            // 62.62896 - 3625 7000 (62.62) = 29 56
            if (inputs.rt2) {
                outputBuffer.leftStickX = 128 + (directions.x * 29);
                outputBuffer.leftStickY = 128 + (directions.y * 56);
            }
            // 58.22172 - 4875 7875 (58.24) = 39 63
            if (inputs.rt3) {
                outputBuffer.leftStickX = 128 + (directions.x * 39);
                outputBuffer.leftStickY = 128 + (directions.y * 63);
            }
            // 53.81448 - 5125 7000 (53.79) = 41 56
            if (inputs.rt4) {
                outputBuffer.leftStickX = 128 + (directions.x * 41);
                outputBuffer.leftStickY = 128 + (directions.y * 56);
            }
            // 49.40724 - 6375 7625 (50.10) = 51 61
            if (inputs.rt5) {
                outputBuffer.leftStickX = 128 + (directions.x * 51);
                outputBuffer.leftStickY = 128 + (directions.y * 61);
            }

            /* Extended Up B Angles */
            if (inputs.rf1) {
                // 67.0362 - 3875 9125 = 31 73
                outputBuffer.leftStickX = 128 + (directions.x * 31);
                outputBuffer.leftStickY = 128 + (directions.y * 73);
                // 62.62896 - 4500 8750 (62.8) = 36 70
                if (inputs.rt2) {
                    outputBuffer.leftStickX = 128 + (directions.x * 36);
                    outputBuffer.leftStickY = 128 + (directions.y * 70);
                }
                // 58.22172 - 5250 8500 (58.3) = 42 68
                if (inputs.rt3) {
                    outputBuffer.leftStickX = 128 + (directions.x * 42);
                    outputBuffer.leftStickY = 128 + (directions.y * 68);
                }
                // 53.81448 - 5875 8000 (53.7) = 47 64
                if (inputs.rt4) {
                    outputBuffer.leftStickX = 128 + (directions.x * 47);
                    outputBuffer.leftStickY = 128 + (directions.y * 64);
                }
                // 49.40724 - 5875 7125 (50.49) = 47 57
                if (inputs.rt5) {
                    outputBuffer.leftStickX = 128 + (directions.x * 47);
                    outputBuffer.leftStickY = 128 + (directions.y * 57);
                }
            }
        }
    }

    // C-stick ASDI Slideoff angle overrides any other C-stick modifiers (such as
    // angled fsmash).
    if (directions.cx != 0 && directions.cy != 0) {
        // 5250 8500 = 42 68
        outputBuffer.rightStickX = 128 + (directions.cx * 42);
        outputBuffer.rightStickY = 128 + (directions.cy * 68);
    }

    // Horizontal SOCD overrides X-axis modifiers (for ledgedash maximum jump
    // trajectory).
    if (!_options.disable_ledgedash_socd_override && _horizontal_socd && !directions.vertical) {
        outputBuffer.leftStickX = 128 + (directions.x * 80);
    }


    uint8_t triggerLAnalog = 0;
    uint8_t triggerRAnalog = 0;

    if (inputs.rf7) {
        triggerRAnalog = 49;
    }
    if (inputs.rf8) {
        triggerRAnalog = 94;
    }

    if (outputBuffer.triggerLDigital) {
        triggerLAnalog = 140;
    }
    if (outputBuffer.triggerRDigital) {
        triggerRAnalog = 140;
    }

    outputBuffer.triggerLAnalog = triggerLAnalog;
    outputBuffer.triggerRAnalog = triggerRAnalog;

    // Shut off C-stick when using D-Pad layer.
    if ((inputs.lt1 && inputs.lt2) || inputs.nunchuk_c) {
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
