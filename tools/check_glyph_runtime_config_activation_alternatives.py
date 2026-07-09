#!/usr/bin/env python3
"""Validate the runtime-config activation alternatives A-F claim invariants."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs/runtime_config/runtime_config_activation_alternatives_a_f.md"

REQUIRED_PHRASES = (
    "design / docs-checker only",
    "compares six activation alternatives",
    "currently hardware-passed",
    "hardware-passed for the generated-table alias candidate preserving the active publication path",
    "explicitly forbidden under current evidence",
    "future architecture only",
    "claim invariants",
    "current lane is blocked before active behavior until a selected activation strategy is implemented and hardware-gated",
    "candidate.view",
    "active_storage.view",
    "tools/check_glyph_source_owned_table_symbol_map.py",
    "runtime-loaded profile or config interpreter",
    "runtime-loaded config",
    "webserial/device write",
    "not implemented",
    "not approved",
)

REQUIRED_SECTION_HEADINGS = (
    "Purpose",
    "Current Baseline",
    "Claim Invariants",
    "Alternatives",
    "Comparison Summary",
    "Non-Claims",
    "Stop Line",
)

REQUIRED_ALTERNATIVES = (
    "### A. Source-Owned Table-Content Replacement Through The Current Baseline Tables",
    "### B. Source-Owned Generated Table File Replacing Or Aliasing The Baseline Tables",
    "### C. Generated `RuntimeConfigView` Wrapper Activation",
    "### D. Activate Through `candidate.view`",
    "### E. Activate Through `active_storage.view` Or RAM-Backed Active Table Storage",
    "### F. Runtime-Loaded Profile Or Config Interpreter",
)

FORBIDDEN_POSITIVE_PATTERNS = (
    r"\bgenerated artifact is active\b",
    r"\bgenerated wrapper is safe\b",
    r"\bgenerated runtimeconfigview wrapper safe\b",
    r"\bgenerated runtimeconfigview wrapper is safe\b",
    r"\bruntime-loaded config is implemented\b",
    r"\bwebserial/device write is implemented\b",
    r"\bdevice write is implemented\b",
    r"\bflashing automation is implemented\b",
    r"\bcandidate\.view active publication is approved\b",
    r"\bactive_storage\.view active publication is approved\b",
    r"\bram-backed active table publication is approved\b",
    r"\bnunchuk validation is claimed\b",
    r"\bunrecorded hardware validation is claimed\b",
)


class ActivationAlternativesError(ValueError):
    """Raised when claim invariants around the activation alternatives drift."""


def fail(message: str) -> None:
    raise ActivationAlternativesError(message)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("`", ""))


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required doc: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def ensure_headings(text: str, headings: tuple[str, ...]) -> None:
    lowered = text.lower()
    for heading in headings:
        if f"## {heading}".lower() not in lowered:
            fail(f"missing required section heading: {heading}")


def ensure_alternatives(text: str) -> None:
    for alt in REQUIRED_ALTERNATIVES:
        if alt.lower() not in text.lower():
            fail(f"missing required alternative heading: {alt}")


def ensure_no_positive_claims(text: str) -> None:
    lowered = normalize(text)
    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        if re.search(pattern, lowered):
            fail(f"doc contains forbidden positive claim matching: {pattern}")


def ensure_claim_invariants(text: str) -> None:
    lowered = normalize(text)
    required_phrases = (
        "every claim in this note must satisfy",
        "source-backed means the claim is supported by repo source, repo docs, repo tests, fixtures, or an explicit user/domain statement",
        "inferred means the claim is a reasoned interpretation",
        "unknown means the repo does not currently support the claim",
        "no claim in this note may silently upgrade a design alternative into an implementation decision",
        "no alternative here is approval to implement any runtime path",
    )
    for phrase in required_phrases:
        if phrase not in lowered:
            fail(f"missing claim invariant phrase: {phrase}")


def ensure_non_claims(text: str) -> None:
    lowered = normalize(text)
    required_non_claims = (
        "this note does not implement runtime-loaded config",
        "this note does not implement storage",
        "this note does not implement webserial/device write",
        "this note does not implement flashing automation",
        "this note does not change firmware runtime behavior",
        "this note does not claim unrecorded hardware validation",
        "this note does not claim nunchuk validation",
        "this note does not approve candidate.view active publication",
        "this note does not approve active_storage.view active publication",
        "this note does not approve ram-backed active table publication",
        "this note does not approve generated runtimeconfigview wrapper activation",
    )
    for phrase in required_non_claims:
        if phrase not in lowered:
            fail(f"missing non-claim phrase: {phrase}")


def ensure_alt_b_source_shape(text: str) -> None:
    lowered = normalize(text)
    required_b_shape = (
        "concrete source-change shape",
        "replace or alias the compile-time contents of src/modes/ultimateidentityruntimetables.hpp before firmware build",
        "keep getactiveruntimeconfigstate()",
        "resolveactiveruntimeconfig()",
        "ksourceownedcurrentbaselineruntimeconfig unchanged at publication time",
        "ee5fd35c4ce00e31d9a00905c771699ad17517b9",
    )
    for phrase in required_b_shape:
        if phrase not in lowered:
            fail(f"missing alternative B source-shape phrase: {phrase}")


def main() -> int:
    print("glyph_runtime_config_activation_alternatives")
    try:
        text = read_required(DOC_PATH)
        ensure_headings(
            text,
            (
                "Purpose",
                "Current Baseline",
                "Claim Invariants",
                "Alternatives",
                "Comparison Summary",
                "Checker Gates",
                "Non-Claims",
                "Stop Line",
            ),
        )
        ensure_alternatives(text)
        ensure_claim_invariants(text)
        ensure_non_claims(text)
        ensure_alt_b_source_shape(text)
        ensure_no_positive_claims(text)
    except (OSError, ValueError, ActivationAlternativesError) as exc:
        print("status=FAIL")
        print(f"error={exc}")
        return 1

    print("status=PASS")
    print("claim_invariants_hardened=true")
    print("alternatives_covered=A-F")
    print("runtime_loaded_config_implemented=false")
    print("webserial_device_write_implemented=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
