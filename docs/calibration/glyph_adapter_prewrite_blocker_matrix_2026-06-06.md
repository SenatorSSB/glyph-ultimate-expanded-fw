# Glyph Adapter Prewrite Blocker Matrix - 2026-06-06

## Purpose and scope

This packet consolidates the current write-capable adapter blockers before any
adapter output, device write, WebSerial, protobuf binary write, or
runtime-loaded config work can start.

Status: `write_capable_adapter_blocked_docs_tools_matrix`

This is docs/tools-only. It is a read-only blocker matrix, not an adapter
implementation and not a write path.

## Source inputs

The matrix is grounded in existing repository packets:

- Export corpus final blocker/status:
  `docs/calibration/glyph_export_corpus_final_blocker_status_2026-06-06.md`
- Configurator compatibility source registry:
  `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
- Offline remapper adapter blocker escalation:
  `docs/calibration/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.md`
- Offline remapper export loss gate:
  `docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md`
- WebSerial transport blocker packet:
  `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`
- Runtime storage/interpreter blocker packet:
  `docs/calibration/glyph_runtime_storage_interpreter_blocker_packet_2026-06-03.md`
- Protobuf config schema research packet:
  `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
- External remapper license/code-reuse blocker:
  `docs/calibration/glyph_external_remapper_license_code_reuse_blocker_2026-06-04.md`
- Roadmap next-work index:
  `docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md`

## Blocker matrix

| Blocker | Current status | Source-backed reason | Required future resolution |
| --- | --- | --- | --- |
| Official corpus present, metadata missing | `BLOCKED` | The final blocker/status packet records `official_configurator_corpus_present_initial`, `corpus_present=true`, and `completion_allowed=false`. | Provide exact configurator version/source reference and capture route metadata before broader compatibility claims. |
| Missing official configurator source authority | `BLOCKED` | The source registry keeps official configurator behavior and official packet/schema sources deferred. External observations are non-authoritative. | Source-authority approval and explicit source references for any official compatibility claim. |
| External observations non-authoritative | `BLOCKED` | External remapper observations are comparison inputs only and are not promoted to authority. | Source audit may record observations, but promotion requires explicit approval. |
| Runtime-owned behavior not safely represented in external JSON | `BLOCKED` | The export-loss gate records `runtime_owned_behavior_represented=false`. | Approved transform design plus sidecar/non-round-trip caveats; still not implementation by itself. |
| Active profile round-trip unsafe | `BLOCKED` | Binding loss and SOCD drift remain adapter-blocking; active profile round-trip is not safe. | New source-backed strategy, corpus evidence, and explicit approval before any active-profile adapter path. |
| WebSerial/device write blocked | `BLOCKED` | WebSerial transport and device write are not implemented and require source authority, user approval, rollback, and hardware planning. | Explicit user approval plus source-backed packet framing, safe dry-run/readback, rollback, and hardware test plan. |
| Runtime-loaded config blocked | `BLOCKED` | Runtime-loaded config, storage, and interpreter are not implemented and remain design/source-authority blocked. | Explicit user approval, design resolution, source authority, validator policy, and hardware plan. |
| Protobuf binary write blocked | `BLOCKED` | Official protobuf/schema authority is missing and protobuf binary generation is not implemented. | Official schema/source authority and explicit approval before binary generation or write behavior. |
| External source code reuse blocked | `BLOCKED` | License review is not completed, code reuse is not approved, no external code is copied, and no dependency is added. | License/source review and explicit user approval before reuse or dependency addition. |
| Adapter output generation blocked | `BLOCKED` | Adapter implementation and external-remapper-compatible JSON generation remain blocked. | Implementation approval after the above blockers are resolved and reviewed. |

## Allowed next work

Allowed next work is limited to docs/tools-only refinement:

- maintain this blocker matrix if upstream packet status changes;
- provide official configurator corpus metadata if available;
- perform a non-authoritative external source audit without copying code;
- refine clean-room design packets without generating adapter output;
- prepare user-facing handoff packets.

## Explicit non-claims

- No adapter output generation is made here.
- No external-remapper-compatible JSON generation is made here.
- No WebSerial or device write is implemented here.
- No Save to Device path is implemented here.
- No protobuf binary generation is implemented here.
- No runtime-loaded config is implemented here.
- No firmware behavior change is made here.
- No active profile artifact change is made here.
- No external source code is copied here.
- No external dependency is added here.
- No official configurator compatibility claim is made here.
- No hardware validation claim is made here.
- No nunchuk hardware validation claim is made here.
- No Senscope browser-app change is made here.

## Future branch policy

The next adapter-related implementation branch is blocked. A future branch may
only move beyond docs/tools if the user explicitly approves implementation after
source-authority, corpus, license, transport, runtime-loaded config, and
round-trip blockers are reviewed.
