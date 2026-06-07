#!/usr/bin/env python3
"""Validate Step 10 runtime-config storage/fallback docs and offline guardrails."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUTHORITY_DOC = (
    REPO_ROOT / "docs" / "runtime_config" / "runtime_config_storage_fallback_source_authority.md"
)
ARCHITECTURE_DOC = (
    REPO_ROOT / "docs" / "runtime_config" / "runtime_config_storage_fallback_architecture.md"
)

REQUIRED_PERSISTENCE_REFERENCES = (
    "HAL/pico/include/core/Persistence.hpp",
    "HAL/pico/src/core/Persistence.cpp",
    "config/glyph/common/src/config.cpp",
    "HAL/pico/src/comms/ConfiguratorBackend.cpp",
    "platformio.ini",
)

REQUIRED_SOURCE_DOC_PHRASES = (
    "implementation_allowed_by_source_audit=false",
    "source-backed persistence exists for the current protobuf `config` object",
    "step 10 firmware storage/fallback implementation is blocked",
    "must not modify firmware to consume runtime-loaded config from storage",
)

REQUIRED_ARCH_DOC_PHRASES = (
    "design-only and does not modify firmware source",
    "because `runtime_config_storage_fallback_source_authority.md` records",
    "that future path is not implemented here",
    "runtime-loaded storage is not implemented",
)

REQUIRED_HEADINGS = {
    "source": (
        "source-backed capabilities found",
        "unsupported assumptions",
        "unknowns",
        "forbidden or not approved",
    ),
    "arch": (
        "non-claims",
        "explicit stop line",
    ),
}

REQUIRED_SECTION_ASSERTS = (
    "runtime-loaded storage is not implemented",
    "runtime-loaded config consumption from storage is not implemented",
    "firmware binary/protobuf runtime-config parser integration is not implemented",
    "firmware-consuming manual runtime config load path is not implemented",
    "webserial/device write is not implemented",
    "direct device mutation workflow is not implemented",
    "firmware flashing automation is not implemented",
    "official protobuf compatibility is not claimed",
)


class RuntimeConfigStorageFallbackError(ValueError):
    """Raised when Step 10 fallback guardrails are not preserved."""


def fail(message: str) -> None:
    raise RuntimeConfigStorageFallbackError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def read_doc(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"missing required doc {path.relative_to(REPO_ROOT)}: {exc}")
    return ""


def ensure_headings(text: str, headings: tuple[str, ...], *, label: str) -> None:
    for heading in headings:
        token = f"## {heading}"
        if token.lower() not in text.lower():
            fail(f"{label} missing section heading: {heading}")


def ensure_phrases(text: str, phrases: tuple[str, ...], *, label: str) -> None:
    lowered = normalize(text)
    for phrase in phrases:
        if phrase not in lowered:
            fail(f"{label} missing required phrase: {phrase}")


def extract_bullet_items(text: str, heading: str) -> list[str]:
    pattern = rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing section for heading {heading}")
    block = match.group(1)
    items = [line.strip(" -") for line in block.splitlines() if line.strip().startswith("-")]
    return items


def ensure_section_is_nonempty(text: str, heading: str) -> None:
    items = extract_bullet_items(text, heading)
    if not items:
        fail(f"section {heading} must contain at least one bullet item")


def ensure_no_positive_implementation_claims(text: str, label: str) -> None:
    lowered = text.lower()
    deny_markers = (
        "not ",
        "no ",
        "does not",
        "do not",
        "must not",
        "should not",
        "did not",
    )
    targets = (
        "runtime-loaded",
        "webserial",
        "firmware flashing",
        "firmware parser",
        "device write",
    )

    for line in lowered.splitlines():
        if "implemented" not in line:
            continue
        if not any(target in line for target in targets):
            continue
        if any(marker in line for marker in deny_markers):
            continue
        fail(f"{label} contains potential positive implementation claim: {line.strip()}")


def validate_source_authority_doc(text: str) -> None:
    ensure_phrases(text, REQUIRED_SOURCE_DOC_PHRASES, label="source authority doc")
    ensure_headings(
        text,
        REQUIRED_HEADINGS["source"],
        label="source authority doc",
    )
    ensure_section_is_nonempty(text, "Unsupported Assumptions")
    ensure_section_is_nonempty(text, "Unknowns")
    ensure_no_positive_implementation_claims(text, "source authority doc")
    lowered = normalize(text)
    for path in REQUIRED_PERSISTENCE_REFERENCES:
        if path.lower() not in lowered:
            fail(f"source authority doc missing current persistence reference: {path}")


def validate_architecture_doc(text: str) -> None:
    ensure_phrases(text, REQUIRED_ARCH_DOC_PHRASES, label="architecture doc")
    ensure_headings(
        text,
        REQUIRED_HEADINGS["arch"],
        label="architecture doc",
    )
    ensure_section_is_nonempty(text, "Non-Claims")
    for phrase in REQUIRED_SECTION_ASSERTS:
        if phrase not in normalize(text):
            fail(f"architecture doc missing non-claim phrase: {phrase}")
    ensure_no_positive_implementation_claims(text, "architecture doc")


def main() -> int:
    print("glyph_runtime_config_storage_fallback")
    source_text = read_doc(SOURCE_AUTHORITY_DOC)
    architecture_text = read_doc(ARCHITECTURE_DOC)

    try:
        validate_source_authority_doc(source_text)
        validate_architecture_doc(architecture_text)
    except (RuntimeConfigStorageFallbackError, OSError, ValueError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print(f"source_auth_doc={SOURCE_AUTHORITY_DOC.relative_to(REPO_ROOT)}")
    print(f"architecture_doc={ARCHITECTURE_DOC.relative_to(REPO_ROOT)}")
    print("implementation_allowed_by_source_audit=false")
    print("device_write_claim=false")
    print("webserial_claim=false")
    print("firmware_flashing_claim=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
