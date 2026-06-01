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
    {14, 87}, {128, 87}, {242, 87},
    {14, 169}, {128, 169}, {242, 169},
    {14, 169}, {128, 169}, {242, 169},
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
    {78, 87}, {128, 87}, {178, 87},
    {78, 169}, {128, 169}, {178, 169},
    {78, 169}, {128, 169}, {178, 169},
};

constexpr StickPoint kMX2Table[9] = {
    {65, 87}, {128, 87}, {191, 87},
    {65, 169}, {128, 169}, {191, 169},
    {65, 169}, {128, 169}, {191, 169},
};

constexpr StickPoint kY1Table[9] = {
    {61, 99}, {128, 99}, {195, 99},
    {61, 128}, {128, 128}, {195, 128},
    {61, 157}, {128, 157}, {195, 157},
};

constexpr StickPoint kMY1Table[9] = {
    {14, 179}, {128, 179}, {242, 179},
    {14, 169}, {128, 169}, {242, 169},
    {14, 77}, {128, 77}, {242, 77},
};

// RF3 under LF7/LF8 layer is a normal x-only 41px modifier over default y rows.
constexpr StickPoint kLayerNormalXTable[9] = {
    {87, 51}, {128, 51}, {169, 51},
    {87, 128}, {128, 128}, {169, 128},
    {87, 205}, {128, 205}, {169, 205},
};

constexpr StickPoint kMLayerNormalXTable[9] = {
    {87, 87}, {128, 87}, {169, 87},
    {87, 169}, {128, 169}, {169, 169},
    {87, 169}, {128, 169}, {169, 169},
};

// RF4 under LF7/LF8 layer is an x-only flipper modifier over default y rows.
constexpr StickPoint kLayerFlipperTable[9] = {
    {169, 51}, {128, 51}, {87, 51},
    {169, 128}, {128, 128}, {87, 128},
    {169, 205}, {128, 205}, {87, 205},
};

constexpr StickPoint kMLayerFlipperTable[9] = {
    {169, 87}, {128, 87}, {87, 87},
    {169, 169}, {128, 169}, {87, 169},
    {169, 169}, {128, 169}, {87, 169},
};

constexpr StickPoint kY1Tilt1Table[9] = {
    {169, 99}, {128, 99}, {87, 99},
    {169, 128}, {128, 128}, {87, 128},
    {169, 157}, {128, 157}, {87, 157},
};

constexpr StickPoint kMY1Tilt1Table[9] = {
    {169, 179}, {128, 179}, {87, 179},
    {169, 169}, {128, 169}, {87, 169},
    {169, 77}, {128, 77}, {87, 77},
};

constexpr StickPoint kY1LayerFlipperTable[9] = {
    {169, 99}, {128, 99}, {87, 99},
    {169, 128}, {128, 128}, {87, 128},
    {169, 157}, {128, 157}, {87, 157},
};

constexpr StickPoint kMY1LayerFlipperTable[9] = {
    {169, 179}, {128, 179}, {87, 179},
    {169, 169}, {128, 169}, {87, 169},
    {169, 77}, {128, 77}, {87, 77},
};

constexpr StickPoint kY1LayerNormalXTable[9] = {
    {87, 99}, {128, 99}, {169, 99},
    {87, 128}, {128, 128}, {169, 128},
    {87, 157}, {128, 157}, {169, 157},
};

constexpr StickPoint kMY1LayerNormalXTable[9] = {
    {87, 179}, {128, 179}, {169, 179},
    {87, 169}, {128, 169}, {169, 169},
    {87, 77}, {128, 77}, {169, 77},
};

constexpr StickPoint kTilt1Table[9] = {
    {187, 47}, {128, 47}, {69, 47},
    {187, 128}, {128, 128}, {69, 128},
    {187, 209}, {128, 209}, {69, 209},
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
    {169, 88}, {128, 88}, {87, 88},
    {169, 169}, {128, 169}, {87, 169},
    {169, 168}, {128, 168}, {87, 168},
};

constexpr StickPoint kMTilt2Table[9] = {
    {96, 82}, {128, 82}, {160, 82},
    {96, 169}, {128, 169}, {160, 169},
    {96, 174}, {128, 174}, {160, 174},
};

constexpr StickPoint kMTilt3Table[9] = {
    {96, 86}, {128, 86}, {160, 86},
    {96, 169}, {128, 169}, {160, 169},
    {96, 170}, {128, 170}, {160, 170},
};

constexpr size_t kDirectionTwoIndex = 1;
constexpr size_t kDirectionFiveIndex = 4;
constexpr size_t kDirectionEightIndex = 7;

// LT5/RF11 provide Z plus a low-magnitude left-stick override for neutral-airdodge-safe output.
constexpr StickPoint kLt1LowMagnitudeTable[9] = {
    {89, 89}, {128, 79}, {167, 89},
    {79, 128}, {128, 128}, {177, 128},
    {89, 167}, {128, 177}, {167, 167},
};

enum class EffectiveModifier {
    None,
    X1,
    X2,
    Y1,
    LayerNormalX,
    LayerFlipper,
    Tilt1,
    Tilt2,
    Tilt3,
};

int8_t ResolveHorizontalAxis(
    bool base_left_active,
    bool base_right_active,
    bool layer_left_active,
    bool layer_right_active
) {
    const int horizontal_score = static_cast<int>(base_right_active) - static_cast<int>(base_left_active)
        + static_cast<int>(layer_right_active) - static_cast<int>(layer_left_active);

    if (horizontal_score < 0) {
        return -1;
    }
    if (horizontal_score > 0) {
        return 1;
    }
    return 0;
}

const StickPoint *SelectStickTable(
    bool mode_active,
    bool x1_active,
    bool x2_active,
    bool y1_active,
    bool layer_normal_x_active,
    bool layer_flipper_active,
    bool tilt1_effective,
    bool tilt2_effective,
    bool tilt3_effective
) {
    const bool y1_tilt1_special_active = y1_active && tilt1_effective && !x1_active && !x2_active && !tilt2_effective && !tilt3_effective;
    if (y1_tilt1_special_active) {
        return mode_active ? kMY1Tilt1Table : kY1Tilt1Table;
    }

    const bool layer_flipper_effective = layer_flipper_active;
    const bool layer_normal_x_effective = layer_normal_x_active && !layer_flipper_effective;

    const bool y1_layer_normal_x_special_active = y1_active && layer_normal_x_effective
        && !x1_active && !x2_active && !tilt1_effective && !tilt2_effective && !tilt3_effective;
    if (y1_layer_normal_x_special_active) {
        return mode_active ? kMY1LayerNormalXTable : kY1LayerNormalXTable;
    }

    const bool y1_layer_flipper_special_active = y1_active && layer_flipper_effective
        && !x1_active && !x2_active && !tilt1_effective && !tilt2_effective && !tilt3_effective;
    if (y1_layer_flipper_special_active) {
        return mode_active ? kMY1LayerFlipperTable : kY1LayerFlipperTable;
    }

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
    if (layer_normal_x_effective) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::LayerNormalX;
    }
    if (layer_flipper_effective) {
        active_modifier_count++;
        single_modifier = EffectiveModifier::LayerFlipper;
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
            case EffectiveModifier::LayerNormalX:
                return kLayerNormalXTable;
            case EffectiveModifier::LayerFlipper:
                return kLayerFlipperTable;
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
        case EffectiveModifier::LayerNormalX:
            return kMLayerNormalXTable;
        case EffectiveModifier::LayerFlipper:
            return kMLayerFlipperTable;
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
    const bool layer_left_active = inputs.lf8;
    const bool layer_right_active = inputs.lf7;
    const bool layer_active = layer_left_active || layer_right_active;
    const bool layer_rf2_force_up_active = layer_active && inputs.rf2;
    const bool force_up_active = inputs.rf6 || inputs.rf12 || inputs.rf15 || layer_rf2_force_up_active;
    const int8_t horizontal_axis = ResolveHorizontalAxis(inputs.lf3, inputs.lf1, layer_left_active, layer_right_active);
    const bool effective_ls_up = inputs.lf2 || force_up_active;
    const bool effective_ls_down = (inputs.lf5 || inputs.lt6) && !force_up_active;
    const bool effective_ls_left = horizontal_axis < 0;
    const bool effective_ls_right = horizontal_axis > 0;
    const bool ls_to_dpad_active = inputs.rf7;

    outputs.a = inputs.rf1 || inputs.lt6 || inputs.rf12 || inputs.rf15;
    outputs.b = inputs.rf5 || inputs.lf4 || (layer_active && inputs.rf3);
    outputs.x = inputs.rf2 && !layer_active;
    outputs.y = inputs.rf10;
    outputs.buttonL = inputs.lt3;
    // GameCube/N64 backends serialize buttonR as Z; triggerRDigital as R.
    outputs.buttonR = inputs.rt1 || inputs.lt5 || inputs.rf11;
    outputs.triggerLDigital = inputs.lt3;
    outputs.triggerRDigital = inputs.rf16;

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
        outputs.dpadUp = inputs.rt5;
        outputs.dpadDown = inputs.rt2;
        outputs.dpadLeft = inputs.rt3;
        outputs.dpadRight = inputs.rt4;
    }

    if (ls_to_dpad_active) {
        outputs.dpadUp |= effective_ls_up;
        outputs.dpadDown |= effective_ls_down;
        outputs.dpadLeft |= effective_ls_left;
        outputs.dpadRight |= effective_ls_right;
    }

    outputs.leftStickLeft = ls_to_dpad_active ? false : effective_ls_left;
    outputs.leftStickRight = ls_to_dpad_active ? false : effective_ls_right;
    outputs.leftStickDown = ls_to_dpad_active ? false : effective_ls_down;
    outputs.leftStickUp = ls_to_dpad_active ? false : effective_ls_up;

    outputs.rightStickLeft = inputs.rt3;
    outputs.rightStickRight = inputs.rt4;
    outputs.rightStickDown = inputs.rt2;
    outputs.rightStickUp = inputs.rt5;

    outputs.modX = false;
    outputs.modY = false;
}

void Ultimate::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    (void)backend_id;
    const bool layer_left_active = inputs.lf8;
    const bool layer_right_active = inputs.lf7;
    const bool layer_active = layer_left_active || layer_right_active;
    const bool layer_rf2_force_up_active = layer_active && inputs.rf2;
    const bool force_up_active = inputs.rf6 || inputs.rf12 || inputs.rf15 || layer_rf2_force_up_active;
    const bool effective_ls_up = inputs.lf2 || force_up_active;
    const bool effective_ls_down = (inputs.lf5 || inputs.lt6) && !force_up_active;
    const int8_t horizontal_axis = ResolveHorizontalAxis(inputs.lf3, inputs.lf1, layer_left_active, layer_right_active);
    const bool effective_ls_left = horizontal_axis < 0;
    const bool effective_ls_right = horizontal_axis > 0;

    // Coordinate calculations to make modifier handling simpler.
    UpdateDirections(
        effective_ls_left, // Left (LF3 + LF8 layer-left contribution with cancellation)
        effective_ls_right, // Right (LF1 + LF7 layer-right contribution with cancellation)
        effective_ls_down, // Down (LT6/LF5, suppressed by forced-Up)
        effective_ls_up, // Up (RF6/RF12/RF15 and layer RF2 forced-Up)
        inputs.rt3, // C-Left
        inputs.rt4, // C-Right
        inputs.rt2, // C-Down
        inputs.rt5, // C-Up
        ANALOG_STICK_MIN,
        ANALOG_STICK_NEUTRAL,
        ANALOG_STICK_MAX,
        outputs
    );

    // Senscope Glyph Smash Box runtime begin
    const bool mode_active = inputs.rf8;
    const bool x1_active = inputs.lt4;
    const bool x2_active = inputs.lt1;
    const bool y1_active = inputs.lt2;
    const bool z_airdodge_override_active = inputs.lt5 || inputs.rf11;
    const bool null_modifier_active = inputs.rf9;
    const bool ls_to_dpad_active = inputs.rf7;
    const bool down_a_active = inputs.lt6;
    const bool up_a_active = inputs.rf12 || inputs.rf15;
    const bool direction_plus_a_active = down_a_active || up_a_active;
    const bool direction_plus_a_force_up = direction_plus_a_active && (up_a_active || force_up_active);

    const bool layer_rf3_normal_x_active = layer_active && inputs.rf3;
    const bool rf4_layer_flipper_active = layer_active && inputs.rf4;
    const bool tilt1_pressed = inputs.rf3 && !layer_active;
    const bool tilt2_pressed = inputs.rf4 && !layer_active;

    const bool tilt3_effective = tilt1_pressed && tilt2_pressed;
    const bool tilt1_effective = tilt1_pressed && !tilt2_pressed;
    const bool tilt2_effective = tilt2_pressed && !tilt1_pressed;

    const StickPoint *active_table = SelectStickTable(
        mode_active,
        x1_active,
        x2_active,
        y1_active,
        layer_rf3_normal_x_active,
        rf4_layer_flipper_active,
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

        if (direction_plus_a_active) {
            const StickPoint *direction_plus_a_table = mode_active ? kModeDefaultTable : kDefaultTable;
            const size_t direction_plus_a_index = direction_plus_a_force_up ? kDirectionEightIndex : kDirectionTwoIndex;
            outputs.leftStickX = direction_plus_a_table[direction_plus_a_index].x;
            outputs.leftStickY = direction_plus_a_table[direction_plus_a_index].y;
        }

        if (z_airdodge_override_active) {
            const bool lt1_force_up_active = force_up_active;
            const bool lt1_effective_left = effective_ls_left;
            const bool lt1_effective_right = effective_ls_right;
            const bool lt1_effective_up = inputs.lf2 || lt1_force_up_active;
            const bool lt1_effective_down = (inputs.lf5 || inputs.lt6) && !lt1_force_up_active;
            const int8_t lt1_x = lt1_effective_left == lt1_effective_right ? 0 : (lt1_effective_left ? -1 : 1);
            const int8_t lt1_y = lt1_effective_down == lt1_effective_up ? 0 : (lt1_effective_down ? -1 : 1);
            const size_t lt1_direction_index = DirectionIndexFromAxes(lt1_x, lt1_y);
            outputs.leftStickX = kLt1LowMagnitudeTable[lt1_direction_index].x;
            outputs.leftStickY = kLt1LowMagnitudeTable[lt1_direction_index].y;
        }
    }

    if (null_modifier_active) {
        outputs.leftStickX = 128;
        outputs.leftStickY = 128;
    }
    // Senscope Glyph Smash Box runtime end

    // C-stick ASDI Slideoff angle overrides any other C-stick modifiers (such as
    // angled fsmash).
    if (directions.cx != 0 && directions.cy != 0) {
        // 5250 8500 = 42 68
        outputs.rightStickX = 128 + (directions.cx * 42);
        outputs.rightStickY = 128 + (directions.cy * 68);
    }

    if (outputs.triggerLDigital) {
        outputs.triggerLAnalog = 140;
    } else {
        outputs.triggerLAnalog = 0;
    }

    if (outputs.triggerRDigital) {
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
