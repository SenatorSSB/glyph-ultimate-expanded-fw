#!/usr/bin/env python3
"""Evaluate current Glyph identity runtime behavior cases against a source mirror.

This is a bounded regression harness for the representative behavior-case
fixture. It is not a firmware simulator and is not hardware validation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from extract_glyph_identity_runtime_tables import load_source_text_with_generated_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "calibration" / "fixtures" / "glyph_identity_runtime_behavior_cases_2026-05-28.json"
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"
STRUCTURAL_CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_behavior_cases.py"
TABLE_SOURCE_SYNC_CHECKER_PATH = REPO_ROOT / "tools" / "check_glyph_identity_runtime_table_source_sync.py"

ANALOG_STICK_MIN = 28
ANALOG_STICK_NEUTRAL = 128
ANALOG_STICK_MAX = 228

K_DIRECTION_TWO_INDEX = 1
K_DIRECTION_FIVE_INDEX = 4
K_DIRECTION_EIGHT_INDEX = 7

SOURCE_ANCHORS = (
    "ResolveLayerState",
    "ResolveEffectiveDirections",
    "ResolveRoleState",
    "ApplyDigitalButtonOutputs",
    "ApplyDpadOutputs",
    "ApplyDigitalDirectionOutputs",
    "ApplyRightStickDigitalOutputs",
    "SelectStickTable",
    "ApplyTableAnalogOutput",
    "ApplyDirectionPlusAOverride",
    "ApplyZAirdodgeOverride",
    "ApplyHardUpBOverride",
    "ApplyNullOverride",
    "state.z_airdodge_override_active = inputs.lt5 || inputs.rf11;",
    "state.hard_up_b_active = inputs.rf7;",
    "state.null_modifier_active = inputs.rf9;",
    "state.ls_to_dpad_active = inputs.rf13;",
)

IGNORED_EXPECTED_FIELDS = {
    "analog_source",
    "direction_index",
    "table_id",
}

SUPPORTED_EXPECTED_FIELDS = {
    "digital_buttons",
    "dpad",
    "effective_direction",
    "hardware_status",
    "left_stick",
    "left_stick_digital",
    "right_stick",
    "right_stick_digital",
    "suppressed_buttons",
    "suppressed_directions",
    "suppressed_modifiers",
    "trigger_analog",
} | IGNORED_EXPECTED_FIELDS

TABLES: dict[str, tuple[tuple[int, int], ...]] = {
    "Default": (
        (61, 51), (128, 51), (195, 51),
        (61, 128), (128, 128), (195, 128),
        (61, 205), (128, 205), (195, 205),
    ),
    "ModeDefault": (
        (14, 87), (128, 87), (242, 87),
        (14, 169), (128, 169), (242, 169),
        (14, 169), (128, 169), (242, 169),
    ),
    "X1": (
        (93, 51), (128, 51), (163, 51),
        (93, 128), (128, 128), (163, 128),
        (93, 205), (128, 205), (163, 205),
    ),
    "X2": (
        (82, 51), (128, 51), (174, 51),
        (82, 128), (128, 128), (174, 128),
        (82, 205), (128, 205), (174, 205),
    ),
    "MX1": (
        (78, 87), (128, 87), (178, 87),
        (78, 169), (128, 169), (178, 169),
        (78, 169), (128, 169), (178, 169),
    ),
    "MX2": (
        (65, 87), (128, 87), (191, 87),
        (65, 169), (128, 169), (191, 169),
        (65, 169), (128, 169), (191, 169),
    ),
    "Y1": (
        (61, 99), (128, 99), (195, 99),
        (61, 128), (128, 128), (195, 128),
        (61, 157), (128, 157), (195, 157),
    ),
    "MY1": (
        (14, 179), (128, 179), (242, 179),
        (14, 169), (128, 169), (242, 169),
        (14, 77), (128, 77), (242, 77),
    ),
    "LayerNormalX": (
        (87, 51), (128, 51), (169, 51),
        (87, 128), (128, 128), (169, 128),
        (87, 205), (128, 205), (169, 205),
    ),
    "MLayerNormalX": (
        (87, 87), (128, 87), (169, 87),
        (87, 169), (128, 169), (169, 169),
        (87, 169), (128, 169), (169, 169),
    ),
    "LayerFlipper": (
        (169, 51), (128, 51), (87, 51),
        (169, 128), (128, 128), (87, 128),
        (169, 205), (128, 205), (87, 205),
    ),
    "MLayerFlipper": (
        (169, 87), (128, 87), (87, 87),
        (169, 169), (128, 169), (87, 169),
        (169, 169), (128, 169), (87, 169),
    ),
    "Y1Tilt1": (
        (169, 99), (128, 99), (87, 99),
        (169, 128), (128, 128), (87, 128),
        (169, 157), (128, 157), (87, 157),
    ),
    "MY1Tilt1": (
        (169, 179), (128, 179), (87, 179),
        (169, 169), (128, 169), (87, 169),
        (169, 77), (128, 77), (87, 77),
    ),
    "Y1LayerFlipper": (
        (169, 99), (128, 99), (87, 99),
        (169, 128), (128, 128), (87, 128),
        (169, 157), (128, 157), (87, 157),
    ),
    "MY1LayerFlipper": (
        (169, 179), (128, 179), (87, 179),
        (169, 169), (128, 169), (87, 169),
        (169, 77), (128, 77), (87, 77),
    ),
    "Y1LayerNormalX": (
        (87, 99), (128, 99), (169, 99),
        (87, 128), (128, 128), (169, 128),
        (87, 157), (128, 157), (169, 157),
    ),
    "MY1LayerNormalX": (
        (87, 179), (128, 179), (169, 179),
        (87, 169), (128, 169), (169, 169),
        (87, 77), (128, 77), (169, 77),
    ),
    "Tilt1": (
        (187, 47), (128, 47), (69, 47),
        (187, 128), (128, 128), (69, 128),
        (187, 209), (128, 209), (69, 209),
    ),
    "Tilt2": (
        (88, 79), (128, 79), (168, 79),
        (88, 128), (128, 128), (168, 128),
        (88, 177), (128, 177), (168, 177),
    ),
    "Tilt3": (
        (75, 86), (128, 86), (181, 86),
        (75, 128), (128, 128), (181, 128),
        (75, 170), (128, 170), (181, 170),
    ),
    "MTilt1": (
        (169, 88), (128, 88), (87, 88),
        (169, 169), (128, 169), (87, 169),
        (169, 168), (128, 168), (87, 168),
    ),
    "MTilt2": (
        (96, 82), (128, 82), (160, 82),
        (96, 169), (128, 169), (160, 169),
        (96, 174), (128, 174), (160, 174),
    ),
    "MTilt3": (
        (96, 86), (128, 86), (160, 86),
        (96, 169), (128, 169), (160, 169),
        (96, 170), (128, 170), (160, 170),
    ),
    "Lt1LowMagnitude": (
        (89, 89), (128, 79), (167, 89),
        (79, 128), (128, 128), (177, 128),
        (89, 167), (128, 177), (167, 167),
    ),
}


@dataclass
class InputState:
    lf1: bool = False
    lf2: bool = False
    lf3: bool = False
    lf4: bool = False
    lf5: bool = False
    lf6: bool = False
    lf7: bool = False
    lf8: bool = False
    lt1: bool = False
    lt2: bool = False
    lt3: bool = False
    lt4: bool = False
    lt5: bool = False
    lt6: bool = False
    rt1: bool = False
    rt2: bool = False
    rt3: bool = False
    rt4: bool = False
    rt5: bool = False
    rf1: bool = False
    rf2: bool = False
    rf3: bool = False
    rf4: bool = False
    rf5: bool = False
    rf6: bool = False
    rf7: bool = False
    rf8: bool = False
    rf9: bool = False
    rf10: bool = False
    rf11: bool = False
    rf12: bool = False
    rf13: bool = False
    rf14: bool = False
    rf15: bool = False
    rf16: bool = False
    mb1: bool = False
    mb2: bool = False
    mb3: bool = False
    mb4: bool = False
    mb5: bool = False
    mb6: bool = False
    mb7: bool = False
    nunchuk_c: bool = False
    nunchuk_connected: bool = False
    nunchuk_x: int = 0
    nunchuk_y: int = 0


@dataclass(frozen=True)
class LayerState:
    layer_left_active: bool
    layer_right_active: bool
    layer_direction_active: bool
    lf4_submode_active: bool
    layer_transform_active: bool
    c_stick_any_active: bool
    rf2_suppressed_by_lf4_submode_cstick: bool


@dataclass(frozen=True)
class EffectiveDirectionState:
    left: bool
    right: bool
    up: bool
    down: bool
    force_up_active: bool
    horizontal_axis: int


@dataclass(frozen=True)
class RoleState:
    mode_active: bool
    x1_active: bool
    x2_active: bool
    y1_active: bool
    layer_rf3_normal_x_active: bool
    rf4_layer_flipper_active: bool
    tilt1_effective: bool
    tilt2_effective: bool
    tilt3_effective: bool
    z_airdodge_override_active: bool
    null_modifier_active: bool
    hard_up_b_active: bool
    ls_to_dpad_active: bool
    direction_plus_a_active: bool
    direction_plus_a_force_up: bool


@dataclass
class OutputState:
    a: bool = False
    b: bool = False
    x: bool = False
    y: bool = False
    buttonL: bool = False
    buttonR: bool = False
    triggerLDigital: bool = False
    triggerRDigital: bool = False
    start: bool = False
    select: bool = False
    home: bool = False
    capture: bool = False
    dpadUp: bool = False
    dpadDown: bool = False
    dpadLeft: bool = False
    dpadRight: bool = False
    leftStickLeft: bool = False
    leftStickRight: bool = False
    leftStickUp: bool = False
    leftStickDown: bool = False
    rightStickLeft: bool = False
    rightStickRight: bool = False
    rightStickUp: bool = False
    rightStickDown: bool = False
    leftStickX: int = 128
    leftStickY: int = 128
    rightStickX: int = 128
    rightStickY: int = 128
    triggerLAnalog: int = 0
    triggerRAnalog: int = 0


@dataclass
class StickDirections:
    horizontal: bool = False
    vertical: bool = False
    diagonal: bool = False
    x: int = 0
    y: int = 0
    cx: int = 0
    cy: int = 0


@dataclass(frozen=True)
class Evaluation:
    input_state: InputState
    effective_directions: EffectiveDirectionState
    roles: RoleState
    outputs: OutputState
    table_name: str


@dataclass(frozen=True)
class Mismatch:
    case_id: str
    field: str
    expected: Any
    actual: Any


class EvaluationError(Exception):
    pass


DIGITAL_BUTTON_FIELDS: dict[str, tuple[str, ...]] = {
    "A": ("a",),
    "B": ("b",),
    "X": ("x",),
    "Y": ("y",),
    "L": ("buttonL", "triggerLDigital"),
    "R": ("triggerRDigital",),
    "Z": ("buttonR",),
    "Capture": ("capture",),
    "Home": ("home",),
    "Select/Minus": ("select",),
    "Start/Plus": ("start",),
}

DIRECTION_FIELDS = {
    "Left": "left",
    "Right": "right",
    "Up": "up",
    "Down": "down",
}

ROLE_MODIFIER_FIELDS = {
    "Mode": "mode_active",
    "X1": "x1_active",
    "X2": "x2_active",
    "Y1": "y1_active",
    "LayerNormalX": "layer_rf3_normal_x_active",
    "LayerFlipper": "rf4_layer_flipper_active",
    "Tilt1": "tilt1_effective",
    "Tilt2": "tilt2_effective",
    "Tilt3": "tilt3_effective",
}


def run_structural_checker() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(STRUCTURAL_CHECKER_PATH.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def run_table_source_sync_checker() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TABLE_SOURCE_SYNC_CHECKER_PATH.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def load_fixture() -> dict[str, Any]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_source_anchors() -> list[str]:
    source_text = load_source_text_with_generated_tables(SOURCE_PATH)
    return [anchor for anchor in SOURCE_ANCHORS if anchor not in source_text]


def input_state_from_case(case: dict[str, Any]) -> InputState:
    inputs = InputState()

    for button in case.get("input_buttons", []):
        field = button.lower()
        if not hasattr(inputs, field):
            raise EvaluationError(f"unsupported input button {button!r}")
        setattr(inputs, field, True)

    for field, value in case.get("input_state", {}).items():
        if field not in {"nunchuk_c", "nunchuk_connected", "nunchuk_x", "nunchuk_y"}:
            raise EvaluationError(f"unsupported input_state field {field!r}")
        setattr(inputs, field, value)

    return inputs


def resolve_horizontal_axis(
    base_left_active: bool,
    base_right_active: bool,
    layer_left_active: bool,
    layer_right_active: bool,
) -> int:
    horizontal_score = int(base_right_active) - int(base_left_active)
    horizontal_score += int(layer_right_active) - int(layer_left_active)
    if horizontal_score < 0:
        return -1
    if horizontal_score > 0:
        return 1
    return 0


def resolve_layer_state(inputs: InputState) -> LayerState:
    layer_left_active = inputs.lf8
    layer_right_active = inputs.lf7
    layer_direction_active = layer_left_active or layer_right_active
    lf4_submode_active = inputs.lf4 and (layer_direction_active or inputs.lt2)
    layer_transform_active = layer_direction_active or lf4_submode_active
    c_stick_any_active = inputs.rt2 or inputs.rt3 or inputs.rt4 or inputs.rt5
    rf2_suppressed = lf4_submode_active and c_stick_any_active
    return LayerState(
        layer_left_active=layer_left_active,
        layer_right_active=layer_right_active,
        layer_direction_active=layer_direction_active,
        lf4_submode_active=lf4_submode_active,
        layer_transform_active=layer_transform_active,
        c_stick_any_active=c_stick_any_active,
        rf2_suppressed_by_lf4_submode_cstick=rf2_suppressed,
    )


def resolve_effective_directions(inputs: InputState, layer: LayerState) -> EffectiveDirectionState:
    pure_layer_rf2_force_up_active = (
        layer.layer_direction_active
        and not inputs.lf4
        and inputs.rf2
        and not layer.rf2_suppressed_by_lf4_submode_cstick
    )
    lf4_submode_rf3_force_up_active = layer.lf4_submode_active and inputs.rf3
    force_up_active = (
        inputs.rf6
        or inputs.rf12
        or inputs.rf15
        or pure_layer_rf2_force_up_active
        or lf4_submode_rf3_force_up_active
    )
    horizontal_axis = resolve_horizontal_axis(
        inputs.lf3,
        inputs.lf1,
        layer.layer_left_active,
        layer.layer_right_active,
    )
    return EffectiveDirectionState(
        left=horizontal_axis < 0,
        right=horizontal_axis > 0,
        up=inputs.lf2 or force_up_active,
        down=(inputs.lf5 or inputs.lt6) and not force_up_active,
        force_up_active=force_up_active,
        horizontal_axis=horizontal_axis,
    )


def resolve_role_state(inputs: InputState, layer: LayerState, directions: EffectiveDirectionState) -> RoleState:
    down_a_active = inputs.lt6
    up_a_active = inputs.rf12 or inputs.rf15
    tilt1_pressed = inputs.rf3 and not layer.layer_transform_active
    tilt2_pressed = inputs.rf4 and not layer.layer_transform_active
    direction_plus_a_active = down_a_active or up_a_active

    return RoleState(
        mode_active=inputs.rf8,
        x1_active=inputs.lt4,
        x2_active=inputs.lt1,
        y1_active=inputs.lt2 and not inputs.lf4,
        layer_rf3_normal_x_active=layer.layer_direction_active and not inputs.lf4 and inputs.rf3,
        rf4_layer_flipper_active=layer.layer_transform_active and inputs.rf4,
        tilt3_effective=tilt1_pressed and tilt2_pressed,
        tilt1_effective=tilt1_pressed and not tilt2_pressed,
        tilt2_effective=tilt2_pressed and not tilt1_pressed,
        z_airdodge_override_active=inputs.lt5 or inputs.rf11,
        null_modifier_active=inputs.rf9,
        hard_up_b_active=inputs.rf7,
        ls_to_dpad_active=inputs.rf13,
        direction_plus_a_active=direction_plus_a_active,
        direction_plus_a_force_up=direction_plus_a_active and (up_a_active or directions.force_up_active),
    )


def apply_digital_button_outputs(inputs: InputState, layer: LayerState, outputs: OutputState) -> None:
    outputs.a = inputs.rf1 or inputs.lt6 or inputs.rf12 or inputs.rf15
    outputs.b = inputs.rf5 or inputs.lf4 or inputs.rf7 or (layer.layer_direction_active and not inputs.lf4 and inputs.rf3)
    outputs.x = inputs.rf2 and not layer.rf2_suppressed_by_lf4_submode_cstick and (
        not layer.layer_direction_active or inputs.lf4
    )
    outputs.y = inputs.rf10
    outputs.buttonL = inputs.lt3
    outputs.buttonR = inputs.rt1 or inputs.lt5 or inputs.rf11
    outputs.triggerLDigital = inputs.lt3
    outputs.triggerRDigital = inputs.rf16
    outputs.start = inputs.mb7
    outputs.select = inputs.mb6
    outputs.home = inputs.mb5
    outputs.capture = inputs.mb4


def apply_dpad_outputs(
    inputs: InputState,
    directions: EffectiveDirectionState,
    roles: RoleState,
    outputs: OutputState,
) -> None:
    outputs.dpadUp = False
    outputs.dpadDown = False
    outputs.dpadLeft = False
    outputs.dpadRight = False

    if inputs.nunchuk_c:
        outputs.dpadUp = inputs.rt5
        outputs.dpadDown = inputs.rt2
        outputs.dpadLeft = inputs.rt3
        outputs.dpadRight = inputs.rt4

    if roles.ls_to_dpad_active:
        outputs.dpadUp = outputs.dpadUp or directions.up
        outputs.dpadDown = outputs.dpadDown or directions.down
        outputs.dpadLeft = outputs.dpadLeft or directions.left
        outputs.dpadRight = outputs.dpadRight or directions.right


def apply_digital_direction_outputs(
    directions: EffectiveDirectionState,
    roles: RoleState,
    outputs: OutputState,
) -> None:
    outputs.leftStickLeft = False if roles.ls_to_dpad_active else directions.left
    outputs.leftStickRight = False if roles.ls_to_dpad_active else directions.right
    outputs.leftStickDown = False if roles.ls_to_dpad_active else directions.down
    outputs.leftStickUp = False if roles.ls_to_dpad_active else directions.up


def apply_right_stick_digital_outputs(inputs: InputState, outputs: OutputState) -> None:
    outputs.rightStickLeft = inputs.rt3
    outputs.rightStickRight = inputs.rt4
    outputs.rightStickDown = inputs.rt2
    outputs.rightStickUp = inputs.rt5


def select_stick_table(
    mode_active: bool,
    x1_active: bool,
    x2_active: bool,
    y1_active: bool,
    layer_normal_x_active: bool,
    layer_flipper_active: bool,
    tilt1_effective: bool,
    tilt2_effective: bool,
    tilt3_effective: bool,
) -> str:
    y1_tilt1_special_active = (
        y1_active
        and tilt1_effective
        and not x1_active
        and not x2_active
        and not tilt2_effective
        and not tilt3_effective
    )
    if y1_tilt1_special_active:
        return "MY1Tilt1" if mode_active else "Y1Tilt1"

    layer_flipper_effective = layer_flipper_active
    layer_normal_x_effective = layer_normal_x_active and not layer_flipper_effective

    y1_layer_normal_x_special_active = (
        y1_active
        and layer_normal_x_effective
        and not x1_active
        and not x2_active
        and not tilt1_effective
        and not tilt2_effective
        and not tilt3_effective
    )
    if y1_layer_normal_x_special_active:
        return "MY1LayerNormalX" if mode_active else "Y1LayerNormalX"

    y1_layer_flipper_special_active = (
        y1_active
        and layer_flipper_effective
        and not x1_active
        and not x2_active
        and not tilt1_effective
        and not tilt2_effective
        and not tilt3_effective
    )
    if y1_layer_flipper_special_active:
        return "MY1LayerFlipper" if mode_active else "Y1LayerFlipper"

    active_modifier_count = 0
    single_modifier = "None"

    for active, modifier in (
        (x1_active, "X1"),
        (x2_active, "X2"),
        (y1_active, "Y1"),
        (layer_normal_x_effective, "LayerNormalX"),
        (layer_flipper_effective, "LayerFlipper"),
    ):
        if active:
            active_modifier_count += 1
            single_modifier = modifier

    if tilt3_effective:
        active_modifier_count += 1
        single_modifier = "Tilt3"
    elif tilt1_effective:
        active_modifier_count += 1
        single_modifier = "Tilt1"
    elif tilt2_effective:
        active_modifier_count += 1
        single_modifier = "Tilt2"

    if active_modifier_count != 1:
        return "ModeDefault" if mode_active else "Default"

    if not mode_active:
        return single_modifier

    return {
        "X1": "MX1",
        "X2": "MX2",
        "Y1": "MY1",
        "LayerNormalX": "MLayerNormalX",
        "LayerFlipper": "MLayerFlipper",
        "Tilt1": "MTilt1",
        "Tilt2": "MTilt2",
        "Tilt3": "MTilt3",
    }.get(single_modifier, "ModeDefault")


def direction_index_from_axes(x_axis: int, y_axis: int) -> int:
    x = max(-1, min(1, x_axis))
    y = max(-1, min(1, y_axis))
    return ((y + 1) * 3) + (x + 1)


def apply_table_analog_output(table_name: str, x_axis: int, y_axis: int, outputs: OutputState) -> None:
    direction_index = direction_index_from_axes(x_axis, y_axis)
    outputs.leftStickX, outputs.leftStickY = TABLES[table_name][direction_index]


def apply_direction_plus_a_override(roles: RoleState, outputs: OutputState) -> None:
    if not roles.direction_plus_a_active:
        return

    table_name = "ModeDefault" if roles.mode_active else "Default"
    direction_index = K_DIRECTION_EIGHT_INDEX if roles.direction_plus_a_force_up else K_DIRECTION_TWO_INDEX
    outputs.leftStickX, outputs.leftStickY = TABLES[table_name][direction_index]


def apply_z_airdodge_override(directions: EffectiveDirectionState, outputs: OutputState) -> None:
    lt1_x = 0 if directions.left == directions.right else (-1 if directions.left else 1)
    lt1_y = 0 if directions.down == directions.up else (-1 if directions.down else 1)
    direction_index = direction_index_from_axes(lt1_x, lt1_y)
    outputs.leftStickX, outputs.leftStickY = TABLES["Lt1LowMagnitude"][direction_index]


def apply_hard_up_b_override(directions: EffectiveDirectionState, outputs: OutputState) -> None:
    rf7_horizontal = 128 if directions.left == directions.right else (77 if directions.left else 179)
    outputs.leftStickX = rf7_horizontal
    outputs.leftStickY = 172


def apply_null_override(outputs: OutputState) -> None:
    outputs.leftStickX = 128
    outputs.leftStickY = 128


def update_directions(
    ls_left: bool,
    ls_right: bool,
    ls_down: bool,
    ls_up: bool,
    rs_left: bool,
    rs_right: bool,
    rs_down: bool,
    rs_up: bool,
    outputs: OutputState,
) -> StickDirections:
    directions = StickDirections()
    outputs.leftStickX = ANALOG_STICK_NEUTRAL
    outputs.leftStickY = ANALOG_STICK_NEUTRAL
    outputs.rightStickX = ANALOG_STICK_NEUTRAL
    outputs.rightStickY = ANALOG_STICK_NEUTRAL

    if ls_left or ls_right:
        directions.horizontal = True
        if ls_left:
            directions.x = -1
            outputs.leftStickX = ANALOG_STICK_MIN
        else:
            directions.x = 1
            outputs.leftStickX = ANALOG_STICK_MAX

    if ls_down or ls_up:
        directions.vertical = True
        if ls_down:
            directions.y = -1
            outputs.leftStickY = ANALOG_STICK_MIN
        else:
            directions.y = 1
            outputs.leftStickY = ANALOG_STICK_MAX

    directions.diagonal = directions.horizontal and directions.vertical

    if rs_left or rs_right:
        if rs_left:
            directions.cx = -1
            outputs.rightStickX = ANALOG_STICK_MIN
        else:
            directions.cx = 1
            outputs.rightStickX = ANALOG_STICK_MAX

    if rs_down or rs_up:
        if rs_down:
            directions.cy = -1
            outputs.rightStickY = ANALOG_STICK_MIN
        else:
            directions.cy = 1
            outputs.rightStickY = ANALOG_STICK_MAX

    return directions


def evaluate_case(case: dict[str, Any]) -> Evaluation:
    inputs = input_state_from_case(case)
    outputs = OutputState()

    digital_layer = resolve_layer_state(inputs)
    digital_effective_directions = resolve_effective_directions(inputs, digital_layer)
    digital_roles = resolve_role_state(inputs, digital_layer, digital_effective_directions)
    apply_digital_button_outputs(inputs, digital_layer, outputs)
    apply_dpad_outputs(inputs, digital_effective_directions, digital_roles, outputs)
    apply_digital_direction_outputs(digital_effective_directions, digital_roles, outputs)
    apply_right_stick_digital_outputs(inputs, outputs)

    analog_layer = resolve_layer_state(inputs)
    analog_effective_directions = resolve_effective_directions(inputs, analog_layer)
    analog_roles = resolve_role_state(inputs, analog_layer, analog_effective_directions)
    directions = update_directions(
        analog_effective_directions.left,
        analog_effective_directions.right,
        analog_effective_directions.down,
        analog_effective_directions.up,
        inputs.rt3,
        inputs.rt4,
        inputs.rt2,
        inputs.rt5,
        outputs,
    )

    table_name = select_stick_table(
        analog_roles.mode_active,
        analog_roles.x1_active,
        analog_roles.x2_active,
        analog_roles.y1_active,
        analog_roles.layer_rf3_normal_x_active,
        analog_roles.rf4_layer_flipper_active,
        analog_roles.tilt1_effective,
        analog_roles.tilt2_effective,
        analog_roles.tilt3_effective,
    )

    if analog_roles.ls_to_dpad_active:
        center_table = "ModeDefault" if analog_roles.mode_active else "Default"
        outputs.leftStickX, outputs.leftStickY = TABLES[center_table][K_DIRECTION_FIVE_INDEX]
    else:
        apply_table_analog_output(table_name, directions.x, directions.y, outputs)
        apply_direction_plus_a_override(analog_roles, outputs)

        if analog_roles.z_airdodge_override_active:
            apply_z_airdodge_override(analog_effective_directions, outputs)

        if analog_roles.hard_up_b_active:
            apply_hard_up_b_override(analog_effective_directions, outputs)

    if analog_roles.null_modifier_active:
        apply_null_override(outputs)

    if directions.cx != 0 and directions.cy != 0:
        outputs.rightStickX = 128 + (directions.cx * 42)
        outputs.rightStickY = 128 + (directions.cy * 68)

    outputs.triggerLAnalog = 140 if outputs.triggerLDigital else 0
    outputs.triggerRAnalog = 140 if outputs.triggerRDigital else 0

    if inputs.nunchuk_c:
        outputs.rightStickX = 128
        outputs.rightStickY = 128

    if inputs.nunchuk_connected:
        outputs.leftStickX = inputs.nunchuk_x
        outputs.leftStickY = inputs.nunchuk_y

    return Evaluation(
        input_state=inputs,
        effective_directions=analog_effective_directions,
        roles=analog_roles,
        outputs=outputs,
        table_name=table_name,
    )


def actual_digital_button_labels(outputs: OutputState) -> set[str]:
    actual: set[str] = set()
    for label, fields in DIGITAL_BUTTON_FIELDS.items():
        if any(getattr(outputs, field) for field in fields):
            actual.add(label)
    return actual


def compare_expected(case: dict[str, Any], evaluation: Evaluation) -> list[Mismatch]:
    case_id = case["case_id"]
    expected = case.get("expected", {})
    outputs = evaluation.outputs
    mismatches: list[Mismatch] = []

    unsupported_fields = sorted(set(expected) - SUPPORTED_EXPECTED_FIELDS)
    for field in unsupported_fields:
        mismatches.append(Mismatch(case_id, field, "supported expected field", "unsupported expected field"))

    if "digital_buttons" in expected:
        expected_labels = expected["digital_buttons"]
        if not isinstance(expected_labels, list):
            mismatches.append(Mismatch(case_id, "digital_buttons", "list", type(expected_labels).__name__))
        else:
            unknown_labels = sorted(label for label in expected_labels if label not in DIGITAL_BUTTON_FIELDS)
            for label in unknown_labels:
                mismatches.append(Mismatch(case_id, f"digital_buttons.{label}", "known button label", "unknown button label"))

            actual_labels = actual_digital_button_labels(outputs)
            if set(expected_labels) != actual_labels:
                mismatches.append(Mismatch(case_id, "digital_buttons", sorted(expected_labels), sorted(actual_labels)))

            for label in expected_labels:
                for field in DIGITAL_BUTTON_FIELDS.get(label, ()):
                    if not getattr(outputs, field):
                        mismatches.append(Mismatch(case_id, f"digital_buttons.{label}.{field}", True, False))

    if "suppressed_buttons" in expected:
        for label in expected["suppressed_buttons"]:
            fields = DIGITAL_BUTTON_FIELDS.get(label)
            if fields is None:
                mismatches.append(Mismatch(case_id, f"suppressed_buttons.{label}", "known button label", "unknown button label"))
                continue
            for field in fields:
                actual = getattr(outputs, field)
                if actual:
                    mismatches.append(Mismatch(case_id, f"suppressed_buttons.{label}.{field}", False, actual))

    if "effective_direction" in expected:
        compare_direction_dict(
            case_id,
            "effective_direction",
            expected["effective_direction"],
            {
                "left": evaluation.effective_directions.left,
                "right": evaluation.effective_directions.right,
                "up": evaluation.effective_directions.up,
                "down": evaluation.effective_directions.down,
            },
            mismatches,
        )

    if expected.get("left_stick") is not None:
        actual_left_stick = [outputs.leftStickX, outputs.leftStickY]
        if expected["left_stick"] != actual_left_stick:
            mismatches.append(Mismatch(case_id, "left_stick", expected["left_stick"], actual_left_stick))

    if expected.get("right_stick") is not None:
        actual_right_stick = [outputs.rightStickX, outputs.rightStickY]
        if expected["right_stick"] != actual_right_stick:
            mismatches.append(Mismatch(case_id, "right_stick", expected["right_stick"], actual_right_stick))

    if expected.get("dpad") is not None:
        compare_direction_dict(
            case_id,
            "dpad",
            expected["dpad"],
            {
                "left": outputs.dpadLeft,
                "right": outputs.dpadRight,
                "up": outputs.dpadUp,
                "down": outputs.dpadDown,
            },
            mismatches,
        )

    if expected.get("right_stick_digital") is not None:
        compare_direction_dict(
            case_id,
            "right_stick_digital",
            expected["right_stick_digital"],
            {
                "left": outputs.rightStickLeft,
                "right": outputs.rightStickRight,
                "up": outputs.rightStickUp,
                "down": outputs.rightStickDown,
            },
            mismatches,
        )

    if expected.get("left_stick_digital") is not None:
        compare_direction_dict(
            case_id,
            "left_stick_digital",
            expected["left_stick_digital"],
            {
                "left": outputs.leftStickLeft,
                "right": outputs.leftStickRight,
                "up": outputs.leftStickUp,
                "down": outputs.leftStickDown,
            },
            mismatches,
        )

    if "trigger_analog" in expected:
        for trigger, expected_value in expected["trigger_analog"].items():
            if trigger == "L":
                actual = outputs.triggerLAnalog
            elif trigger == "R":
                actual = outputs.triggerRAnalog
            else:
                mismatches.append(Mismatch(case_id, f"trigger_analog.{trigger}", "L or R", "unknown trigger"))
                continue
            if expected_value != actual:
                mismatches.append(Mismatch(case_id, f"trigger_analog.{trigger}", expected_value, actual))

    if "suppressed_directions" in expected:
        for direction in expected["suppressed_directions"]:
            direction_field = DIRECTION_FIELDS.get(direction)
            if direction_field is None:
                mismatches.append(Mismatch(case_id, f"suppressed_directions.{direction}", "known direction", "unknown direction"))
                continue
            effective_actual = getattr(evaluation.effective_directions, direction_field)
            digital_actual = getattr(outputs, f"leftStick{direction}")
            if effective_actual:
                mismatches.append(Mismatch(case_id, f"suppressed_directions.{direction}.effective", False, effective_actual))
            if digital_actual:
                mismatches.append(Mismatch(case_id, f"suppressed_directions.{direction}.digital", False, digital_actual))

    if "suppressed_modifiers" in expected:
        for modifier in expected["suppressed_modifiers"]:
            role_field = ROLE_MODIFIER_FIELDS.get(modifier)
            if role_field is None:
                mismatches.append(Mismatch(case_id, f"suppressed_modifiers.{modifier}", "known modifier", "unknown modifier"))
                continue
            actual = getattr(evaluation.roles, role_field)
            if actual:
                mismatches.append(Mismatch(case_id, f"suppressed_modifiers.{modifier}", False, actual))

    if "hardware_status" in expected:
        actual_hardware_status = "not_hardware_validated"
        if expected["hardware_status"] != actual_hardware_status:
            mismatches.append(Mismatch(case_id, "hardware_status", expected["hardware_status"], actual_hardware_status))

    return mismatches


def compare_direction_dict(
    case_id: str,
    field: str,
    expected: Any,
    actual: dict[str, bool],
    mismatches: list[Mismatch],
) -> None:
    if not isinstance(expected, dict):
        mismatches.append(Mismatch(case_id, field, "dict", type(expected).__name__))
        return

    for direction, expected_value in expected.items():
        if direction not in actual:
            mismatches.append(Mismatch(case_id, f"{field}.{direction}", "known direction", "unknown direction"))
            continue
        actual_value = bool(actual[direction])
        if bool(expected_value) != actual_value:
            mismatches.append(Mismatch(case_id, f"{field}.{direction}", bool(expected_value), actual_value))


def format_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def print_mismatches(mismatches: list[Mismatch]) -> None:
    if not mismatches:
        return

    print("mismatches:")
    for mismatch in mismatches:
        print(
            "- "
            f"case_id={mismatch.case_id} "
            f"field={mismatch.field} "
            f"expected={format_value(mismatch.expected)} "
            f"actual={format_value(mismatch.actual)}"
        )


def main() -> int:
    print("glyph_identity_runtime_behavior_evaluator")

    checker_result = run_structural_checker()
    checker_output = "\n".join(part for part in (checker_result.stdout.strip(), checker_result.stderr.strip()) if part)
    if checker_result.returncode != 0:
        print("status=FAIL")
        print("cases_evaluated=0")
        print("fixture_checker_status=FAIL")
        print("table_source_sync_status=NOT_RUN")
        print("hardware_status=not_new_hardware_result")
        print("nunchuk_status=preserved_but_not_hardware_validated")
        if checker_output:
            print("fixture_checker_output:")
            print(checker_output)
        return checker_result.returncode

    table_sync_result = run_table_source_sync_checker()
    table_sync_output = "\n".join(part for part in (table_sync_result.stdout.strip(), table_sync_result.stderr.strip()) if part)
    if table_sync_result.returncode != 0:
        print("status=FAIL")
        print("cases_evaluated=0")
        print("fixture_checker_status=PASS")
        print("table_source_sync_status=FAIL")
        print("hardware_status=not_new_hardware_result")
        print("nunchuk_status=preserved_but_not_hardware_validated")
        if table_sync_output:
            print("table_source_sync_output:")
            print(table_sync_output)
        return table_sync_result.returncode

    missing_anchors = validate_source_anchors()
    if missing_anchors:
        print("status=FAIL")
        print("cases_evaluated=0")
        print("fixture_checker_status=PASS")
        print("table_source_sync_status=PASS")
        print("source_anchor_status=FAIL")
        print("hardware_status=not_new_hardware_result")
        print("nunchuk_status=preserved_but_not_hardware_validated")
        print("missing_source_anchors:")
        for anchor in missing_anchors:
            print(f"- {anchor}")
        print("source_shape_changed=mirror_evaluator_needs_review")
        return 1

    fixture = load_fixture()
    cases = fixture.get("cases", [])
    mismatches: list[Mismatch] = []

    for case in cases:
        case_id = case.get("case_id", "<unknown>")
        try:
            evaluation = evaluate_case(case)
        except EvaluationError as exc:
            mismatches.append(Mismatch(case_id, "case", "evaluable source-backed input", str(exc)))
            continue
        mismatches.extend(compare_expected(case, evaluation))

    print(f"status={'FAIL' if mismatches else 'PASS'}")
    print(f"cases_evaluated={len(cases)}")
    print("fixture_checker_status=PASS")
    print("table_source_sync_status=PASS")
    print("source_anchor_status=PASS")
    print("hardware_status=not_new_hardware_result")
    print("nunchuk_status=preserved_but_not_hardware_validated")
    print_mismatches(mismatches)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
