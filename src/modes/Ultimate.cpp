/* Ultimate profile by Taker */
#include "modes/Ultimate.hpp"
#include <config.pb.h>

#define ANALOG_STICK_MIN 28
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 228

namespace {
struct StickPoint {
    uint8_t x;
    uint8_t y;
};

constexpr StickPoint kDefaultTable[9] = {
    {61, 51}, {128, 51}, {195, 51},
    {61, 128}, {128, 128}, {195, 128},
    {61, 205}, {128, 205}, {195, 205},
};

constexpr StickPoint kModeDefaultTable[9] = {
    {1, 84}, {128, 84}, {255, 84},
    {1, 172}, {128, 172}, {255, 172},
    {1, 172}, {128, 172}, {255, 172},
};

constexpr StickPoint kX1Table[9] = {
    {93, 51}, {128, 51}, {163, 51},
    {93, 128}, {128, 128}, {163, 128},
    {93, 205}, {128, 205}, {163, 205},
};

constexpr StickPoint kX2Table[9] = {
    {82, 51}, {128, 51}, {174, 51},
    {82, 128}, {128, 128}, {174, 128},
    {82, 205}, {128, 205}, {174, 205},
};

constexpr StickPoint kMX1Table[9] = {
    {74, 84}, {128, 84}, {182, 84},
    {74, 172}, {128, 172}, {182, 172},
    {74, 172}, {128, 172}, {182, 172},
};

constexpr StickPoint kMX2Table[9] = {
    {59, 84}, {128, 84}, {197, 84},
    {59, 172}, {128, 172}, {197, 172},
    {59, 172}, {128, 172}, {197, 172},
};

constexpr StickPoint kY1Table[9] = {
    {61, 99}, {128, 99}, {195, 99},
    {61, 128}, {128, 128}, {195, 128},
    {61, 157}, {128, 157}, {195, 157},
};

constexpr StickPoint kY2Table[9] = {
    {61, 82}, {128, 82}, {195, 82},
    {61, 128}, {128, 128}, {195, 128},
    {61, 174}, {128, 174}, {195, 174},
};

constexpr StickPoint kMY1Table[9] = {
    {1, 184}, {128, 184}, {255, 184},
    {1, 172}, {128, 172}, {255, 172},
    {1, 72}, {128, 72}, {255, 72},
};

constexpr StickPoint kMY2Table[9] = {
    {1, 165}, {128, 165}, {255, 165},
    {1, 172}, {128, 172}, {255, 172},
    {1, 91}, {128, 91}, {255, 91},
};

constexpr StickPoint kTilt1Table[9] = {
    {187, 87}, {128, 87}, {69, 87},
    {187, 128}, {128, 128}, {69, 128},
    {187, 169}, {128, 169}, {69, 169},
};

constexpr StickPoint kTilt2Table[9] = {
    {88, 79}, {128, 79}, {168, 79},
    {88, 128}, {128, 128}, {168, 128},
    {88, 177}, {128, 177}, {168, 177},
};

constexpr StickPoint kTilt3Table[9] = {
    {75, 86}, {128, 86}, {181, 86},
    {75, 128}, {128, 128}, {181, 128},
    {75, 170}, {128, 170}, {181, 170},
};

constexpr StickPoint kMTilt1Table[9] = {
    {95, 81}, {128, 81}, {161, 81},
    {95, 172}, {128, 172}, {161, 172},
    {95, 175}, {128, 175}, {161, 175},
};

constexpr StickPoint kMTilt2Table[9] = {
    {95, 81}, {128, 81}, {161, 81},
    {95, 172}, {128, 172}, {161, 172},
    {95, 175}, {128, 175}, {161, 175},
};

constexpr StickPoint kMTilt3Table[9] = {
    {96, 82}, {128, 82}, {160, 82},
    {96, 172}, {128, 172}, {160, 172},
    {96, 174}, {128, 174}, {160, 174},
};

constexpr size_t kDirectionFiveIndex = 4;

enum class EffectiveModifier {
    None,
    X1,
    X2,
    Y1,
    Y2,
    Tilt1,
    Tilt2,
    Tilt3,
};

const StickPoint *SelectStickTable(
    bool mode_active,
    bool x1_active,
    bool x2_active,
    bool y1_active,
    bool y2_active,
    bool tilt1_effective,
    bool tilt2_effective,
    bool tilt3_effective
) {
    int active_modifier_count = 0;
    EffectiveModifier single_modifier = EffectiveModifier::None;

    if (x1_active) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::X1;
    }
    if (x2_active) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::X2;
    }
    if (y1_active) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::Y1;
    }
    if (y2_active) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::Y2;
    }

    if (tilt3_effective) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::Tilt3;
    } else if (tilt1_effective) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::Tilt1;
    } else if (tilt2_effective) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::Tilt2;
    }

    if (active_modifier_count != 1) {
        return mode_active ? kModeDefaultTable : kDefaultTable;
    }

    if (!mode_active) {
        switch (single_modifier) {
            case EffectiveModifier::X1:
                return kX1Table;
            case EffectiveModifier::X2:
                return kX2Table;
            case EffectiveModifier::Y1:
                return kY1Table;
            case EffectiveModifier::Y2:
                return kY2Table;
            case EffectiveModifier::Tilt1:
                return kTilt1Table;
            case EffectiveModifier::Tilt2:
                return kTilt2Table;
            case EffectiveModifier::Tilt3:
                return kTilt3Table;
            default:
                return kDefaultTable;
        }
    }

    switch (single_modifier) {
        case EffectiveModifier::X1:
            return kMX1Table;
        case EffectiveModifier::X2:
            return kMX2Table;
        case EffectiveModifier::Y1:
            return kMY1Table;
        case EffectiveModifier::Y2:
            return kMY2Table;
        case EffectiveModifier::Tilt1:
            return kMTilt1Table;
        case EffectiveModifier::Tilt2:
            return kMTilt2Table;
        case EffectiveModifier::Tilt3:
            return kMTilt3Table;
        default:
            return kModeDefaultTable;
    }
}

size_t DirectionIndexFromAxes(int8_t x_axis, int8_t y_axis) {
    int x = static_cast<int>(x_axis);
    int y = static_cast<int>(y_axis);

    if (x < -1) {
        x = -1;
    } else if (x > 1) {
        x = 1;
    }

    if (y < -1) {
        y = -1;
    } else if (y > 1) {
        y = 1;
    }

    const int index = ((y + 1) * 3) + (x + 1);
    return static_cast<size_t>(index);
}

} // namespace

Ultimate::Ultimate() : ControllerMode() {}

void Ultimate::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    outputs.a = inputs.rt1;
    outputs.b = inputs.rf1;
    outputs.x = inputs.rf2;
    outputs.y = inputs.rf6;
    outputs.buttonL = inputs.lt1;
    outputs.buttonR = inputs.rf3;
    outputs.triggerLDigital = inputs.lf4;
    outputs.triggerRDigital = inputs.rf5;

    outputs.start = inputs.mb7;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;

    outputs.dpadUp = 0;
    outputs.dpadDown = 0;
    outputs.dpadLeft = 0;
    outputs.dpadRight = 0;

    // Preserve source-backed nunchuk C D-pad layer behavior.
    if (inputs.nunchuk_c) {
        outputs.dpadUp = inputs.rt4;
        outputs.dpadDown = inputs.rt2;
        outputs.dpadLeft = inputs.rt3;
        outputs.dpadRight = inputs.rt5;
    }

    // Preserve direct D-pad left/right inputs.
    outputs.dpadLeft |= inputs.lf8;
    outputs.dpadRight |= inputs.lf6;

    const bool ls_to_dpad_active = inputs.rf7;
    if (ls_to_dpad_active) {
        outputs.dpadUp |= inputs.rf4;
        outputs.dpadDown |= inputs.lf2;
        outputs.dpadLeft |= inputs.lf3;
        outputs.dpadRight |= inputs.lf1;
    }

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

void Ultimate::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    (void)backend_id;

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
        outputs
    );

    // Senscope Glyph Smash Box runtime begin
    const bool mode_active = inputs.rf8;
    const bool x1_active = inputs.lt5;
    const bool x2_active = inputs.lt4;
    const bool y1_active = inputs.lt2;
    const bool y2_active = inputs.lt3;
    const bool ls_to_dpad_active = inputs.rf7;

    const bool tilt1_pressed = inputs.rf3;
    const bool tilt2_pressed = inputs.rf4;

    const bool tilt3_effective = tilt1_pressed && tilt2_pressed;
    const bool tilt1_effective = tilt1_pressed && !tilt2_pressed;
    const bool tilt2_effective = tilt2_pressed && !tilt1_pressed;

    const StickPoint *active_table = SelectStickTable(
        mode_active,
        x1_active,
        x2_active,
        y1_active,
        y2_active,
        tilt1_effective,
        tilt2_effective,
        tilt3_effective
    );

    if (ls_to_dpad_active) {
        const StickPoint center = mode_active ? kModeDefaultTable[kDirectionFiveIndex] : kDefaultTable[kDirectionFiveIndex];
        outputs.leftStickX = center.x;
        outputs.leftStickY = center.y;
    } else {
        const size_t direction_index = DirectionIndexFromAxes(directions.x, directions.y);
        outputs.leftStickX = active_table[direction_index].x;
        outputs.leftStickY = active_table[direction_index].y;
    }
    // Senscope Glyph Smash Box runtime end

    // C-stick ASDI Slideoff angle overrides any other C-stick modifiers (such as
    // angled fsmash).
    if (directions.cx != 0 && directions.cy != 0) {
        // 5250 8500 = 42 68
        outputs.rightStickX = 128 + (directions.cx * 42);
        outputs.rightStickY = 128 + (directions.cy * 68);
    }

    if (inputs.lf4) {
        outputs.triggerLAnalog = 140;
    } else {
        outputs.triggerLAnalog = 0;
    }

    if (inputs.rf5) {
        outputs.triggerRAnalog = 140;
    } else {
        outputs.triggerRAnalog = 0;
    }

    // Shut off C-stick when using D-Pad layer.
    if (inputs.nunchuk_c) {
        outputs.rightStickX = 128;
        outputs.rightStickY = 128;
    }

    // Nunchuk overrides left stick.
    if (inputs.nunchuk_connected) {
        outputs.leftStickX = inputs.nunchuk_x;
        outputs.leftStickY = inputs.nunchuk_y;
    }
}
