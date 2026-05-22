#include "modes/ESAM1.hpp"
#include <cmath>

#define PI  3.14159265
#define PI4 0.78539816

#define ANALOG_STICK_MIN 28
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 228

ESAM1::ESAM1(socd::SocdType socd_type) : ControllerMode(socd_type) {
    _socd_pair_count = 4;
    _socd_pairs = new socd::SocdPair[_socd_pair_count]{
        socd::SocdPair{&InputState::left,    &InputState::right  },
        socd::SocdPair{ &InputState::down,   &InputState::up     },
        socd::SocdPair{ &InputState::c_left, &InputState::c_right},
        socd::SocdPair{ &InputState::c_down, &InputState::c_up   },
    };
}

void ESAM1::UpdateDigitalOutputs(InputState &inputs, OutputState &outputs) {
    outputs.a = inputs.a;
    outputs.b = inputs.b;
    outputs.x = inputs.x;
    outputs.y = inputs.y;
    outputs.buttonL = false;
    outputs.buttonR = inputs.z;
    outputs.triggerLDigital = inputs.l;
    outputs.triggerRDigital = inputs.r;
    outputs.start = inputs.start;
    outputs.select = inputs.select;
    outputs.home = inputs.home;

    // Turn on D-Pad layer by holding lightshield.
    if (inputs.lightshield) {
        outputs.dpadUp = inputs.up;
        outputs.dpadDown = inputs.down;
        outputs.dpadLeft = inputs.left;
        outputs.dpadRight = inputs.right;
    }
}

void ESAM1::UpdateAnalogOutputs(InputState &inputs, OutputState &outputs) {
    // Coordinate calculations to make modifier handling simpler.
    UpdateDirections(
        inputs.left,
        inputs.right,
        inputs.down,
        inputs.up,
        inputs.c_left,
        inputs.c_right,
        inputs.c_down,
        inputs.c_up,
        ANALOG_STICK_MIN,
        ANALOG_STICK_NEUTRAL,
        ANALOG_STICK_MAX,
        outputs
    );

    uint8_t nY = ANALOG_STICK_NEUTRAL;
    uint8_t nX = ANALOG_STICK_NEUTRAL;

    bool shield_button_pressed = inputs.l || inputs.r;

    // ModeCSR not pressed
    if (!inputs.midshield) {
        nY = 128;
        nX = 128;
        
        if (directions.y == 0)
            outputs.leftStickY = nY;
        else if (directions.y == 1)
            outputs.leftStickY = 205;
        else
            outputs.leftStickY = 51;

        if (directions.x == 0)
            outputs.leftStickX = nX;
        else if (directions.x == 1)
            outputs.leftStickX = 195;
        else
            outputs.leftStickX = 61;

        if (inputs.mod_x && !inputs.mod_y) {
            // Tilt1 X
            outputs.leftStickX = 128 + (directions.x * 53); //    Tilt1 Y Up                 Tilt1 Y Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 42) : 128 + (directions.y * 42);
        }
        else if (!inputs.mod_x && inputs.mod_y) {
            // Tilt2 X
            outputs.leftStickX = 128 + (directions.x * 215); //   Tilt2 Y Up                 Tilt2 Y Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 63) : 128 + (directions.y * 73);
        }
        else if (inputs.mod_x && inputs.mod_y) {
            // Tilt3 X
            outputs.leftStickX = 128 + (directions.x * 40); //    Tilt3 Y Up                 Tilt3 Y Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 49) : 128 + (directions.y * 49);
        }

        // X1
        if (inputs.mod_x1 && !inputs.mod_x2)
            outputs.leftStickX = 128 + (directions.x * 32);
        // X2
        else if (!inputs.mod_x1 && inputs.mod_x2)
            outputs.leftStickX = 128 + (directions.x * 46);
        // X3
        else if (inputs.mod_x1 && inputs.mod_x2)
            outputs.leftStickX = 128 + (directions.x * 46);
        
        // Y1
        if (inputs.mod_y1 && !inputs.mod_y2)      //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 29) : 128 + (directions.y * 29);
        // Y2
        else if (!inputs.mod_y1 && inputs.mod_y2) //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 46) : 128 + (directions.y * 46);
        // Y3
        else if (inputs.mod_y1 && inputs.mod_y2)  //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? 128 + (directions.y * 29) : 128 + (directions.y * 29);
    }
    // ModeCSR pressed 
    else {
        nY = 172;
        nX = 128;
        
        if (directions.y == 0)
            outputs.leftStickY = nY;
        else if (directions.y == 1)
            outputs.leftStickY = 172;
        else
            outputs.leftStickY = 84;

        if (directions.x == 0)
            outputs.leftStickX = nX;
        else if (directions.x == 1)
            outputs.leftStickX = 255;
        else
            outputs.leftStickX = 1;

        if (inputs.mod_x && !inputs.mod_y) {
            // Tilt1 X
            outputs.leftStickX = nX + (directions.x * 33);  //   Tilt1 Y Up                 Tilt1 Y Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 3) : nY + (directions.y * 91);
        }
        else if (!inputs.mod_x && inputs.mod_y) {
            // Tilt2 X
            outputs.leftStickX = nX + (directions.x * 69);  //   Tilt2 Y Up                 Tilt2 Y Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 245) : nY + (directions.y * 77);
        }
        else if (inputs.mod_x && inputs.mod_y) {
            // Tilt3 X
            outputs.leftStickX = nX + (directions.x * 32);  //   Tilt3 Y Up                 Tilt3 Y Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 2) : nY + (directions.y * 90);
        }

        // X1
        if (inputs.mod_x1 && !inputs.mod_x2)
            outputs.leftStickX = nX + (directions.x * 51);
        // X2
        else if (!inputs.mod_x1 && inputs.mod_x2)
            outputs.leftStickX = nX + (directions.x * 69);
        // X3
        else if (inputs.mod_x1 && inputs.mod_x2)
            outputs.leftStickX = nX + (directions.x * 46);
        
        // Y1
        if (inputs.mod_y1 && !inputs.mod_y2)      //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 156) : nY + (directions.y * 244);
        // Y2
        else if (!inputs.mod_y1 && inputs.mod_y2) //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 175) : nY + (directions.y * 7);
        // Y3
        else if (inputs.mod_y1 && inputs.mod_y2)  //             Up                        Down
            outputs.leftStickY = (directions.y == 1) ? nY + (directions.y * 41) : nY + (directions.y * 41);
        
        // C stick rotation
        if (directions.cx != 0 || directions.cy != 0) {
            double tempX = outputs.rightStickX - 128;
            double tempY = outputs.rightStickY - 128;

            double angle = atan(tempY/tempX);

            // If X is negative, we are on the left side of the circle, add π to adjust
            if (tempX < 0)
                angle += PI;

            // Rotate 45 degrees CCW
            angle += PI4;

            tempX = round(cos(angle) * (ANALOG_STICK_MAX - ANALOG_STICK_NEUTRAL));
            tempY = round(sin(angle) * (ANALOG_STICK_MAX - ANALOG_STICK_NEUTRAL));

            outputs.rightStickX = tempX + 128;
            outputs.rightStickY = tempY + 128;
        }
    }

    if (inputs.l) {
        outputs.triggerLAnalog = 140;
    }

    if (inputs.r) {
        outputs.triggerRAnalog = 140;
    }

    // Shut off C-stick when using D-Pad layer.
    if (inputs.lightshield) {
        outputs.leftStickX = 128;
        outputs.leftStickY = 128;

        if (inputs.midshield)
            outputs.leftStickY = 172;

    }

    // Nunchuk overrides left stick.
    if (inputs.nunchuk_connected) {
        outputs.leftStickX = inputs.nunchuk_x;
        outputs.leftStickY = inputs.nunchuk_y;
    }
}