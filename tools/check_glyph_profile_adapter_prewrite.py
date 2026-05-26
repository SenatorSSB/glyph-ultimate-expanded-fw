#!/usr/bin/env python3
"""Read-only prewrite validation for future Glyph profile adapter output.

This tool intentionally does not normalize, rewrite, reorder, or emit adapter output.
It reports source-backed structural errors separately from policy/corpus decision
surfaces so future write-capable work can fail only on actual structural faults.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODE_ACTIVATION_MASK_CAPACITY = 10


@dataclass
class ModeSignal:
    label: str
    omitted_activates: int = 0
    explicit_unspecified: int = 0
    duplicate_physical: dict[str, int] = field(default_factory=dict)
    many_to_one_aliases: dict[str, int] = field(default_factory=dict)
    omitted_socd_type: int = 0


@dataclass
class FileResult:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    game_modes_count: int = 0
    backend_configs_count: int = 0
    omitted_activates: int = 0
    explicit_unspecified: int = 0
    omitted_socd_type: int = 0
    omitted_default_mode_by_backend: list[str] = field(default_factory=list)
    mode_signals: list[ModeSignal] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only prewrite validation for explicit Glyph profile JSON fixture paths. "
            "Warnings are decision surfaces; errors are structural."
        ),
    )
    parser.add_argument("fixtures", nargs="+", type=Path, help="Explicit JSON fixture path(s) to inspect.")
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_object(path: Path, result: FileResult) -> dict[str, Any] | None:
    if not path.exists():
        result.errors.append(f"missing fixture: {display_path(path)}")
        return None
    if not path.is_file():
        result.errors.append(f"fixture is not a file: {display_path(path)}")
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as exc:  # pragma: no cover - defensive parse guard
        result.errors.append(f"failed to parse JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        result.errors.append("root JSON value must be an object")
        return None
    return payload


def optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def validate_one_based_index(
    result: FileResult,
    *,
    label: str,
    value: Any,
    upper_bound: int,
    zero_policy_warning: bool,
) -> None:
    index = optional_int(value)
    if index is None:
        result.errors.append(f"{label} must be an integer when present")
        return
    if index < 0:
        result.errors.append(f"{label} must not be negative, got {index}")
        return
    if index == 0:
        if zero_policy_warning:
            result.warnings.append(
                f"{label}=0 is source-confirmed as not rejected by current validation, "
                "but outbound adapter use still needs policy approval",
            )
        else:
            result.errors.append(f"{label} must be one-based, got 0")
        return
    if index > upper_bound:
        result.errors.append(f"{label}={index} exceeds available count {upper_bound}")


def analyze_fixture(path: Path) -> FileResult:
    result = FileResult(path=path)
    payload = load_json_object(path, result)
    if payload is None:
        return result

    game_modes = payload.get("gameModeConfigs")
    backend_configs = payload.get("communicationBackendConfigs")

    if not isinstance(game_modes, list):
        result.errors.append("gameModeConfigs must be present as a list")
        game_modes = []
    if not isinstance(backend_configs, list):
        result.errors.append("communicationBackendConfigs must be present as a list")
        backend_configs = []

    result.game_modes_count = len(game_modes)
    result.backend_configs_count = len(backend_configs)

    if result.game_modes_count > MODE_ACTIVATION_MASK_CAPACITY:
        result.warnings.append(
            "gameModeConfigs count exceeds known mode activation-mask capacity "
            f"({result.game_modes_count} > {MODE_ACTIVATION_MASK_CAPACITY})",
        )

    for field_name in ("defaultBackendConfig", "defaultUsbBackendConfig"):
        if field_name in payload:
            validate_one_based_index(
                result,
                label=field_name,
                value=payload[field_name],
                upper_bound=result.backend_configs_count,
                zero_policy_warning=True,
            )

    for backend_index, backend in enumerate(backend_configs):
        if not isinstance(backend, dict):
            result.errors.append(f"communicationBackendConfigs[{backend_index}] must be an object")
            continue
        backend_id = backend.get("backendId")
        backend_label = backend_id if isinstance(backend_id, str) and backend_id else f"index_{backend_index + 1}"
        if "defaultModeConfig" not in backend:
            result.omitted_default_mode_by_backend.append(backend_label)
        else:
            validate_one_based_index(
                result,
                label=f"communicationBackendConfigs[{backend_index}].defaultModeConfig({backend_label})",
                value=backend.get("defaultModeConfig"),
                upper_bound=result.game_modes_count,
                zero_policy_warning=True,
            )

    for mode_index, mode in enumerate(game_modes):
        if not isinstance(mode, dict):
            result.errors.append(f"gameModeConfigs[{mode_index}] must be an object")
            continue
        name = mode.get("name")
        mode_id = mode.get("modeId")
        label = f"{name if isinstance(name, str) and name else 'index_' + str(mode_index)}/{mode_id if isinstance(mode_id, str) and mode_id else '<missing_mode_id>'}"
        signal = ModeSignal(label=label)

        socd_pairs = mode.get("socdPairs", [])
        if socd_pairs is None:
            socd_pairs = []
        if not isinstance(socd_pairs, list):
            result.errors.append(f"gameModeConfigs[{mode_index}].socdPairs must be a list when present")
            socd_pairs = []
        for pair_index, pair in enumerate(socd_pairs):
            if not isinstance(pair, dict):
                result.errors.append(f"gameModeConfigs[{mode_index}].socdPairs[{pair_index}] must be an object")
                continue
            if "socdType" not in pair:
                signal.omitted_socd_type += 1
                result.omitted_socd_type += 1

        remaps = mode.get("buttonRemapping", [])
        if remaps is None:
            remaps = []
        if not isinstance(remaps, list):
            result.errors.append(f"gameModeConfigs[{mode_index}].buttonRemapping must be a list when present")
            remaps = []

        physical_counter: Counter[str] = Counter()
        activates_counter: Counter[str] = Counter()

        for remap_index, remap in enumerate(remaps):
            if not isinstance(remap, dict):
                result.errors.append(
                    f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}] must be an object",
                )
                continue
            physical = remap.get("physicalButton")
            if not isinstance(physical, str) or not physical:
                result.errors.append(
                    f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}].physicalButton must be a non-empty string",
                )
            else:
                physical_counter[physical] += 1

            if "activates" not in remap:
                signal.omitted_activates += 1
                result.omitted_activates += 1
                continue
            activates = remap.get("activates")
            if not isinstance(activates, str) or not activates:
                result.errors.append(
                    f"gameModeConfigs[{mode_index}].buttonRemapping[{remap_index}].activates must be a non-empty string when present",
                )
                continue
            if activates == "BTN_UNSPECIFIED":
                signal.explicit_unspecified += 1
                result.explicit_unspecified += 1
            else:
                activates_counter[activates] += 1

        signal.duplicate_physical = {button: count for button, count in physical_counter.items() if count > 1}
        signal.many_to_one_aliases = {button: count for button, count in activates_counter.items() if count > 1}
        result.mode_signals.append(signal)

    return result


def print_result(result: FileResult) -> None:
    print(f"[{display_path(result.path)}]")
    print(f"- gameModeConfigs={result.game_modes_count}")
    print(f"- communicationBackendConfigs={result.backend_configs_count}")
    print(f"- omitted_activates={result.omitted_activates}")
    print(f"- explicit_BTN_UNSPECIFIED={result.explicit_unspecified}")
    print(f"- omitted_socdType={result.omitted_socd_type}")
    if result.omitted_default_mode_by_backend:
        print("- omitted_defaultModeConfig_by_backend=" + ", ".join(result.omitted_default_mode_by_backend))
    else:
        print("- omitted_defaultModeConfig_by_backend=none")

    alias_modes = [signal for signal in result.mode_signals if signal.many_to_one_aliases]
    if alias_modes:
        print("- many_to_one_logical_aliases:")
        for signal in alias_modes:
            rendered = ", ".join(f"{button}({count})" for button, count in sorted(signal.many_to_one_aliases.items()))
            print(f"  - {signal.label}: {rendered}")
    else:
        print("- many_to_one_logical_aliases: none")

    duplicate_modes = [signal for signal in result.mode_signals if signal.duplicate_physical]
    if duplicate_modes:
        print("- duplicate_physical_remaps:")
        for signal in duplicate_modes:
            rendered = ", ".join(f"{button}({count})" for button, count in sorted(signal.duplicate_physical.items()))
            print(f"  - {signal.label}: {rendered}")
    else:
        print("- duplicate_physical_remaps: none")

    if result.warnings:
        print("- warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    if result.errors:
        print("- errors:")
        for error in result.errors:
            print(f"  - {error}")
    print()


def main() -> int:
    args = parse_args()
    results = [analyze_fixture(path if path.is_absolute() else REPO_ROOT / path) for path in args.fixtures]
    has_errors = False
    for result in results:
        print_result(result)
        if result.errors:
            has_errors = True
    if has_errors:
        print("result=FAIL")
        return 1
    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
