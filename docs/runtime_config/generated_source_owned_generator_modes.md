# Source-owned generator modes

Status: complete as offline tooling; no production profile is authorized.

`tools/source_owned_generator_modes.py` is the reusable contract library and
`tools/generate_source_owned_generator_modes.py` is its thin JSON CLI. The
pipeline is strictly offline:

```text
validated profile -> authoritative baseline -> explicit ownership
-> complete 28-table artifact -> semantic manifest -> classification
-> optional preparation -> explicitly gated inert installation
```

The generator never edits `src/**`, builds firmware, flashes hardware, or
selects a runtime view. Installation is separate and atomic; dry-run reports
the exact intended output without mutation.

Generic file outputs are restricted to absolute, isolated system-temporary
paths and use the shared canonical-resolution, alias, symlink, overwrite, and
atomic-write policy. Standard output remains non-mutating. The only source
install exception is the exact inert
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp`
path; active baseline and all aliases remain rejected.

## Modes

* `full_replacement` requires all 28 tables. Missing or unknown tables fail;
  the baseline is used only for comparison. It produces `NO_OP` or
  `FULL_REPLACEMENT_CHANGESET`.
* `overlay_preserve` requires an explicit `owned_tables` list. Empty ownership
  is valid and produces a no-op. Every unowned table is copied from the current
  source-owned baseline, and any unowned input is rejected. It produces
  `NO_OP` or `EXPLICIT_OWNED_TABLE_CHANGESET`.
* `reject_partial` is validation-only. Partial input fails with a deterministic
  missing-table list; a complete input is rejected until an explicit
  full-replacement transition is selected.

Input schema is version 2; artifact schema is version 1; manifest and prepared
packet schemas are version 1. Legacy input without explicit ownership is
rejected as `SOURCE_AUTHORITY_BLOCKER`; no migration invents ownership.

## Authority and digests

The baseline is extracted from the current source-owned table source and is
identified by source paths, stable table order, count, and a SHA-256 semantic
digest. Digests use UTF-8 JSON with sorted keys, compact separators, and no
formatting or source-byte dependence. Per-table, complete-artifact, and
manifest digests are separate.

Provenance is explicit: `production_authorized`, `source_baseline_derived`,
`synthetic_test`, `example_only`, `migrated_legacy`, or `unknown`.
Production preparation/install accepts only authorized input. Baseline-derived
changes require separate authorization; baseline-derived no-ops are accepted
for equivalence proof but are not hardware candidates. Synthetic and example
fixtures remain test-only.

Every complete artifact has exactly 28 ordered manifest rows containing symbol,
action, ownership, provenance, baseline/candidate digests, changed state, and
reason. Manifest counts, row order, digests, and classification are verified
before preparation or installation.

## CLI and exit codes

```bash
python3 tools/generate_source_owned_generator_modes.py inspect-baseline
python3 tools/generate_source_owned_generator_modes.py validate-input INPUT.json
python3 tools/generate_source_owned_generator_modes.py generate INPUT.json
python3 tools/generate_source_owned_generator_modes.py generate-manifest INPUT.json
python3 tools/generate_source_owned_generator_modes.py classify INPUT.json --production
python3 tools/generate_source_owned_generator_modes.py prepare INPUT.json --production --output PACKET.json
python3 tools/generate_source_owned_generator_modes.py install PACKET.json /absolute/tmp/artifact.json --dry-run
```

Exit codes are 0 success, 2 invalid input, 3 source-authority/provenance
blocker, 4 baseline mismatch, 5 unsafe unowned change, 6 ineligible no-op,
7 I/O/integrity failure, and 8 invariant failure.

The fixture-backed matrix is `tools/check_glyph_source_owned_generator_modes.py`.
It covers all three modes, shape/ownership/provenance/baseline/manifest gates,
determinism, atomic dry-run/install behavior, legacy ambiguity, and the
canonical-default/unowned-table regression class. Fixtures are synthetic or
source-baseline-derived only; the current example layout remains
`SOURCE_AUTHORITY_BLOCKER` and is not a hardware candidate.

The prepared v2 packet can be rendered for review with
`tools/render_source_owned_cpp_preview.py`. This separate preview path
revalidates the packet and emits inactive C++ text only; it does not install,
mutate active source, create a candidate, or establish production authority.

## Boundary

No production hardware candidate was created. The failed canonical-grid
candidate remains unmerged, Alternative B remains hardware-passed only for its
source-aligned alias path, root cause remains unproven, and Nunchuk remains
`NOT_TESTED`. Runtime-loaded config, WebSerial/device write, persistence,
protobuf write, and flashing automation remain unimplemented.
