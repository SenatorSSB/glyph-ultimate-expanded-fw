#!/usr/bin/env python3
"""Read-only checker for Glyph active Ultimate profile binding path trace."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRACE_DOC = (
    REPO_ROOT
    / "docs"
    / "calibration"
    / "glyph_active_profile_binding_path_trace_2026-05-27.md"
)
DEFAULT_SOURCE = REPO_ROOT / "config" / "glyph" / "common" / "include" / "glyph_overrides.hpp"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing required file: {path.relative_to(REPO_ROOT)}") from exc


def _require_regex(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) is None:
        raise AssertionError(f"missing required trace conclusion: {label}")


def _extract_ultimate_remap_block(source_text: str) -> str:
    match = re.search(
        r"\.mode_id\s*=\s*MODE_ULTIMATE\s*,.*?\.button_remapping\s*=\s*\{(?P<remaps>.*?)\}\s*,",
        source_text,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError("unable to locate MODE_ULTIMATE button_remapping block in default source")
    return match.group("remaps")


def _has_mapping(remap_block: str, physical_button: str, activates: str) -> bool:
    pattern = (
        r"ButtonRemap\s*\{\s*\.physical_button\s*=\s*"
        + re.escape(physical_button)
        + r"\s*,\s*\.activates\s*=\s*"
        + re.escape(activates)
        + r"\s*\}"
    )
    return re.search(pattern, remap_block) is not None


def main() -> int:
    failures: list[str] = []

    try:
        trace_text = _read_text(TRACE_DOC)
    except AssertionError as exc:
        print(f"failure={exc}")
        print("status=FAIL")
        return 1

    required_patterns = {
        "normal_update_profile_preservation": (
            r"normal firmware update.*(does not|doesn't).*(rewrite|overwrite|change).*(stored|persisted).*(profile|config)"
        ),
        "fixture_consumption_conclusion": (
            r"glyphuserprofilesultimatemvp01\.json.*(not|no).*(build-consumed|consumed).*(firmware|runtime)"
        ),
        "real_default_factory_source_conclusion": (
            r"config/glyph/common/include/glyph_overrides\.hpp.*(factory/default|default|build-consumed)"
        ),
        "lt3_binding_path_recommendation": (
            r"(option 2|recommendation).*(manual config import/write path|handlesetconfig|config import)"
        ),
    }

    for label, pattern in required_patterns.items():
        try:
            _require_regex(trace_text, pattern, label)
        except AssertionError as exc:
            failures.append(str(exc))

    source_text = _read_text(DEFAULT_SOURCE)
    remap_block = _extract_ultimate_remap_block(source_text)

    lt3_to_lt3 = _has_mapping(remap_block, "BTN_LT3", "BTN_LT3")
    rf3_to_lt1 = _has_mapping(remap_block, "BTN_RF3", "BTN_LT1")
    rf4_to_lt2 = _has_mapping(remap_block, "BTN_RF4", "BTN_LT2")

    mapping_presence_count = sum((lt3_to_lt3, rf3_to_lt1, rf4_to_lt2))
    build_consumed_source_updated = mapping_presence_count > 0

    if build_consumed_source_updated:
        if not lt3_to_lt3:
            failures.append("build-consumed source update is missing BTN_LT3 -> BTN_LT3")
        if not rf3_to_lt1:
            failures.append("build-consumed source update is missing BTN_RF3 -> BTN_LT1")
        if not rf4_to_lt2:
            failures.append("build-consumed source update is missing BTN_RF4 -> BTN_LT2")

    print(f"trace_doc={TRACE_DOC.relative_to(REPO_ROOT)}")
    print(f"default_source={DEFAULT_SOURCE.relative_to(REPO_ROOT)}")
    print(f"doc_exists={'true' if TRACE_DOC.exists() else 'false'}")
    print(
        "build_consumed_profile_source_updated="
        f"{'true' if build_consumed_source_updated else 'false'}"
    )
    print(f"default_source_btn_lt3_to_lt3={'true' if lt3_to_lt3 else 'false'}")
    print(f"default_source_btn_rf3_to_lt1={'true' if rf3_to_lt1 else 'false'}")
    print(f"default_source_btn_rf4_to_lt2={'true' if rf4_to_lt2 else 'false'}")
    print(
        "caveat=This checker verifies source-trace conclusions and source content only; "
        "it does not claim the active on-device profile was updated."
    )

    if failures:
        for failure in failures:
            print(f"failure={failure}")
        print("status=FAIL")
        return 1

    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
