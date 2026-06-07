# Glyph Next User Action Handoff - 2026-06-06

## Purpose and scope

This packet closes the GFW4 docs/tools supervisor sequence and identifies the
next meaningful actions that require user artifacts, product prioritization,
source authority, domain input for a specific ambiguity, official configurator
metadata, implementation approval, or hardware results after a test artifact
exists. It also records the
export corpus final blocker/status consolidation, which now records that the
official configurator corpus exists while write-capable implementation remains
blocked.

Status: `next_user_action_required_for_specific_artifacts_priorities_or_approval`.

This is docs/tools-only. It does not implement firmware behavior, change active
profile artifacts, record a hardware result, claim nunchuk validation, implement
runtime-loaded config, implement WebSerial/device write, or generate external
adapter output.

## Current configurator state

`configurator` now contains the following docs/tools-only packets from this
sequence:

| Branch | Commit | Packet |
| --- | --- | --- |
| `glyph/gfw4-preservation-hardware-readiness` | `12d13347d2ca` | Preservation hardware readiness packet. |
| `glyph/gfw4-preservation-result-template-hardening` | `695370cf1403` | Preservation result template/checker hardening. |
| `glyph/gfw4-export-corpus-readiness-status` | `0f5d488d6272` | Export corpus readiness/status packet. |
| `glyph/gfw5-export-corpus-final-blocker-status` | `26b4c5858ff8` | Export corpus final blocker/status packet. |
| `glyph/gfw4-adapter-prewrite-blocker-matrix` | `b593ef9ca0b3` | Adapter/prewrite blocker matrix. |
| `glyph/gfw5-adapter-prewrite-implementation-gate` | `cd41cfe16d1e` | Adapter prewrite implementation gate. |
| `glyph/gfw4-physical-logical-rf5-gap-index` | `19ff86c074e0` | Physical/logical/RF5 ambiguity gap index. |

The post-GFW3 baseline remains the current source-backed configurator baseline.
The GFW3 runtime remap result is user-reported pass for its stated scope.
The preservation hardware result is recorded for applicable non-nunchuk scope;
nunchuk remains NOT_TESTED / unvalidated / unavailable because the controller
has no nunchuk port available out of the box.
Nunchuk hardware validation is not claimed.
Export corpus final blocker/status consolidation records that export corpus
capture now has two user-provided official configurator JSON fixtures. Exact
configurator version/source reference, exact capture timestamp, and exact
push/download route details remain unknown.

## Current action categories

| Item | Current state | Required next input |
| --- | --- | --- |
| Export corpus metadata | `WAITING_FOR_USER_ARTIFACT` | Exact official configurator app version/source reference, exact capture timestamp, and exact push/download route details if available. This is optional metadata, not a general engineering blocker. |
| Engineering/source research prioritization | `READY_FOR_USER_PRODUCT_DECISION` | Choose/prioritize whether to start generated C++ constants path, export target contract, runtime-loaded config design, or transport source research. |
| Write-capable adapter / prewrite behavior | `READY_FOR_SOURCE_RESEARCH` / `READY_FOR_USER_PRODUCT_DECISION` | Official corpus exists; source authority for write behavior, license/code-reuse review, transport/runtime decisions, and explicit product approval remain required before implementation. |
| Physical/logical/RF5 ambiguity | `READY_FOR_SOURCE_RESEARCH` | Source authority, user-reported hardware result, or explicit user/domain input only if the historical RF5 row must be resolved. |
| Runtime-loaded config / WebSerial / device write / protobuf binary write / external adapter output | `FUTURE_PHASE` | Engineering design or source research may proceed when prioritized and scoped. Explicit product approval is required before implementation. |
| Hardware testing | `WAITING_FOR_HARDWARE_TEST` only after artifact exists | Provide hardware test results only after a firmware/candidate artifact exists for the stated test scope. |

## Exact next user-required actions

1. Provide exact official configurator app version/source reference and exact
   capture timestamp/route metadata if desired, or leave those metadata fields
   unknown.
2. Choose/prioritize whether to start generated C++ constants path, export target
   contract, runtime-loaded config design, or transport source research.
3. Provide product approval before any firmware behavior implementation,
   runtime-loaded config implementation, WebSerial/device write, protobuf binary
   write, external adapter output, firmware flashing automation, or schema
   change begins.
4. Provide domain input or hardware/source evidence only if the historical
   physical/logical/RF5 ambiguity must be resolved.
5. Provide hardware test results only after a test artifact exists.

Recommended future preservation result branch:
`glyph/gfw4-preservation-hardware-result`.

## Explicit non-claims

- No hardware result is recorded by this handoff.
- No preservation hardware pass/fail result is claimed here.
- No nunchuk hardware validation claim is made here.
- No firmware behavior change is made here.
- No active profile artifact change is made here.
- No runtime-loaded config is implemented here.
- No WebSerial/device write is implemented here.
- No protobuf binary write is implemented here.
- No firmware flashing automation is implemented here.
- No external remapper adapter output is generated here.
- No external source code is copied and no external dependency is added here.
- No official configurator compatibility claim is made here.
- No Super Smash Bros. Ultimate game semantics are changed here.

## Source inputs

- `docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md`
- `docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md`
- `docs/calibration/glyph_preservation_hardware_readiness_packet_2026-06-06.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_result.md`
- `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result.json`
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result_TEMPLATE.json`
- `docs/calibration/glyph_export_corpus_readiness_status_2026-06-06.md`
- `docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md`
- `docs/calibration/fixtures/glyph_export_corpus_final_blocker_status_2026-06-06.json`
- `tools/check_glyph_export_corpus_final_blocker_status.py`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- `tools/check_glyph_official_configurator_export_corpus.py`
- `docs/calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md`
- `tools/check_glyph_external_remapper_misattribution_correction.py`
- `docs/calibration/glyph_adapter_prewrite_blocker_matrix_2026-06-06.md`
- `docs/calibration/glyph_adapter_prewrite_implementation_gate_2026-06-06.md`
- `docs/calibration/fixtures/glyph_adapter_prewrite_implementation_gate_2026-06-06.json`
- `tools/check_glyph_adapter_prewrite_implementation_gate.py`
- `docs/calibration/glyph_physical_logical_rf5_gap_index_2026-06-06.md`

## Stop boundary

The autonomous docs/tools sequence stops here only for specific user artifacts,
prioritization choices, product approvals, domain ambiguity resolution, or
hardware results after a test artifact exists. Routine engineering design and
source research are not user-domain-blocked when scope is clear.

No firmware implementation should start from this handoff alone.
