#!/usr/bin/env python3
"""Report and validate the source-owned table symbol-map boundary for Alternative B."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ULTIMATE_CPP = REPO_ROOT / "src/modes/Ultimate.cpp"
INTERPRETER_HPP = REPO_ROOT / "src/modes/UltimateRuntimeConfigInterpreter.hpp"
TABLES_HPP = REPO_ROOT / "src/modes/UltimateIdentityRuntimeTables.hpp"
GENERATED_BASELINE_HPP = (
    REPO_ROOT
    / "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
)

DESIGN_NOTE = REPO_ROOT / "docs/runtime_config/source_owned_table_symbol_map.md"
RUNTIME_README = REPO_ROOT / "docs/runtime_config/README.md"
IMPLEMENTATION_BOUNDARY = REPO_ROOT / "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md"
ACTIVATION_ALTERNATIVES = REPO_ROOT / "docs/runtime_config/runtime_config_activation_alternatives_a_f.md"
CURRENT_STATE = REPO_ROOT / "docs/CURRENT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
SOURCE_OWNED_REALIZATION = REPO_ROOT / "docs/runtime_config/generated_source_owned_realization_design.md"
GENERATOR_CONTRACT = REPO_ROOT / "docs/runtime_config/generated_source_owned_generator_contract.md"
LAYOUT_SPEC = REPO_ROOT / "docs/runtime_config/generated_source_owned_layout_spec.md"
ARTIFACT_INSTALL = REPO_ROOT / "docs/runtime_config/generated_source_owned_artifact_install.md"
BASELINE_ARTIFACT = REPO_ROOT / "docs/runtime_config/generated_source_owned_baseline_artifact.md"
SOURCE_OWNED_REPLACEMENT = REPO_ROOT / "docs/runtime_config/source_owned_table_replacement_design.md"

CHECKED_DOCS = (
    DESIGN_NOTE,
    RUNTIME_README,
    IMPLEMENTATION_BOUNDARY,
    ACTIVATION_ALTERNATIVES,
    CURRENT_STATE,
    ROADMAP,
    SOURCE_OWNED_REALIZATION,
    GENERATOR_CONTRACT,
    LAYOUT_SPEC,
    ARTIFACT_INSTALL,
    BASELINE_ARTIFACT,
    SOURCE_OWNED_REPLACEMENT,
)

FORBIDDEN_DOC_PATTERNS = (
    re.compile(r"\bruntime-loaded config is implemented\b", re.IGNORECASE),
    re.compile(r"\bpersistent storage is implemented\b", re.IGNORECASE),
    re.compile(r"\bwebserial/device write is implemented\b", re.IGNORECASE),
    re.compile(r"\bdevice write is implemented\b", re.IGNORECASE),
    re.compile(r"\bbackend/config\.pb write path is implemented\b", re.IGNORECASE),
    re.compile(r"\bflashing automation is implemented\b", re.IGNORECASE),
    re.compile(r"\bcandidate\.view active publication is approved\b", re.IGNORECASE),
    re.compile(r"\bactive_storage\.view active publication is approved\b", re.IGNORECASE),
    re.compile(r"\bgenerated runtimeconfigview wrapper is selected active\b", re.IGNORECASE),
    re.compile(r"\bgenerated active runtimeconfigview wrapper is selected active\b", re.IGNORECASE),
    re.compile(r"\bruntimeconfigview replacement becomes the customization mechanism\b", re.IGNORECASE),
    re.compile(r"\bruntimeconfigview replacement is the customization mechanism\b", re.IGNORECASE),
)


class SourceOwnedTableSymbolMapError(AssertionError):
    """Raised when the source-owned table symbol map drifts."""


def fail(message: str) -> None:
    raise SourceOwnedTableSymbolMapError(message)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing required path: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def line_lookup(path: Path, needle: str) -> tuple[int, str]:
    lines = read_required(path).splitlines()
    for index, line in enumerate(lines, start=1):
        if needle in line:
            return index, line.strip()
    fail(f"missing required source symbol in {path.relative_to(REPO_ROOT)}: {needle}")


def block_lookup(path: Path, signature: str, required_fragments: tuple[str, ...]) -> tuple[int, int, list[str]]:
    lines = read_required(path).splitlines()
    for start_index, line in enumerate(lines):
        if signature not in line:
            continue
        brace_depth = 0
        seen_open = False
        collected: list[str] = []
        for index in range(start_index, len(lines)):
            current = lines[index]
            collected.append(current.rstrip())
            brace_depth += current.count("{")
            if current.count("{"):
                seen_open = True
            brace_depth -= current.count("}")
            if seen_open and brace_depth == 0:
                body_text = "\n".join(collected)
                for fragment in required_fragments:
                    if fragment not in body_text:
                        fail(
                            f"{path.relative_to(REPO_ROOT)} function block missing required fragment: {fragment}"
                        )
                return start_index + 1, index + 1, collected
    fail(f"missing required function block in {path.relative_to(REPO_ROOT)}: {signature}")


def ensure_doc_is_safe(path: Path) -> None:
    text = read_required(path)
    for pattern in FORBIDDEN_DOC_PATTERNS:
        if pattern.search(text):
            fail(
                f"{path.relative_to(REPO_ROOT)} contains a forbidden positive implementation claim: "
                f"{pattern.pattern}"
            )


def main() -> int:
    print("glyph_source_owned_table_symbol_map: PASS")

    active_start, active_end, active_block = block_lookup(
        ULTIMATE_CPP,
        "const ActiveRuntimeConfigState& GetActiveRuntimeConfigState()",
        ("&kSourceOwnedCurrentBaselineRuntimeConfig",),
    )
    resolve_start, resolve_end, resolve_block = block_lookup(
        ULTIMATE_CPP,
        "const RuntimeConfigView& ResolveActiveRuntimeConfig()",
        ("return *GetActiveRuntimeConfigState().active_view;",),
    )
    active_pointer_line, active_pointer_text = line_lookup(
        ULTIMATE_CPP,
        "&kSourceOwnedCurrentBaselineRuntimeConfig,",
    )
    resolve_line, resolve_text = line_lookup(
        ULTIMATE_CPP,
        "return *GetActiveRuntimeConfigState().active_view;",
    )

    if "candidate.view" in "\n".join(active_block):
        fail("GetActiveRuntimeConfigState() must not publish candidate.view")
    if "active_storage.view" in "\n".join(active_block):
        fail("GetActiveRuntimeConfigState() must not publish active_storage.view")
    if "candidate.view" in "\n".join(resolve_block):
        fail("ResolveActiveRuntimeConfig() must not dereference candidate.view")
    if "active_storage.view" in "\n".join(resolve_block):
        fail("ResolveActiveRuntimeConfig() must not dereference active_storage.view")

    baseline_tables_line, baseline_tables_text = line_lookup(
        INTERPRETER_HPP,
        "constexpr RuntimeTableView kSourceOwnedCurrentBaselineRuntimeTables[kRuntimeTableCount] = {",
    )
    known_good_line, known_good_text = line_lookup(
        INTERPRETER_HPP,
        "constexpr RuntimeConfigView kKnownGoodRuntimeConfig = {",
    )
    baseline_config_line, baseline_config_text = line_lookup(
        INTERPRETER_HPP,
        "constexpr RuntimeConfigView kSourceOwnedCurrentBaselineRuntimeConfig = kKnownGoodRuntimeConfig;",
    )

    include_line, include_text = line_lookup(
        ULTIMATE_CPP,
        '#include "modes/UltimateIdentityRuntimeTables.hpp"',
    )
    generated_include_line, generated_include_text = line_lookup(
        TABLES_HPP,
        '#include "runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"',
    )
    tables_header_line, tables_header_text = line_lookup(
        TABLES_HPP,
        "SOURCE_OWNED_GENERATED_TABLE(kDefaultTable, 0);",
    )

    ultimate_text = read_required(ULTIMATE_CPP)
    interpreter_text = read_required(INTERPRETER_HPP)
    forbidden_source_tokens = (
        "GeneratedRuntimeConfigBaselineActiveView",
        "GeneratedRuntimeConfigView",
        "RuntimeConfigView replacement",
        "RAM-backed active table publication",
    )
    for token in forbidden_source_tokens:
        if token in ultimate_text or token in interpreter_text:
            fail(f"forbidden active-publication token present in source path: {token}")

    print("- active pointer publication:")
    print(
        f"  {ULTIMATE_CPP.relative_to(REPO_ROOT)}:{active_start}-{active_end} "
        f"(pointer line {active_pointer_line}) {active_pointer_text}"
    )
    print("- active runtime resolution:")
    print(
        f"  {ULTIMATE_CPP.relative_to(REPO_ROOT)}:{resolve_start}-{resolve_end} "
        f"(deref line {resolve_line}) {resolve_text}"
    )
    print("- baseline source symbols:")
    print(f"  {INTERPRETER_HPP.relative_to(REPO_ROOT)}:{baseline_tables_line} {baseline_tables_text}")
    print(f"  {INTERPRETER_HPP.relative_to(REPO_ROOT)}:{known_good_line} {known_good_text}")
    print(f"  {INTERPRETER_HPP.relative_to(REPO_ROOT)}:{baseline_config_line} {baseline_config_text}")
    print("- current source-owned table include/alias boundary:")
    print(f"  {ULTIMATE_CPP.relative_to(REPO_ROOT)}:{include_line} {include_text}")
    print(f"  {TABLES_HPP.relative_to(REPO_ROOT)}:{generated_include_line} {generated_include_text}")
    print(f"  {TABLES_HPP.relative_to(REPO_ROOT)}:{tables_header_line} {tables_header_text}")

    inert_artifacts = (
        "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp",
        "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp",
        "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigExample.hpp",
        "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigSchema.hpp",
        "docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp",
        "docs/runtime_config/fixtures/generated_source_owned_realization_design.json",
        "docs/runtime_config/fixtures/generated_source_owned_schema_scaffold.json",
        "docs/runtime_config/fixtures/generated_source_owned_generator_contract.json",
        "docs/runtime_config/fixtures/generated_source_owned_layout_spec.json",
        "docs/runtime_config/fixtures/generated_source_owned_layout_spec.example.json",
        "docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json",
        "docs/runtime_config/fixtures/generated_source_owned_artifact_install.json",
        "docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json",
    )
    print("- generated-source-owned inert artifact paths:")
    for path in inert_artifacts:
        print(f"  {path}")

    alternative_b_touchpoints = (
        "src/modes/UltimateIdentityRuntimeTables.hpp -> replace or alias the compile-time table contents",
        "src/modes/UltimateRuntimeConfigInterpreter.hpp -> preserve kSourceOwnedCurrentBaselineRuntimeTables, kKnownGoodRuntimeConfig, and kSourceOwnedCurrentBaselineRuntimeConfig",
        "src/modes/Ultimate.cpp -> keep GetActiveRuntimeConfigState() and ResolveActiveRuntimeConfig() on the stable source-owned publication path",
        "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp -> inert baseline artifact stays non-active",
    )
    print("- Alternative B candidate touchpoints:")
    for touchpoint in alternative_b_touchpoints:
        print(f"  {touchpoint}")

    print("- checked docs:")
    for path in CHECKED_DOCS:
        ensure_doc_is_safe(path)
        print(f"  {path.relative_to(REPO_ROOT)}")

    print("status=PASS")
    print("active_publication=GetActiveRuntimeConfigState()->&kSourceOwnedCurrentBaselineRuntimeConfig")
    print("active_resolution=ResolveActiveRuntimeConfig()->*GetActiveRuntimeConfigState().active_view")
    print("baseline_tables_symbol=kSourceOwnedCurrentBaselineRuntimeTables")
    print("baseline_config_symbol=kSourceOwnedCurrentBaselineRuntimeConfig")
    print("known_good_symbol=kKnownGoodRuntimeConfig")
    print("table_include_path=src/modes/UltimateIdentityRuntimeTables.hpp")
    print("alternative_b_boundary=source_owned_table_content_replacement_before_build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
