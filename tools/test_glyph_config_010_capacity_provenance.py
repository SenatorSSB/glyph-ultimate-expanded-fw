#!/usr/bin/env python3
"""Adversarial input checks for GP-VAL-028's generated capacity proof."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from check_glyph_config_010_mode_activation_capacity import (
    ContractError, ROOT, validate_inputs,
)

INPUTS = [
    "docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json",
    "tools/fixtures/mode_selection_host/generated/config.pb.h",
    "tools/fixtures/mode_selection_host/generated/provenance.json",
    "tools/fixtures/mode_selection_host/generated/nanopb.library.json",
    "tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt",
    "tools/fixtures/mode_selection_host/include/config.pb.h",
    "tools/fixtures/custom_modifier_cache_host/schema/config.proto",
    "tools/fixtures/custom_modifier_cache_host/schema/config.options",
    "config/glyph/env.ini",
    "platformio.ini",
    "src/core/mode_selection.cpp",
    "config/glyph/common/include/glyph_overrides.hpp",
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "tools/fixtures/mode_selection_host/generated/README.md",
]


def copy_inputs(root: Path) -> None:
    for name in INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", "--", *INPUTS], cwd=root, check=True)


def change(root: Path, name: str, old: str, new: str) -> None:
    path = root / name
    data = path.read_text(encoding="utf-8")
    assert old in data, (name, old)
    path.write_text(data.replace(old, new, 1), encoding="utf-8")


def mutate_manifest(root: Path, change_dependencies) -> None:
    path = root / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entry = next(item for item in manifest["entries"] if item["id"] == "gp_config_010_mode_activation_capacity")
    change_dependencies(entry["source_dependencies"])
    path.write_text(json.dumps(manifest), encoding="utf-8")


def mutate_fixture(root: Path, change_sources) -> None:
    path = root / "docs/runtime_config/fixtures/gp_config_010_mode_activation_capacity.json"
    fixture = json.loads(path.read_text(encoding="utf-8"))
    change_sources(fixture["production_sources"])
    path.write_text(json.dumps(fixture), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-capacity-positive-") as directory:
        root = Path(directory)
        copy_inputs(root)
        validate_inputs(root)
    cases = [
        ("missing header", "missing regular generated fixture", lambda r: (r / INPUTS[1]).unlink()),
        ("tampered header", "staged generated fixture drift", lambda r: change(r, INPUTS[1], "nanopb-0.4.9.2", "nanopb-0.4.9.3")),
        ("provenance", "staged generated fixture drift", lambda r: change(r, INPUTS[2], '"work_order": "GP-VAL-028"', '"work_order": "GP-VAL-999"')),
        ("version", "staged generated fixture drift", lambda r: change(r, INPUTS[3], '"version": "0.4.92"', '"version": "0.4.91"')),
        ("license", "staged generated fixture drift", lambda r: (r / INPUTS[4]).write_bytes(b"tampered license")),
        ("proto", "proto drift", lambda r: (r / INPUTS[6]).write_bytes((r / INPUTS[6]).read_bytes() + b"\n")),
        ("options", "options drift", lambda r: (r / INPUTS[7]).write_bytes((r / INPUTS[7]).read_bytes() + b"\n")),
        ("HayBox selector", "HayBox selector drift", lambda r: change(r, INPUTS[8], "HayBox-proto#db4e2f6", "HayBox-proto#0000000")),
        ("Nanopb selector", "Nanopb selector drift", lambda r: change(r, INPUTS[9], "nanopb/Nanopb@^0.4.8", "nanopb/Nanopb@0.4.91")),
        ("host double", "host double drift", lambda r: change(r, INPUTS[5], "game_mode_configs[30]", "game_mode_configs[29]")),
        ("active source", "source drift", lambda r: change(r, INPUTS[10], "kModeActivationMaskCapacity = 30", "kModeActivationMaskCapacity = 29")),
        ("fixture authority", "generated fixture identity", lambda r: change(r, INPUTS[0], "bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323", "0" * 64)),
        ("untracked correct bytes", "generated fixture closure must be tracked", lambda r: subprocess.run(["git", "rm", "--cached", "-q", "--", INPUTS[1]], cwd=r, check=True)),
        ("missing manifest dependency", "capacity manifest dependency closure", lambda r: mutate_manifest(r, lambda deps: deps.remove("config/glyph/env.ini"))),
        ("wrong manifest dependency", "capacity manifest dependency closure", lambda r: mutate_manifest(r, lambda deps: deps.__setitem__(deps.index("config/glyph/env.ini"), "config/glyph/wrong.ini"))),
        ("missing source record", "ordered production-source closure", lambda r: mutate_fixture(r, lambda sources: sources.pop())),
    ]
    for label, expected, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="glyph-capacity-negative-") as directory:
            root = Path(directory)
            copy_inputs(root)
            mutate(root)
            try:
                validate_inputs(root)
            except ContractError as exc:
                assert expected in str(exc), (label, str(exc))
                continue
            raise AssertionError(f"accepted {label} drift")
    print(f"glyph_config_010_capacity_provenance: PASS; {len(cases)} adversarial cases and exact manifest closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
