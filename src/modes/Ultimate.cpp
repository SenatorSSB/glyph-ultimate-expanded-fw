/* Ultimate profile by Taker */
#include "modes/Ultimate.hpp"
#include <config.pb.h>

#define ANALOG_STICK_MIN 28
#define ANALOG_STICK_NEUTRAL 128
#define ANALOG_STICK_MAX 228

namespace {
struct RuntimeConfigView;

struct StickPoint {
    uint8_t x;
    uint8_t y;
};

enum class RuntimeConfigSource {
    KnownGoodFallback,
    SourceOwnedBaseline,
    SourceViewCandidate,
};

enum class RuntimeConfigActivationStatus {
    CandidateViewSelected,
    SourceOwnedSelected,
    FallbackSelected,
};

struct ActiveRuntimeConfigState {
    const RuntimeConfigView* active_view;
    RuntimeConfigSource source;
    RuntimeConfigActivationStatus status;
};

#include "modes/UltimateIdentityRuntimeTables.hpp"
#include "modes/UltimateRuntimeConfigInterpreter.hpp"

enum class RuntimeConfigCandidateStatus {
    Empty,
    SourceViewValid,
    SourceViewEquivalent,
    InvalidSourceView,
};

struct RuntimeConfigCandidateState {
    RuntimeConfigCandidateStatus status;
    StickPoint points[kRuntimeTableCount][kRuntimeTablePointCount];
    RuntimeTableView tables[kRuntimeTableCount];
    RuntimeConfigView view;
};

struct DiagnosticSourceViewCandidatePublicationState {
    RuntimeConfigCandidateState candidate;
    bool materialized;
    bool validated;
    bool equivalent_to_source_owned_baseline;
};

void ResetRuntimeConfigCandidateState(RuntimeConfigCandidateState &candidate) {
    candidate.status = RuntimeConfigCandidateStatus::Empty;
    for (size_t table_index = 0; table_index < kRuntimeTableCount; ++table_index) {
        for (size_t point_index = 0; point_index < kRuntimeTablePointCount; ++point_index) {
            candidate.points[table_index][point_index] = {ANALOG_STICK_NEUTRAL, ANALOG_STICK_NEUTRAL};
        }
        candidate.tables[table_index] = {
            kRuntimeTableIdOrder[table_index],
            kRuntimeTableSymbolNames[table_index],
            candidate.points[table_index],
            kRuntimeTablePointCount,
        };
    }
    candidate.view = {
        kRuntimeConfigSchemaName,
        kRuntimeConfigSchemaVersion,
        candidate.tables,
        0,
        RuntimeTableId::Default,
    };
}

bool ValidateRuntimeConfigCandidateState(const RuntimeConfigCandidateState &candidate) {
    if (
        candidate.status != RuntimeConfigCandidateStatus::SourceViewValid &&
        candidate.status != RuntimeConfigCandidateStatus::SourceViewEquivalent
    ) {
        return false;
    }
    return ValidateRuntimeConfigView(candidate.view);
}

bool RuntimeConfigViewsHaveEquivalentPoints(const RuntimeConfigView &lhs, const RuntimeConfigView &rhs) {
    if (!ValidateRuntimeConfigView(lhs) || !ValidateRuntimeConfigView(rhs)) {
        return false;
    }

    for (size_t table_index = 0; table_index < kRuntimeTableCount; ++table_index) {
        const RuntimeTableId table_id = kRuntimeTableIdOrder[table_index];
        const RuntimeTableView *lhs_table = FindRuntimeTableView(lhs, table_id);
        const RuntimeTableView *rhs_table = FindRuntimeTableView(rhs, table_id);
        if (lhs_table == nullptr || rhs_table == nullptr) {
            return false;
        }
        for (size_t point_index = 0; point_index < kRuntimeTablePointCount; ++point_index) {
            if (
                lhs_table->table[point_index].x != rhs_table->table[point_index].x ||
                lhs_table->table[point_index].y != rhs_table->table[point_index].y
            ) {
                return false;
            }
        }
    }

    return true;
}

bool MaterializeRuntimeConfigCandidateFromSourceView(
    const RuntimeConfigView &source_view,
    RuntimeConfigCandidateState &candidate
) {
    ResetRuntimeConfigCandidateState(candidate);
    if (!ValidateRuntimeConfigView(source_view)) {
        candidate.status = RuntimeConfigCandidateStatus::InvalidSourceView;
        return false;
    }

    for (size_t table_index = 0; table_index < kRuntimeTableCount; ++table_index) {
        const RuntimeTableView &source_table = source_view.tables[table_index];
        for (size_t point_index = 0; point_index < kRuntimeTablePointCount; ++point_index) {
            candidate.points[table_index][point_index] = source_table.table[point_index];
        }
        candidate.tables[table_index] = {
            source_table.id,
            source_table.symbol_name,
            candidate.points[table_index],
            source_table.point_count,
        };
    }
    candidate.view = {
        source_view.schema_name,
        source_view.schema_version,
        candidate.tables,
        kRuntimeTableCount,
        source_view.fallback_table_id,
    };

    candidate.status = ValidateRuntimeConfigView(candidate.view)
        ? RuntimeConfigCandidateStatus::SourceViewValid
        : RuntimeConfigCandidateStatus::InvalidSourceView;
    return candidate.status == RuntimeConfigCandidateStatus::SourceViewValid;
}

DiagnosticSourceViewCandidatePublicationState InitializeDiagnosticSourceViewCandidatePublicationState() {
    DiagnosticSourceViewCandidatePublicationState state = {
        {},
        false,
        false,
        false,
    };

    ResetRuntimeConfigCandidateState(state.candidate);
    state.materialized = MaterializeRuntimeConfigCandidateFromSourceView(
        kSourceOwnedCurrentBaselineRuntimeConfig,
        state.candidate
    );
    state.validated = state.materialized && ValidateRuntimeConfigCandidateState(state.candidate);
    state.equivalent_to_source_owned_baseline = state.validated &&
        RuntimeConfigViewsHaveEquivalentPoints(
            state.candidate.view,
            kSourceOwnedCurrentBaselineRuntimeConfig
        );
    if (state.equivalent_to_source_owned_baseline) {
        state.candidate.status = RuntimeConfigCandidateStatus::SourceViewEquivalent;
    }
    return state;
}

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
    bool rt1_rf4_custom_active;
    bool rf4_modifier_suppressed_by_cstick;
    bool rf4_behavior_available;
    bool base_rf3_x_active;
    bool rf9_base_rf3_x_mode_active;
    bool rf4_suppressed_by_rf9_rf3_mode;
    bool rf3_x_suppressed_by_rf9;
    bool rf3_x_restored_by_cstick;
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
    const bool base_rf3_x_active = inputs.rf3 && !inputs.lt2 && !inputs.lf4;
    const bool rf9_base_rf3_x_mode_active = inputs.rf9 && base_rf3_x_active;
    const bool rf4_suppressed_by_rf9_rf3_mode = rf9_base_rf3_x_mode_active && inputs.rf4;
    const bool rt1_rf4_custom_active = inputs.rt1 && inputs.rf4 && !rf4_suppressed_by_rf9_rf3_mode;
    const bool rf4_modifier_suppressed_by_cstick = inputs.rf4 && layer.c_stick_any_active && !rt1_rf4_custom_active;
    const bool rf4_behavior_available = inputs.rf4 && !rf4_modifier_suppressed_by_cstick && !rf4_suppressed_by_rf9_rf3_mode;
    const bool lt2_rf4_active = inputs.lt2 && !inputs.lf4 && rf4_behavior_available;
    const bool lf4_rf2_deactivates_rf4 = inputs.lf4 && inputs.rf2;
    const bool tilt1_pressed = rf4_behavior_available && (!inputs.lt2 || inputs.lf4) && !inputs.rt1 && !lf4_rf2_deactivates_rf4;
    const bool tilt2_pressed = inputs.rt1 && !inputs.rf4;
    const bool rf3_x_suppressed_by_rf9 = rf9_base_rf3_x_mode_active && !layer.c_stick_any_active;
    const bool rf3_x_restored_by_cstick = rf9_base_rf3_x_mode_active && layer.c_stick_any_active;

    RoleState state;
    state.mode_active = inputs.rf8;
    state.x1_active = inputs.lt5;
    state.x2_active = inputs.lt4;
    state.y1_active = inputs.lt2 && !inputs.lf4 && !lt2_sublayer_active;
    state.layer_rf3_normal_x_active = lt2_rf3_active;
    state.rf4_layer_flipper_active = lt2_rf4_active;
    state.rt1_rf4_custom_active = rt1_rf4_custom_active;
    state.rf4_modifier_suppressed_by_cstick = rf4_modifier_suppressed_by_cstick;
    state.rf4_behavior_available = rf4_behavior_available;
    state.base_rf3_x_active = base_rf3_x_active;
    state.rf9_base_rf3_x_mode_active = rf9_base_rf3_x_mode_active;
    state.rf4_suppressed_by_rf9_rf3_mode = rf4_suppressed_by_rf9_rf3_mode;
    state.rf3_x_suppressed_by_rf9 = rf3_x_suppressed_by_rf9;
    state.rf3_x_restored_by_cstick = rf3_x_restored_by_cstick;
    state.tilt3_effective = false;
    state.tilt1_effective = tilt1_pressed;
    state.tilt2_effective = tilt2_pressed;
    state.z_airdodge_override_active = inputs.rf6;
    state.null_modifier_active = inputs.rf9 && !state.rf9_base_rf3_x_mode_active && !state.rf4_behavior_available;
    state.hard_up_b_active = inputs.rf7;
    state.ls_to_dpad_active = inputs.rf13;
    state.direction_plus_a_active = down_a_active || up_a_active;
    state.direction_plus_a_force_up = state.direction_plus_a_active && (up_a_active || directions.force_up_active);
    return state;
}

void ApplyDigitalButtonOutputs(const InputState &inputs, const LayerState &layer, const RoleState &roles, OutputState &outputs) {
    const bool lt2_sublayer_active = inputs.lt2 && !inputs.lf4 && (inputs.rf1 || inputs.rf2 || inputs.rf3 || inputs.rf4);
    const bool lt2_rf1_x_active = inputs.lt2 && !inputs.lf4 && inputs.rf1 && !layer.c_stick_any_active;
    const bool lf4_rf2_x_active = inputs.lf4 && inputs.rf2 && !layer.c_stick_any_active;
    const bool base_rf1_a_active = inputs.rf1 && !lt2_sublayer_active;
    const bool base_rf2_b_active = inputs.rf2 && !inputs.lt2 && !inputs.lf4;

    outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5;
    outputs.b = base_rf2_b_active || inputs.lf4 || inputs.rf7 || (inputs.lt2 && !inputs.lf4 && inputs.rf3);
    outputs.x = (roles.base_rf3_x_active && !roles.rf3_x_suppressed_by_rf9) || lt2_rf1_x_active || lf4_rf2_x_active;
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

RuntimeTableId SelectRuntimeTableId(
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
        return RuntimeTableId::RT1RF4Custom;
    }

    const bool y1_tilt1_special_active = y1_active && tilt1_effective && !x1_active && !x2_active && !tilt2_effective && !tilt3_effective;
    if (y1_tilt1_special_active) {
        return mode_active ? RuntimeTableId::MY1Tilt1 : RuntimeTableId::Y1Tilt1;
    }

    const bool layer_flipper_effective = layer_flipper_active;
    const bool layer_normal_x_effective = layer_normal_x_active && !layer_flipper_effective;

    const bool y1_layer_normal_x_special_active = y1_active && layer_normal_x_effective
        && !x1_active && !x2_active && !tilt1_effective && !tilt2_effective && !tilt3_effective;
    if (y1_layer_normal_x_special_active) {
        return mode_active ? RuntimeTableId::MY1LayerNormalX : RuntimeTableId::Y1LayerNormalX;
    }

    const bool y1_layer_flipper_special_active = y1_active && layer_flipper_effective
        && !x1_active && !x2_active && !tilt1_effective && !tilt2_effective && !tilt3_effective;
    if (y1_layer_flipper_special_active) {
        return mode_active ? RuntimeTableId::MY1LayerFlipper : RuntimeTableId::Y1LayerFlipper;
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
        return mode_active ? RuntimeTableId::ModeDefault : RuntimeTableId::Default;
    }

    if (!mode_active) {
        switch (single_modifier) {
            case EffectiveModifier::X1:
                return RuntimeTableId::X1;
            case EffectiveModifier::X2:
                return RuntimeTableId::X2;
            case EffectiveModifier::Y1:
                return RuntimeTableId::Y1;
            case EffectiveModifier::LayerNormalX:
                return RuntimeTableId::LayerNormalX;
            case EffectiveModifier::LayerFlipper:
                return RuntimeTableId::LayerFlipper;
            case EffectiveModifier::Tilt1:
                return RuntimeTableId::Tilt1;
            case EffectiveModifier::Tilt2:
                return RuntimeTableId::Tilt2;
            case EffectiveModifier::Tilt3:
                return RuntimeTableId::Tilt3;
            default:
                return RuntimeTableId::Default;
        }
    }

    switch (single_modifier) {
        case EffectiveModifier::X1:
            return RuntimeTableId::MX1;
        case EffectiveModifier::X2:
            return RuntimeTableId::MX2;
        case EffectiveModifier::Y1:
            return RuntimeTableId::MY1;
        case EffectiveModifier::LayerNormalX:
            return RuntimeTableId::MLayerNormalX;
        case EffectiveModifier::LayerFlipper:
            return RuntimeTableId::MLayerFlipper;
        case EffectiveModifier::Tilt1:
            return RuntimeTableId::ModeDefault;
        case EffectiveModifier::Tilt2:
            return RuntimeTableId::MTilt2;
        case EffectiveModifier::Tilt3:
            return RuntimeTableId::MTilt3;
        default:
            return RuntimeTableId::ModeDefault;
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

void ApplyTableAnalogOutput(
    const RuntimeConfigView &runtime_config,
    RuntimeTableId active_table_id,
    int8_t x_axis,
    int8_t y_axis,
    OutputState &outputs
) {
    const size_t direction_index = DirectionIndexFromAxes(x_axis, y_axis);
    const StickPoint *active_table = LookupRuntimeTable(runtime_config, active_table_id);
    outputs.leftStickX = active_table[direction_index].x;
    outputs.leftStickY = active_table[direction_index].y;
}

void ApplyDirectionPlusAOverride(const RuntimeConfigView &runtime_config, const RoleState &roles, OutputState &outputs) {
    if (!roles.direction_plus_a_active) {
        return;
    }

    const RuntimeTableId direction_plus_a_table_id = roles.mode_active ? RuntimeTableId::ModeDefault : RuntimeTableId::Default;
    const size_t direction_plus_a_index = roles.direction_plus_a_force_up ? kDirectionEightIndex : kDirectionTwoIndex;
    const StickPoint direction_plus_a_point = LookupRuntimeStickPoint(runtime_config, direction_plus_a_table_id, direction_plus_a_index);
    outputs.leftStickX = direction_plus_a_point.x;
    outputs.leftStickY = direction_plus_a_point.y;
}

static_assert(
    ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig),
    "source-owned baseline runtime config must remain a valid fallback"
);

DiagnosticSourceViewCandidatePublicationState gDiagnosticSourceViewCandidatePublicationState =
    InitializeDiagnosticSourceViewCandidatePublicationState();

const ActiveRuntimeConfigState gActiveRuntimeConfigState = {
    gDiagnosticSourceViewCandidatePublicationState.validated &&
            gDiagnosticSourceViewCandidatePublicationState.equivalent_to_source_owned_baseline
        ? &gDiagnosticSourceViewCandidatePublicationState.candidate.view
        : &kSourceOwnedCurrentBaselineRuntimeConfig,
    gDiagnosticSourceViewCandidatePublicationState.validated &&
            gDiagnosticSourceViewCandidatePublicationState.equivalent_to_source_owned_baseline
        ? RuntimeConfigSource::SourceViewCandidate
        : RuntimeConfigSource::SourceOwnedBaseline,
    gDiagnosticSourceViewCandidatePublicationState.validated &&
            gDiagnosticSourceViewCandidatePublicationState.equivalent_to_source_owned_baseline
        ? RuntimeConfigActivationStatus::CandidateViewSelected
        : RuntimeConfigActivationStatus::FallbackSelected,
};

const DiagnosticSourceViewCandidatePublicationState& GetDiagnosticSourceViewCandidatePublicationState() {
    return gDiagnosticSourceViewCandidatePublicationState;
}

const ActiveRuntimeConfigState& GetActiveRuntimeConfigState() {
    return gActiveRuntimeConfigState;
}

const RuntimeConfigView& ResolveActiveRuntimeConfig() {
    return *GetActiveRuntimeConfigState().active_view;
}

void ApplyZAirdodgeOverride(const RuntimeConfigView &runtime_config, const EffectiveDirectionState &directions, OutputState &outputs) {
    const int8_t lt1_x = directions.left == directions.right ? 0 : (directions.left ? -1 : 1);
    const int8_t lt1_y = directions.down == directions.up ? 0 : (directions.down ? -1 : 1);
    const size_t lt1_direction_index = DirectionIndexFromAxes(lt1_x, lt1_y);
    const StickPoint lt1_point = LookupRuntimeStickPoint(runtime_config, RuntimeTableId::Lt1LowMagnitude, lt1_direction_index);
    outputs.leftStickX = lt1_point.x;
    outputs.leftStickY = lt1_point.y;
}

void ApplyHardUpBOverride(const EffectiveDirectionState &directions, OutputState &outputs) {
    // RF7 is a hard Up+B analog override with horizontal from effective direction.
    const uint8_t rf7_horizontal = directions.left == directions.right ? 128 : (directions.left ? 77 : 179);
    outputs.leftStickX = rf7_horizontal;
    outputs.leftStickY = 172;
}

void ApplyRF3VerticalCStickDiagonalOverride(
    const InputState &inputs,
    const EffectiveDirectionState &directions,
    const StickDirections &stick_directions,
    OutputState &outputs
) {
    if (!inputs.rf3 || inputs.rt3 || inputs.rt4 || stick_directions.cy == 0) {
        return;
    }

    if (directions.left == directions.right) {
        return;
    }

    outputs.rightStickX = directions.left ? 95 : 161;
    outputs.rightStickY = stick_directions.cy > 0 ? 165 : 91;
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

    ApplyDigitalButtonOutputs(inputs, layer, roles, outputs);
    ApplyDpadOutputs(inputs, effective_directions, roles, outputs);
    ApplyDigitalDirectionOutputs(effective_directions, roles, outputs);
    ApplyRightStickDigitalOutputs(inputs, outputs);
}

void Ultimate::UpdateAnalogOutputs(const InputState &inputs, OutputState &outputs, CommunicationBackendId backend_id) {
    (void)backend_id;
    const LayerState layer = ResolveLayerState(inputs);
    const EffectiveDirectionState effective_directions = ResolveEffectiveDirections(inputs, layer);
    const RoleState roles = ResolveRoleState(inputs, layer, effective_directions);
    const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();

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
    const bool rf4_rf2_minus41_active = roles.rf4_behavior_available && inputs.rf2 && !inputs.lt2 && !inputs.lf4 && !roles.rt1_rf4_custom_active;
    RuntimeTableId active_table_id = SelectRuntimeTableId(
        roles.mode_active,
        roles.x1_active,
        roles.x2_active,
        roles.y1_active,
        roles.layer_rf3_normal_x_active,
        roles.rf4_layer_flipper_active,
        roles.rt1_rf4_custom_active || (roles.tilt1_effective && !rf4_rf2_minus41_active),
        roles.rt1_rf4_custom_active || roles.tilt2_effective,
        roles.tilt3_effective
    );
    if (rf4_rf2_minus41_active) {
        active_table_id = RuntimeTableId::Tilt1Minus41;
    }

    if (roles.ls_to_dpad_active) {
        const RuntimeTableId center_table_id = roles.mode_active ? RuntimeTableId::ModeDefault : RuntimeTableId::Default;
        const StickPoint center = LookupRuntimeStickPoint(runtime_config, center_table_id, kDirectionFiveIndex);
        outputs.leftStickX = center.x;
        outputs.leftStickY = center.y;
    } else {
        ApplyTableAnalogOutput(runtime_config, active_table_id, directions.x, directions.y, outputs);
        ApplyDirectionPlusAOverride(runtime_config, roles, outputs);

        if (roles.z_airdodge_override_active) {
            ApplyZAirdodgeOverride(runtime_config, effective_directions, outputs);
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

    ApplyRF3VerticalCStickDiagonalOverride(inputs, effective_directions, directions, outputs);

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
