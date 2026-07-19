# Overlay/Preserve Proof — 2026-07-19

The proof input is
`docs/runtime_config/fixtures/generated_source_owned_layout_spec.json`.
The current source-owned baseline is 28 tables from
`src/modes/UltimateIdentityRuntimeTables.hpp`, resolved through
`src/modes/UltimateRuntimeConfigInterpreter.hpp`, with semantic digest
`9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970`.

Result: `SOURCE_AUTHORITY_BLOCKER`.

The input does not explicitly declare a generation mode or owned table set.
The two tables that happened to match the baseline in the historical
canonical-grid artifact are not ownership authority. No artifact was
generated, installed, or prepared for hardware. The complete manifest is
therefore intentionally `not_generated`; see the machine-readable report in
`fixtures/generated_source_owned_overlay_preserve_proof_2026-07-19.json`.

The next required decision is an explicit, source-authorized table ownership
set and replacement content. Until then there is no authorized active change
set and no hardware candidate.
