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

// Keep the generated-like table constants local to this translation unit.
#include "modes/UltimateIdentityRuntimeTables.hpp"

constexpr StickPoint kTilt1Minus41Table[9] = {
    {87, 47}, {87, 47}, {87, 47},
    {87, 128}, {87, 128}, {87, 128},
    {87, 209}, {87, 209}, {87, 209},
};

// RT1+RF4 custom modifier. Direction 5 is source-encoded center because table
// selection requires a 9-point table and the requested neutral behavior is unchanged.
constexpr StickPoint kRT1RF4CustomTable[9] = {
    {69, 78}, {128, 78}, {187, 78},
    {69, 128}, {128, 128}, {187, 128},
    {72, 172}, {128, 179}, {184, 172},
};

constexpr size_t kDirectionTwoIndex = 1;
constexpr size_t kDirectionFiveIndex = 4;
constexpr size_t kDirectionEightIndex = 7;

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

struct LayerState {
    bool layer_left_active;
    bool layer_right_active;
    bool layer_direction_active;
    bool lf4_submode_active;
    bool layer_transform_active;
    bool c_stick_any_active;
    bool rf2_suppressed_by_lf4_submode_cstick;
};

struct EffectiveDirectionState {
    bool left;
    bool right;
    bool up;
    bool down;
    bool force_up_active;
    int8_t horizontal_axis;
};

struct RoleState {
    bool mode_active;
    bool x1_active;
    bool x2_active;
    bool y1_active;
    bool layer_rf3_normal_x_active;
    bool rf4_layer_flipper_active;
    bool tilt1_effective;
    bool tilt2_effective;
    bool tilt3_effective;
    bool z_airdodge_override_active;
    bool null_modifier_active;
    bool hard_up_b_active;
    bool ls_to_dpad_active;
    bool direction_plus_a_active;
    bool direction_plus_a_force_up;
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

LayerState ResolveLayerState(const InputState &inputs) {
    LayerState state;
    state.layer_left_active = false;
    state.layer_right_active = false;
    state.layer_direction_active = state.layer_left_active || state.layer_right_active;
    state.lf4_submode_active = inputs.lf4;
    state.layer_transform_active = (inputs.lt2 && !inputs.lf4) || state.lf4_submode_active;
    state.c_stick_any_active = inputs.rt2 || inputs.rt3 || inputs.rt4 || inputs.rt5;
    state.rf2_suppressed_by_lf4_submode_cstick = state.lf4_submode_active && state.c_stick_any_active;
    return state;
}

EffectiveDirectionState ResolveEffectiveDirections(const InputState &inputs, const LayerState &layer) {
    const bool lt2_rf2_force_up_active = inputs.lt2 && !inputs.lf4 && inputs.rf2;
    const bool lf4_submode_rf3_force_up_active = inputs.lf4 && inputs.rf3;

    EffectiveDirectionState state;
    state.force_up_active = inputs.rf5 || lt2_rf2_force_up_active || lf4_submode_rf3_force_up_active;
    state.horizontal_axis = ResolveHorizontalAxis(inputs.lf3, inputs.lf1, layer.layer_left_active, layer.layer_right_active);
    state.up = inputs.lf2 || state.force_up_active;
    state.down = (inputs.lf5 || inputs.lt6) && !state.force_up_active;
    state.left = state.horizontal_axis < 0;
    state.right = state.horizontal_axis > 0;
    return state;
}

RoleState ResolveRoleState(const InputState &inputs, const LayerState &layer, const EffectiveDirectionState &directions) {
    (void)layer;
    const bool down_a_active = inputs.lt6;
    const bool up_a_active = inputs.rf5;
    const bool lt2_sublayer_active = inputs.lt2 && !inputs.lf4 && (inputs.rf1 || inputs.rf2 || inputs.rf3 || inputs.rf4);
    const bool lt2_rf3_active = inputs.lt2 && !inputs.lf4 && inputs.rf3;
    const bool lt2_rf4_active = inputs.lt2 && !inputs.lf4 && inputs.rf4;
    const bool lf4_rf2_deactivates_rf4 = inputs.lf4 && inputs.rf2;
    const bool tilt1_pressed = inputs.rf4 && (!inputs.lt2 || inputs.lf4) && !inputs.rt1 && !lf4_rf2_deactivates_rf4;
    const bool tilt2_pressed = inputs.rt1 && !inputs.rf4;

    RoleState state;
    state.mode_active = inputs.rf8;
    state.x1_active = inputs.lt5;
    state.x2_active = inputs.lt4;
    state.y1_active = inputs.lt2 && !inputs.lf4 && !lt2_sublayer_active;
    state.layer_rf3_normal_x_active = lt2_rf3_active;
    state.rf4_layer_flipper_active = lt2_rf4_active;
    state.tilt3_effective = false;
    state.tilt1_effective = tilt1_pressed;
    state.tilt2_effective = tilt2_pressed;
    state.z_airdodge_override_active = inputs.rf6;
    state.null_modifier_active = inputs.rf9 && !inputs.rf4;
    state.hard_up_b_active = inputs.rf7;
    state.ls_to_dpad_active = inputs.rf13;
    state.direction_plus_a_active = down_a_active || up_a_active;
    state.direction_plus_a_force_up = state.direction_plus_a_active && (up_a_active || directions.force_up_active);
    return state;
}

void ApplyDigitalButtonOutputs(const InputState &inputs, const LayerState &layer, OutputState &outputs) {
    const bool lt2_sublayer_active = inputs.lt2 && !inputs.lf4 && (inputs.rf1 || inputs.rf2 || inputs.rf3 || inputs.rf4);
    const bool lt2_rf1_x_active = inputs.lt2 && !inputs.lf4 && inputs.rf1 && !layer.c_stick_any_active;
    const bool lf4_rf2_x_active = inputs.lf4 && inputs.rf2 && !layer.c_stick_any_active;
    const bool base_rf1_a_active = inputs.rf1 && !lt2_sublayer_active;
    const bool base_rf2_b_active = inputs.rf2 && !inputs.lt2 && !inputs.lf4;
    const bool base_rf3_x_active = inputs.rf3 && !inputs.lt2 && !inputs.lf4;

    outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;
    outputs.b = base_rf2_b_active || inputs.lf4 || inputs.rf7 || (inputs.lt2 && !inputs.lf4 && inputs.rf3);
    outputs.x = base_rf3_x_active || lt2_rf1_x_active || lf4_rf2_x_active;
    outputs.y = inputs.rf10;
    outputs.buttonL = inputs.lt1 || inputs.lt3;
    // GameCube/N64 backends serialize buttonR as Z; triggerRDigital as R.
    outputs.buttonR = inputs.rf6;
    outputs.triggerLDigital = inputs.lt1 || inputs.lt3;
    outputs.triggerRDigital = inputs.rf16 || inputs.lt3;

    outputs.start = inputs.mb7;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;
}

void ApplyDpadOutputs(const InputState &inputs, const EffectiveDirectionState &directions, const RoleState &roles, OutputState &outputs) {
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

    if (roles.ls_to_dpad_active) {
        outputs.dpadUp |= directions.up;
        outputs.dpadDown |= directions.down;
        outputs.dpadLeft |= directions.left;
        outputs.dpadRight |= directions.right;
    }
}

void ApplyDigitalDirectionOutputs(const EffectiveDirectionState &directions, const RoleState &roles, OutputState &outputs) {
    outputs.leftStickLeft = roles.ls_to_dpad_active ? false : directions.left;
    outputs.leftStickRight = roles.ls_to_dpad_active ? false : directions.right;
    outputs.leftStickDown = roles.ls_to_dpad_active ? false : directions.down;
    outputs.leftStickUp = roles.ls_to_dpad_active ? false : directions.up;
}

void ApplyRightStickDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    outputs.rightStickLeft = inputs.rt3;
    outputs.rightStickRight = inputs.rt4;
    outputs.rightStickDown = inputs.rt2;
    outputs.rightStickUp = inputs.rt5;

    outputs.modX = false;
    outputs.modY = false;
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
    if (tilt1_effective && tilt2_effective) {
        return kRT1RF4CustomTable;
    }

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
            return kModeDefaultTable;
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

void ApplyTableAnalogOutput(const StickPoint *active_table, int8_t x_axis, int8_t y_axis, OutputState &outputs) {
    const size_t direction_index = DirectionIndexFromAxes(x_axis, y_axis);
    outputs.leftStickX = active_table[direction_index].x;
    outputs.leftStickY = active_table[direction_index].y;
}

void ApplyDirectionPlusAOverride(const RoleState &roles, OutputState &outputs) {
    if (!roles.direction_plus_a_active) {
        return;
    }

    const StickPoint *direction_plus_a_table = roles.mode_active ? kModeDefaultTable : kDefaultTable;
    const size_t direction_plus_a_index = roles.direction_plus_a_force_up ? kDirectionEightIndex : kDirectionTwoIndex;
    outputs.leftStickX = direction_plus_a_table[direction_plus_a_index].x;
    outputs.leftStickY = direction_plus_a_table[direction_plus_a_index].y;
}

void ApplyZAirdodgeOverride(const EffectiveDirectionState &directions, OutputState &outputs) {
    const int8_t lt1_x = directions.left == directions.right ? 0 : (directions.left ? -1 : 1);
    const int8_t lt1_y = directions.down == directions.up ? 0 : (directions.down ? -1 : 1);
    const size_t lt1_direction_index = DirectionIndexFromAxes(lt1_x, lt1_y);
    outputs.leftStickX = kLt1LowMagnitudeTable[lt1_direction_index].x;
    outputs.leftStickY = kLt1LowMagnitudeTable[lt1_direction_index].y;
}

void ApplyHardUpBOverride(const EffectiveDirectionState &directions, OutputState &outputs) {
    // RF7 is a hard Up+B analog override with horizontal from effective direction.
    const uint8_t rf7_horizontal = directions.left == directions.right ? 128 : (directions.left ? 77 : 179);
    outputs.leftStickX = rf7_horizontal;
    outputs.leftStickY = 172;
}

void ApplyNullOverride(OutputState &outputs) {
    outputs.leftStickX = 128;
    outputs.leftStickY = 128;
    outputs.rightStickX = 128;
    outputs.rightStickY = 128;
}

} // namespace

Ultimate::Ultimate() : ControllerMode() {}

void Ultimate::UpdateDigitalOutputs(const InputState &inputs, OutputState &outputs) {
    // Digital priority: physical inputs, LF4 sub-mode,
    // forced-Up resolution, button carriers, then optional LS->DPad routing.
    const LayerState layer = ResolveLayerState(inputs);
    const EffectiveDirectionState effective_directions = ResolveEffectiveDirections(inputs, layer);
    const RoleState roles = ResolveRoleState(inputs, layer, effective_directions);

    ApplyDigitalButtonOutputs(inputs, layer, outputs);
    ApplyDpadOutputs(inputs, effective_directions, roles, outputs);
    ApplyDigitalDirectionOutputs(effective_directions, roles, outputs);
    ApplyRightStickDigitalOutputs(inputs, outputs);
}

void Ultimate::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    (void)backend_id;
    const LayerState layer = ResolveLayerState(inputs);
    const EffectiveDirectionState effective_directions = ResolveEffectiveDirections(inputs, layer);
    const RoleState roles = ResolveRoleState(inputs, layer, effective_directions);

    // Coordinate calculations to make modifier handling simpler.
    UpdateDirections(
        effective_directions.left, // Left (LF3 with cancellation)
        effective_directions.right, // Right (LF1 with cancellation)
        effective_directions.down, // Down (LT6/LF5, suppressed by forced-Up)
        effective_directions.up, // Up (RF5, LT2+RF2, and LF4+RF3 forced-Up)
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
    // Analog priority: table output, direction-plus-A, RF6 low magnitude,
    // RF7 hard Up+B, C-stick ASDI, RF9 null, then the pre-existing nunchuk override below.
    const bool rt1_rf4_custom_active = inputs.rt1 && inputs.rf4;
    const bool rf4_rf2_minus41_active = inputs.rf4 && inputs.rf2 && !inputs.lt2 && !inputs.lf4 && !inputs.rt1;
    const StickPoint *active_table = SelectStickTable(
        roles.mode_active,
        roles.x1_active,
        roles.x2_active,
        roles.y1_active,
        roles.layer_rf3_normal_x_active,
        roles.rf4_layer_flipper_active,
        rt1_rf4_custom_active || (roles.tilt1_effective && !rf4_rf2_minus41_active),
        rt1_rf4_custom_active || roles.tilt2_effective,
        roles.tilt3_effective
    );
    if (rf4_rf2_minus41_active) {
        active_table = kTilt1Minus41Table;
    }

    if (roles.ls_to_dpad_active) {
        const StickPoint center = roles.mode_active ? kModeDefaultTable[kDirectionFiveIndex] : kDefaultTable[kDirectionFiveIndex];
        outputs.leftStickX = center.x;
        outputs.leftStickY = center.y;
    } else {
        ApplyTableAnalogOutput(active_table, directions.x, directions.y, outputs);
        ApplyDirectionPlusAOverride(roles, outputs);

        if (roles.z_airdodge_override_active) {
            ApplyZAirdodgeOverride(effective_directions, outputs);
        }

        if (roles.hard_up_b_active) {
            ApplyHardUpBOverride(effective_directions, outputs);
        }
    }

    // C-stick ASDI Slideoff angle overrides any other C-stick modifiers (such as
    // angled fsmash).
    if (directions.cx != 0 && directions.cy != 0) {
        // 5250 8500 = 42 68
        outputs.rightStickX = 128 + (directions.cx * 42);
        outputs.rightStickY = 128 + (directions.cy * 68);
    }

    if (roles.null_modifier_active) {
        ApplyNullOverride(outputs);
    }
    // Senscope Glyph Smash Box runtime end

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
