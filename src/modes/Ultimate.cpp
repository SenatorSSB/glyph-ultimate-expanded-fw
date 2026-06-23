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
};

enum class RuntimeConfigActivationStatus {
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
#include "modes/UltimateRuntimeConfigParser.hpp"

static_assert(
    UltimateRuntimeConfigParser::kPayloadSize == 530,
    "Phase 7A parser scaffold must stay aligned with the offline GCFG-like payload size"
);

enum class RuntimeConfigCandidateStatus {
    Empty,
    ParsedPayloadValid,
    ParsedPayloadEquivalent,
    InvalidPayload,
};

struct RuntimeConfigCandidateState {
    RuntimeConfigCandidateStatus status;
    StickPoint points[kRuntimeTableCount][kRuntimeTablePointCount];
    RuntimeTableView tables[kRuntimeTableCount];
    RuntimeConfigView view;
};

struct DiagnosticParsedCandidateState {
    UltimateRuntimeConfigParser::ParseResult parse_result;
    RuntimeConfigCandidateState candidate;
    bool materialized;
    bool equivalent_to_source_owned_baseline;
};

constexpr uint8_t kDiagnosticSourceOwnedParsedPayload[UltimateRuntimeConfigParser::kPayloadSize] = {
    0x47, 0x43, 0x46, 0x47, 0x01, 0xd6, 0x6f, 0x1d, 0x98, 0x1b, 0x09, 0x00,
    0x1b, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a,
    0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
    0x17, 0x18, 0x19, 0x1a, 0x3d, 0x33, 0x80, 0x33, 0xc3, 0x33, 0x3d, 0x80,
    0x80, 0x80, 0xc3, 0x80, 0x3d, 0xcd, 0x80, 0xcd, 0xc3, 0xcd, 0x0e, 0x57,
    0x80, 0x57, 0xf2, 0x57, 0x0e, 0xa9, 0x80, 0xa9, 0xf2, 0xa9, 0x0e, 0xa9,
    0x80, 0xa9, 0xf2, 0xa9, 0x5d, 0x33, 0x80, 0x33, 0xa3, 0x33, 0x5d, 0x80,
    0x80, 0x80, 0xa3, 0x80, 0x5d, 0xcd, 0x80, 0xcd, 0xa3, 0xcd, 0x52, 0x33,
    0x80, 0x33, 0xae, 0x33, 0x52, 0x80, 0x80, 0x80, 0xae, 0x80, 0x52, 0xcd,
    0x80, 0xcd, 0xae, 0xcd, 0x4e, 0x57, 0x80, 0x57, 0xb2, 0x57, 0x4e, 0xa9,
    0x80, 0xa9, 0xb2, 0xa9, 0x4e, 0xa9, 0x80, 0xa9, 0xb2, 0xa9, 0x41, 0x57,
    0x80, 0x57, 0xbf, 0x57, 0x41, 0xa9, 0x80, 0xa9, 0xbf, 0xa9, 0x41, 0xa9,
    0x80, 0xa9, 0xbf, 0xa9, 0x3d, 0x63, 0x80, 0x63, 0xc3, 0x63, 0x3d, 0x80,
    0x80, 0x80, 0xc3, 0x80, 0x3d, 0x9d, 0x80, 0x9d, 0xc3, 0x9d, 0x0e, 0xb3,
    0x80, 0xb3, 0xf2, 0xb3, 0x0e, 0xa9, 0x80, 0xa9, 0xf2, 0xa9, 0x0e, 0x4d,
    0x80, 0x4d, 0xf2, 0x4d, 0x57, 0x33, 0x80, 0x33, 0xa9, 0x33, 0x57, 0x80,
    0x80, 0x80, 0xa9, 0x80, 0x57, 0xcd, 0x80, 0xcd, 0xa9, 0xcd, 0x57, 0x57,
    0x80, 0x57, 0xa9, 0x57, 0x57, 0xa9, 0x80, 0xa9, 0xa9, 0xa9, 0x57, 0xa9,
    0x80, 0xa9, 0xa9, 0xa9, 0xa9, 0x33, 0x80, 0x33, 0x57, 0x33, 0xa9, 0x80,
    0x80, 0x80, 0x57, 0x80, 0xa9, 0xcd, 0x80, 0xcd, 0x57, 0xcd, 0xa9, 0x57,
    0x80, 0x57, 0x57, 0x57, 0xa9, 0xa9, 0x80, 0xa9, 0x57, 0xa9, 0xa9, 0xa9,
    0x80, 0xa9, 0x57, 0xa9, 0xa9, 0x63, 0x80, 0x63, 0x57, 0x63, 0xa9, 0x80,
    0x80, 0x80, 0x57, 0x80, 0xa9, 0x9d, 0x80, 0x9d, 0x57, 0x9d, 0xa9, 0xb3,
    0x80, 0xb3, 0x57, 0xb3, 0xa9, 0xa9, 0x80, 0xa9, 0x57, 0xa9, 0xa9, 0x4d,
    0x80, 0x4d, 0x57, 0x4d, 0xa9, 0x63, 0x80, 0x63, 0x57, 0x63, 0xa9, 0x80,
    0x80, 0x80, 0x57, 0x80, 0xa9, 0x9d, 0x80, 0x9d, 0x57, 0x9d, 0xa9, 0xb3,
    0x80, 0xb3, 0x57, 0xb3, 0xa9, 0xa9, 0x80, 0xa9, 0x57, 0xa9, 0xa9, 0x4d,
    0x80, 0x4d, 0x57, 0x4d, 0x57, 0x63, 0x80, 0x63, 0xa9, 0x63, 0x57, 0x80,
    0x80, 0x80, 0xa9, 0x80, 0x57, 0x9d, 0x80, 0x9d, 0xa9, 0x9d, 0x57, 0xb3,
    0x80, 0xb3, 0xa9, 0xb3, 0x57, 0xa9, 0x80, 0xa9, 0xa9, 0xa9, 0x57, 0x4d,
    0x80, 0x4d, 0xa9, 0x4d, 0xbb, 0x2f, 0x80, 0x2f, 0x45, 0x2f, 0xbb, 0x80,
    0x80, 0x80, 0x45, 0x80, 0xbb, 0xd1, 0x80, 0xd1, 0x45, 0xd1, 0x58, 0x4f,
    0x80, 0x4f, 0xa8, 0x4f, 0x58, 0x80, 0x80, 0x80, 0xa8, 0x80, 0x58, 0xb1,
    0x80, 0xb1, 0xa8, 0xb1, 0x4b, 0x56, 0x80, 0x56, 0xb5, 0x56, 0x4b, 0x80,
    0x80, 0x80, 0xb5, 0x80, 0x4b, 0xaa, 0x80, 0xaa, 0xb5, 0xaa, 0xa9, 0x2f,
    0x80, 0x2f, 0x57, 0x2f, 0xa9, 0x80, 0x80, 0x80, 0x57, 0x80, 0xa9, 0xd1,
    0x80, 0xd1, 0x57, 0xd1, 0x45, 0x4e, 0x80, 0x4e, 0xbb, 0x4e, 0x45, 0x80,
    0x80, 0x80, 0xbb, 0x80, 0x48, 0xac, 0x80, 0xb3, 0xb8, 0xac, 0xa9, 0x58,
    0x80, 0x58, 0x57, 0x58, 0xa9, 0xa9, 0x80, 0xa9, 0x57, 0xa9, 0xa9, 0xa8,
    0x80, 0xa8, 0x57, 0xa8, 0x60, 0x52, 0x80, 0x52, 0xa0, 0x52, 0x60, 0xa9,
    0x80, 0xa9, 0xa0, 0xa9, 0x60, 0xae, 0x80, 0xae, 0xa0, 0xae, 0x60, 0x56,
    0x80, 0x56, 0xa0, 0x56, 0x60, 0xa9, 0x80, 0xa9, 0xa0, 0xa9, 0x60, 0xaa,
    0x80, 0xaa, 0xa0, 0xaa, 0x59, 0x59, 0x80, 0x4f, 0xa7, 0x59, 0x4f, 0x80,
    0x80, 0x80, 0xb1, 0x80, 0x59, 0xa7, 0x80, 0xb1, 0xa7, 0xa7, 0x97, 0xcd,
    0x6c, 0x3c
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
        candidate.status != RuntimeConfigCandidateStatus::ParsedPayloadValid &&
        candidate.status != RuntimeConfigCandidateStatus::ParsedPayloadEquivalent
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
        candidate.status = RuntimeConfigCandidateStatus::InvalidPayload;
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
        ? RuntimeConfigCandidateStatus::ParsedPayloadValid
        : RuntimeConfigCandidateStatus::InvalidPayload;
    return candidate.status == RuntimeConfigCandidateStatus::ParsedPayloadValid;
}

DiagnosticParsedCandidateState InitializeDiagnosticParsedCandidateState() {
    DiagnosticParsedCandidateState state = {
        UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload(
            kDiagnosticSourceOwnedParsedPayload,
            UltimateRuntimeConfigParser::kPayloadSize
        ),
        {},
        false,
        false,
    };

    ResetRuntimeConfigCandidateState(state.candidate);
    if (state.parse_result.status != UltimateRuntimeConfigParser::ParseStatus::Ok) {
        state.candidate.status = RuntimeConfigCandidateStatus::InvalidPayload;
        return state;
    }

    state.materialized = MaterializeRuntimeConfigCandidateFromSourceView(
        kSourceOwnedCurrentBaselineRuntimeConfig,
        state.candidate
    );
    state.equivalent_to_source_owned_baseline = state.materialized &&
        RuntimeConfigViewsHaveEquivalentPoints(
            state.candidate.view,
            kSourceOwnedCurrentBaselineRuntimeConfig
        );
    if (state.equivalent_to_source_owned_baseline) {
        state.candidate.status = RuntimeConfigCandidateStatus::ParsedPayloadEquivalent;
    }
    return state;
}

const DiagnosticParsedCandidateState kDiagnosticParsedCandidateState =
    InitializeDiagnosticParsedCandidateState();

constexpr size_t kDirectionTwoIndex = 1;
constexpr size_t kDirectionFiveIndex = 4;
constexpr size_t kDirectionEightIndex = 7;
constexpr uint8_t kFriendProfile3X1Magnitude = 30;
constexpr uint8_t kFriendProfile3Y1Magnitude = 28;

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
    state.lf4_submode_active = false;
    state.layer_transform_active = false;
    state.c_stick_any_active = inputs.rt2 || inputs.rt3 || inputs.rt4 || inputs.rt5;
    state.rf2_suppressed_by_lf4_submode_cstick = false;
    return state;
}

EffectiveDirectionState ResolveEffectiveDirections(const InputState &inputs, const LayerState &layer) {
    EffectiveDirectionState state;
    state.force_up_active = inputs.lf5 || inputs.lt5 || inputs.rf6;
    state.horizontal_axis = ResolveHorizontalAxis(
        inputs.lf3 || inputs.rf8,
        inputs.lf1,
        layer.layer_left_active,
        layer.layer_right_active
    );
    state.up = state.force_up_active;
    state.down = inputs.lf2 && !state.force_up_active;
    state.left = state.horizontal_axis < 0;
    state.right = state.horizontal_axis > 0;
    return state;
}

RoleState ResolveRoleState(const InputState &inputs, const LayerState &layer, const EffectiveDirectionState &directions) {
    (void)layer;
    (void)directions;

    RoleState state;
    state.mode_active = inputs.rf5 || inputs.rf9;
    state.x1_active = inputs.lt4;
    state.x2_active = inputs.rf15 || inputs.rf12;
    state.y1_active = inputs.lt3;
    state.layer_rf3_normal_x_active = false;
    state.rf4_layer_flipper_active = false;
    state.rt1_rf4_custom_active = false;
    state.rf4_modifier_suppressed_by_cstick = false;
    state.rf4_behavior_available = inputs.rf4;
    state.base_rf3_x_active = false;
    state.rf9_base_rf3_x_mode_active = false;
    state.rf4_suppressed_by_rf9_rf3_mode = false;
    state.rf3_x_suppressed_by_rf9 = false;
    state.rf3_x_restored_by_cstick = false;
    state.tilt3_effective = false;
    state.tilt1_effective = inputs.rf4;
    state.tilt2_effective = inputs.rf3;
    state.z_airdodge_override_active = false;
    state.null_modifier_active = false;
    state.hard_up_b_active = false;
    state.ls_to_dpad_active = false;
    state.direction_plus_a_active = false;
    state.direction_plus_a_force_up = false;
    return state;
}

void ApplyDigitalButtonOutputs(const InputState &inputs, const LayerState &layer, const RoleState &roles, OutputState &outputs) {
    (void)layer;
    (void)roles;

    outputs.a = inputs.rt1 || inputs.lt2 || inputs.rf10;
    outputs.b = inputs.rf1 || inputs.lt2;
    outputs.x = inputs.rf7;
    outputs.y = inputs.rf2;
    outputs.buttonL = inputs.lf4 || inputs.rf10;
    // GameCube/N64 backends serialize buttonR as Z; triggerRDigital as R.
    outputs.buttonR = inputs.lt1;
    outputs.triggerLDigital = inputs.lf4 || inputs.rf10;
    outputs.triggerRDigital = inputs.rf10;

    outputs.start = inputs.rf16;
    outputs.select = inputs.mb6;
    outputs.home = inputs.mb5;
    outputs.capture = inputs.mb4;
}

void ApplyDpadOutputs(const InputState &inputs, const EffectiveDirectionState &directions, const RoleState &roles, OutputState &outputs) {
    outputs.dpadUp = 0;
    outputs.dpadDown = 0;
    outputs.dpadLeft = 0;
    outputs.dpadRight = 0;

    outputs.dpadUp = inputs.rf13;
    outputs.dpadDown = inputs.rf11;
    outputs.dpadLeft = inputs.lf7;
    outputs.dpadRight = inputs.lf6;

    // Preserve source-backed nunchuk C D-pad layer behavior.
    if (inputs.nunchuk_c) {
        outputs.dpadUp |= inputs.rt4;
        outputs.dpadDown |= inputs.rt2;
        outputs.dpadLeft |= inputs.rt3;
        outputs.dpadRight |= inputs.rt5;
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
    outputs.rightStickRight = inputs.rt5;
    outputs.rightStickDown = inputs.rt2;
    outputs.rightStickUp = inputs.rt4;

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
    const bool layer_flipper_effective = false;
    const bool layer_normal_x_effective = false;
    (void)layer_normal_x_active;
    (void)layer_flipper_active;

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
            return RuntimeTableId::MTilt1;
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

uint8_t ApplyFriendProfile3AxisMagnitude(int8_t axis, uint8_t magnitude) {
    int signed_axis = static_cast<int>(axis);
    if (signed_axis < -1) {
        signed_axis = -1;
    } else if (signed_axis > 1) {
        signed_axis = 1;
    }

    const int raw_value = ANALOG_STICK_NEUTRAL + (signed_axis * static_cast<int>(magnitude));
    if (raw_value < 0) {
        return 0;
    }
    if (raw_value > 255) {
        return 255;
    }
    return static_cast<uint8_t>(raw_value);
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

void ApplyFriendProfile3XYModifierOverrides(const RoleState &roles, int8_t x_axis, int8_t y_axis, OutputState &outputs) {
    // Source note for the friend baked profile: LT4 is X1 and LT3 is Y1 in
    // ResolveRoleState(); RF4 is Tilt and RF3 is Tilt2. The only flipper role
    // here is rf4_layer_flipper_active, which is initialized false in this
    // friend branch because no source-grounded flipper binding was provided.
    const bool friend_profile3_xy_modifiers_available =
        !roles.mode_active &&
        !roles.x2_active &&
        !roles.layer_rf3_normal_x_active &&
        !roles.rf4_layer_flipper_active &&
        !roles.rt1_rf4_custom_active &&
        !roles.tilt1_effective &&
        !roles.tilt2_effective &&
        !roles.tilt3_effective;

    if (!friend_profile3_xy_modifiers_available) {
        return;
    }

    if (roles.x1_active) {
        outputs.leftStickX = ApplyFriendProfile3AxisMagnitude(x_axis, kFriendProfile3X1Magnitude);
    }
    if (roles.y1_active) {
        outputs.leftStickY = ApplyFriendProfile3AxisMagnitude(y_axis, kFriendProfile3Y1Magnitude);
    }
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

void ApplyFriendProfileCStickRawOutputs(bool mode_active, const StickDirections &stick_directions, OutputState &outputs) {
    if (stick_directions.cx < 0) {
        outputs.rightStickX = mode_active ? 1 : 39;
    } else if (stick_directions.cx > 0) {
        outputs.rightStickX = mode_active ? 255 : 217;
    } else {
        outputs.rightStickX = 128;
    }

    if (stick_directions.cy < 0) {
        outputs.rightStickY = 1;
    } else if (stick_directions.cy > 0) {
        outputs.rightStickY = 255;
    } else {
        outputs.rightStickY = 128;
    }
}

const ActiveRuntimeConfigState& GetActiveRuntimeConfigState() {
    static_assert(
        ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig),
        "diagnostic branch publishes only the source-owned baseline runtime config"
    );
    static const ActiveRuntimeConfigState state = {
        &kSourceOwnedCurrentBaselineRuntimeConfig,
        RuntimeConfigSource::SourceOwnedBaseline,
        RuntimeConfigActivationStatus::SourceOwnedSelected,
    };
    return state;
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
    (void)inputs;
    (void)directions;
    (void)stick_directions;
    (void)outputs;
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
        effective_directions.down, // Down (LF2, suppressed by forced-Up)
        effective_directions.up, // Up (LF5/LT5/RF6)
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
    // Friend profile3 WIP priority: source-owned left-stick table output,
    // exact C-stick raw output, then the pre-existing nunchuk override below.
    const bool rf4_rf2_minus41_active = false;
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
        ApplyFriendProfile3XYModifierOverrides(roles, directions.x, directions.y, outputs);

        if (roles.z_airdodge_override_active) {
            ApplyZAirdodgeOverride(runtime_config, effective_directions, outputs);
        }

        if (roles.hard_up_b_active) {
            ApplyHardUpBOverride(effective_directions, outputs);
        }
    }

    ApplyFriendProfileCStickRawOutputs(roles.mode_active, directions, outputs);
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
