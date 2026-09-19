#!/usr/bin/env python3
"""Validate the exact-source GP-CONFIG-008 rebinding characterization record."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/runtime_config/fixtures/setconfig_runtime_rebinding_characterization.json"
EXPECTED_CASES = [
    "successful_setconfig_live_config_visibility", "old_activation_chord_mask",
    "same_index_selection_suppressed", "different_index_mode_selection",
    "same_mode_object_reconfigured", "different_mode_object_selection",
    "custom_mode_cached_masks", "generic_inputmode_pointer", "backend_boot_binding",
    "neopixel_rgb_cache_and_brightness", "display_menu_binding",
    "source_path_boot_reconstruction", "display_backend_id_capture",
]
EXPECTED_SOURCES = [
    "HAL/pico/src/comms/ConfiguratorBackend.cpp", "src/core/mode_selection.cpp",
    "src/core/InputMode.cpp", "src/modes/CustomControllerMode.cpp",
    "HAL/pico/src/comms/backend_init.cpp", "HAL/pico/include/comms/NeoPixelBackend.hpp",
    "config/glyph/common/src/config.cpp", "HAL/pico/src/display/InputDisplay.cpp",
]


class Error(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Error(message)


def validate_shape(value: dict) -> None:
    require(value["schema_name"] == "glyph_setconfig_runtime_rebinding_characterization", "fixture identity")
    require(value["schema_version"] == 1 and value["work_order"] == "GP-CONFIG-008", "fixture version/work order")
    require([item["path"] for item in value["production_sources"]] == EXPECTED_SOURCES, "ordered production-source set")
    require(value["cases"] == EXPECTED_CASES, "ordered case corpus")
    require(value["observations"]["non_claims"] == [
        "cross-core timing", "cross-core atomicity", "physical output", "performed reboot",
        "boot result after a new persisted config", "hardware acceptance"
    ], "non-claims")


def load() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    validate_shape(value)
    return value


def correspondence(value: dict) -> None:
    for record in value["production_sources"]:
        path = ROOT / record["path"]
        text = path.read_text(encoding="utf-8")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], f"source drift: {record['path']}")
        for anchor in record["anchors"]:
            require(anchor in text, f"missing source anchor {anchor} in {record['path']}")

    setconfig = (ROOT / "HAL/pico/src/comms/ConfiguratorBackend.cpp").read_text(encoding="utf-8")
    handler = setconfig.index("bool ConfiguratorBackend::HandleSetConfig()")
    require(setconfig.index("persistence.SaveConfig(candidate)", handler) < setconfig.index("\n    _config = candidate;", handler), "publication order")
    require("HandleSetConfig" in setconfig and "setup_mode_activation_bindings" not in setconfig[handler:], "no automatic rebinding in handler")

    mode_selection = (ROOT / "src/core/mode_selection.cpp").read_text(encoding="utf-8")
    require("i != current_mode_index" in mode_selection and "setup_mode_activation_bindings" in mode_selection, "selection boundary")
    require("initialize_backends" in (ROOT / "HAL/pico/src/comms/backend_init.cpp").read_text(encoding="utf-8"), "boot boundary")
    config = (ROOT / "config/glyph/common/src/config.cpp").read_text(encoding="utf-8")
    require("void setup1()" in config and "void loop1()" in config and "led_backend->SetGameMode" in config, "second-core boundary")


def adversarial(value: dict) -> None:
    tampered = json.loads(json.dumps(value))
    tampered["production_sources"] = list(reversed(tampered["production_sources"]))
    try:
        validate_shape(tampered)
    except Error:
        pass
    else:
        raise Error("reversed source corpus accepted")
    tampered = json.loads(json.dumps(value))
    tampered["production_sources"] = tampered["production_sources"][:-1] + [tampered["production_sources"][-2]]
    try:
        validate_shape(tampered)
    except Error:
        pass
    else:
        raise Error("duplicate source corpus accepted")
    tampered = json.loads(json.dumps(value))
    tampered["cases"][0] = "renamed_case"
    try:
        validate_shape(tampered)
    except Error:
        pass
    else:
        raise Error("renamed case accepted")
    require("hardware acceptance" in value["observations"]["non_claims"], "hardware non-claim")


def main() -> int:
    try:
        value = load()
        correspondence(value)
        adversarial(value)
        print("glyph_setconfig_runtime_rebinding_characterization: PASS; 13 cases; H1 research only")
        return 0
    except (OSError, KeyError, TypeError, ValueError, Error) as exc:
        print(f"glyph_setconfig_runtime_rebinding_characterization: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
