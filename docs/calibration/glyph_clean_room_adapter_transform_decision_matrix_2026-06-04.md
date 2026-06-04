# Glyph Clean-Room Adapter Transform Decision Matrix - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only decision and blocker matrix for a
possible future clean-room adapter transform.

Matrix status is `decision_matrix_only_implementation_blocked`.

All decisions are unresolved or blocked.

No implementation decision is approved.

`implementation_decisions_approved=false`

`adapter_implementation_allowed=false`

External JSON generation is not allowed.

No adapter implementation is added.

No transform code is added.

No runtime source is changed.

No active profile artifact is changed.

No exported experiment artifact is changed.

No runtime-loaded config is implemented.

No serial/device write behavior is implemented.

No WebSerial transport is implemented.

No protobuf binary generation is implemented.

No official configurator compatibility is claimed.

No hardware validation is claimed.

No external source is promoted to authority.

No external code is copied and no dependency is added.

Hardware status remains `not_new_hardware_result`.

## Source artifacts

Decision matrix fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_transform_decision_matrix_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_transform_decision_matrix.py`

Source packet references:

- `docs/calibration/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.md`
- `docs/calibration/glyph_offline_remapper_export_loss_gate_2026-06-04.md`
- `docs/calibration/glyph_clean_room_adapter_transform_design_contract_2026-06-04.md`
- `docs/calibration/glyph_clean_room_adapter_transform_rule_matrix_2026-06-04.md`
- `docs/calibration/glyph_storage_transport_research_index_2026-06-03.md`

These source packet references are evidence anchors only. They do not approve
implementation.

## Required decisions

| Decision | Current status | Blocker |
| --- | --- | --- |
| whether the adapter target is import-only, not round-trip | `unresolved` | Active profile round-trip is unsafe through the external remapper export, so target direction must be explicitly decided before implementation. |
| whether the external remapper is allowed to be used as a visual editor | `unresolved` | The external remapper export is not canonical for the active identity-runtime profile, so visual-editor use must be bounded before implementation. |
| whether runtime-owned behavior is represented only in sidecar | `blocked` | Runtime-owned behavior is not represented by external profile JSON in the current checked packets. |
| whether SOCD policy should remain sidecar-only or become a profile-level candidate | `unresolved` | SOCD drift is adapter-blocking and the transform rule matrix currently keeps SOCD policy sidecar-only. |
| whether activates-bearing bindings can ever be regenerated | `blocked` | Exported profile JSON stripped activates-bearing bindings, and active profile round-trip is unsafe. |
| whether official configurator compatibility is in scope | `blocked` | No official configurator compatibility claim is made by the current packets. |
| whether protobuf/device-write remains fully out of scope | `blocked` | Protobuf binary generation, WebSerial transport, serial/device write behavior, and runtime-loaded config remain unimplemented and blocked. |
| whether a repeated no-device experiment is required with browser/version recorded | `unresolved` | Prior packets list repeated no-device experiment evidence with browser/version recorded as required future evidence. |
| whether source audit is required before implementation | `blocked` | External source is not promoted to authority and transform rules remain planning-only. |
| whether license review is required before any code reuse | `blocked` | No external code has been copied and no external dependency has been added. |
| whether user approval is required before implementation | `blocked` | Adapter implementation, transform implementation, and external JSON generation are not approved. |

## Implementation gate

Transform implementation remains blocked until every required decision has a
reviewed answer, required source evidence is available, license review is
complete for any code reuse, and explicit user approval is recorded.

This packet does not decide that an adapter target is import-only.

This packet does not decide that the external remapper is a safe visual editor.

This packet does not decide that runtime-owned behavior may be represented in a
profile-level external JSON field.

This packet does not decide that SOCD policy is a profile-level candidate.

This packet does not decide that activates-bearing bindings can be regenerated.

This packet does not decide official configurator compatibility scope.

This packet does not open protobuf/device-write scope.

This packet does not record a repeated no-device experiment.

This packet does not complete source audit.

This packet does not complete license review.

This packet does not record user approval for implementation.

## Checker output

`tools/check_glyph_clean_room_adapter_transform_decision_matrix.py` prints:

- `glyph_clean_room_adapter_transform_decision_matrix`
- `status=PASS` or `status=FAIL`
- `implementation_decisions_approved=false`
- `adapter_implementation_allowed=false`
- `hardware_status=not_new_hardware_result`
