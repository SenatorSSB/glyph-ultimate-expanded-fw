# Glyph Next User Action Handoff - 2026-06-06

## Purpose and scope

This packet closes the GFW4 docs/tools supervisor sequence and identifies the
next meaningful actions that require the user, corpus artifacts, source
authority, domain input, or implementation approval.

Status: `next_user_action_required`.

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
| `glyph/gfw4-adapter-prewrite-blocker-matrix` | `b593ef9ca0b3` | Adapter/prewrite blocker matrix. |
| `glyph/gfw4-physical-logical-rf5-gap-index` | `19ff86c074e0` | Physical/logical/RF5 ambiguity gap index. |

The post-GFW3 baseline remains the current source-backed configurator baseline.
The GFW3 runtime remap result is user-reported pass for its stated scope.
Nunchuk hardware validation is not claimed.

## Remaining blocked items

| Item | Current state | Required next input |
| --- | --- | --- |
| Preservation hardware matrix | `blocked_pending_user_hardware_execution` | User execution of the preservation hardware matrix and a future result packet. |
| Export corpus capture | `blocked_missing_real_corpus_artifacts` | Real matched-version export corpus artifacts, manifest, hashes, and provenance. |
| Write-capable adapter / prewrite behavior | `adapter_prewrite_blocked` | Corpus, source authority, license/code-reuse review, transport/runtime decisions, and explicit implementation approval. |
| Physical/logical/RF5 ambiguity | `requires_source_authority_hardware_result_or_user_domain_input` | Source authority, user-reported hardware result, or explicit user/domain input if the historical RF5 row must be resolved. |
| Runtime-loaded config / WebSerial / device write / protobuf binary write / external adapter output | Forbidden without future approval | Source authority and explicit implementation approval before any branch may begin. |

## Exact next user-required actions

1. Execute the preservation hardware matrix and report per-row results, or decide
   to leave preservation blocked.
2. Provide real export corpus artifacts with a filled manifest, fixture hashes,
   and matched-version provenance, or leave export corpus capture blocked.
3. Provide source-authority approval before any write-capable adapter,
   runtime-loaded config, WebSerial/device write, protobuf binary write, or
   external adapter output work is considered.
4. Provide domain input or hardware/source evidence if the historical
   physical/logical/RF5 ambiguity must be resolved.
5. Provide explicit implementation approval before any firmware behavior change
   branch is started.

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
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result_TEMPLATE.json`
- `docs/calibration/glyph_export_corpus_readiness_status_2026-06-06.md`
- `docs/calibration/glyph_adapter_prewrite_blocker_matrix_2026-06-06.md`
- `docs/calibration/glyph_physical_logical_rf5_gap_index_2026-06-06.md`

## Stop boundary

The autonomous sequence stops here because the next meaningful work requires at
least one of: user hardware execution, user-provided corpus artifacts,
source-authority approval, explicit domain input, or explicit implementation
approval. No firmware implementation should start from this handoff alone.
