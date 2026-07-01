#!/usr/bin/env python3
"""Check the requested Ultimate Tilt3/Y2 table and LT3 routing update.

This is a deterministic source/evaluator checker only. It is not hardware
validation and it does not exercise transport, storage, or device-write paths.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from check_glyph_identity_runtime_behavior_evaluator import (
    TABLES,
    actual_digital_button_labels,
    evaluate_case,
)
from extract_glyph_identity_runtime_tables import load_source_tables


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "src" / "modes" / "Ultimate.cpp"

EXPECTED_TILT3 = {
    1: (69, 82),
    2: (128, 83),
    3: (187, 82),
    4: (69, 128),
    5: (128, 128),
    6: (187, 128),
    7: (76, 169),
    8: (128, 179),
    9: (180, 169),
}

EXPECTED_Y2 = {
    1: (69, 78),
    2: (128, 78),
    3: (187, 78),
    4: (61, 128),
    5: (128, 128),
    6: (195, 128),
    7: (61, 164),
    8: (128, 174),
    9: (195, 164),
}


class CheckFailure(AssertionError):
    pass


def fail(message: str) -> None:
    raise CheckFailure(message)


def assert_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def case(buttons: Iterable[str]) -> dict[str, object]:
    return {"case_id": "+".join(buttons), "input_buttons": list(buttons), "expected": {}}


def left_stick(buttons: Iterable[str]) -> tuple[int, int]:
    evaluation = evaluate_case(case(buttons))
    return (evaluation.outputs.leftStickX, evaluation.outputs.leftStickY)


def table_id(buttons: Iterable[str]) -> str:
    return evaluate_case(case(buttons)).table_id


def digital_buttons(buttons: Iterable[str]) -> set[str]:
    return actual_digital_button_labels(evaluate_case(case(buttons)).outputs)


def validate_source_tables() -> None:
    source_tables = load_source_tables(SOURCE_PATH)
    for table_name, expected in (("Tilt3", EXPECTED_TILT3), ("Y2", EXPECTED_Y2)):
        actual = source_tables.get(table_name)
        if actual is None:
            fail(f"missing source table: {table_name}")
        for direction, expected_point in expected.items():
            assert_equal(
                f"{table_name} dir {direction}",
                actual[direction - 1],
                expected_point,
            )
            assert_equal(
                f"{table_name} evaluator dir {direction}",
                TABLES[table_name][direction - 1],
                expected_point,
            )

    assert_equal("Tilt3 neutral", source_tables["Tilt3"][4], EXPECTED_TILT3[5])
    assert_equal("Y2 neutral", source_tables["Y2"][4], EXPECTED_Y2[5])
    assert_equal("Y2 dir8 preserved", source_tables["Y2"][7], EXPECTED_Y2[8])


def validate_lt3_y2_only() -> None:
    evaluation = evaluate_case(case(["LT3"]))
    assert_equal("LT3 table", evaluation.table_id, "Y2")
    assert_equal("LT3 Y2 role", evaluation.roles.y2_active, True)
    assert_equal("LT3 digital buttons", actual_digital_button_labels(evaluation.outputs), set())
    assert_equal("LT3 L digital", evaluation.outputs.triggerLDigital, False)
    assert_equal("LT3 R digital", evaluation.outputs.triggerRDigital, False)
    assert_equal("LT3 L button", evaluation.outputs.buttonL, False)


def validate_tilt3_table_runtime_points() -> None:
    directions = {
        1: ["RT1", "RF4", "LF3", "LF5"],
        2: ["RT1", "RF4", "LF5"],
        3: ["RT1", "RF4", "LF1", "LF5"],
        4: ["RT1", "RF4", "LF3"],
        5: ["RT1", "RF4"],
        6: ["RT1", "RF4", "LF1"],
        7: ["RT1", "RF4", "LF3", "LF2"],
        8: ["RT1", "RF4", "LF2"],
        9: ["RT1", "RF4", "LF1", "LF2"],
    }
    for direction, buttons in directions.items():
        assert_equal(f"Tilt3 runtime dir {direction}", left_stick(buttons), EXPECTED_TILT3[direction])
        assert_equal(f"Tilt3 runtime table dir {direction}", table_id(buttons), "Tilt3")


def validate_y2_table_runtime_points() -> None:
    directions = {
        1: ["LT3", "LF3", "LF5"],
        2: ["LT3", "LF5"],
        3: ["LT3", "LF1", "LF5"],
        4: ["LT3", "LF3"],
        5: ["LT3"],
        6: ["LT3", "LF1"],
        7: ["LT3", "LF3", "LF2"],
        8: ["LT3", "LF2"],
        9: ["LT3", "LF1", "LF2"],
    }
    for direction, buttons in directions.items():
        assert_equal(f"Y2 runtime dir {direction}", left_stick(buttons), EXPECTED_Y2[direction])
        assert_equal(f"Y2 runtime table dir {direction}", table_id(buttons), "Y2")


def validate_sublayer_migration() -> None:
    assert_equal("Y2+RF1 emits X", digital_buttons(["LT3", "RF1"]), {"X"})
    assert_equal("Y1+RF1 no longer emits X sublayer", digital_buttons(["LT2", "RF1"]), {"A"})

    assert_equal("Y2+RF2 forces up without base B", digital_buttons(["LT3", "RF2"]), set())
    assert_equal("Y2+RF2 forced-up point", left_stick(["LT3", "RF2"]), (128, 205))
    assert_equal("Y1+RF2 no longer forces up", digital_buttons(["LT2", "RF2"]), {"B"})
    assert_equal("Y1+RF2 keeps Y1 neutral", left_stick(["LT2", "RF2"]), (128, 128))

    assert_equal("Y2+RF3 emits B", digital_buttons(["LT3", "RF3", "LF1"]), {"B"})
    assert_equal("Y2+RF3 table", table_id(["LT3", "RF3", "LF1"]), "LayerNormalX")
    assert_equal("Y2+RF3 point", left_stick(["LT3", "RF3", "LF1"]), (169, 128))
    assert_equal("Y1+RF3 no longer emits B sublayer", digital_buttons(["LT2", "RF3", "LF1"]), {"X"})
    assert_equal("Y1+RF3 table", table_id(["LT2", "RF3", "LF1"]), "Y1")

    assert_equal("Y2+RF4 table", table_id(["LT3", "RF4", "LF1"]), "LayerFlipper")
    assert_equal("Y2+RF4 point", left_stick(["LT3", "RF4", "LF1"]), (87, 128))
    assert_equal("Y1+RF4 no longer flipper sublayer", table_id(["LT2", "RF4", "LF1"]), "Default")


def validate_y2_priority() -> None:
    assert_equal("Y2+RT1 table", table_id(["LT3", "RT1", "LF1"]), "Tilt2")
    assert_equal("Y2+RT1 point", left_stick(["LT3", "RT1", "LF1"]), (168, 128))

    assert_equal("Y2+RF4 table", table_id(["LT3", "RF4", "LF1"]), "LayerFlipper")
    assert_equal("Y2+RF4 point", left_stick(["LT3", "RF4", "LF1"]), (87, 128))

    assert_equal("Y2+RT1+RF4 table", table_id(["LT3", "RT1", "RF4", "LF1"]), "Tilt3")
    assert_equal("Y2+RT1+RF4 point", left_stick(["LT3", "RT1", "RF4", "LF1"]), (187, 128))

    assert_equal("Y2+RF2+RF4 table", table_id(["LT3", "RF2", "RF4", "LF1"]), "LayerFlipper")
    assert_equal("Y2+RF2+RF4 point", left_stick(["LT3", "RF2", "RF4", "LF1"]), (87, 205))


def main() -> int:
    print("glyph_y2_tilt3_routing")
    try:
        validate_source_tables()
        validate_lt3_y2_only()
        validate_tilt3_table_runtime_points()
        validate_y2_table_runtime_points()
        validate_sublayer_migration()
        validate_y2_priority()
    except CheckFailure as exc:
        print("status=FAIL")
        print(f"failure={exc}")
        return 1

    print("status=PASS")
    print("hardware_status=not_new_hardware_result")
    print("tilt3_table=updated")
    print("y2_table=updated_dir8_preserved")
    print("lt3_role=Y2_only")
    print("y1_sublayer_role=migrated_to_y2")
    print("y2_priority=below_rt_rf_modifiers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
