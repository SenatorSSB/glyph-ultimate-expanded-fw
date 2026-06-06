# Glyph Preservation Hardware Readiness Packet - 2026-06-06

## Purpose and scope

This packet prepares the existing Ultimate preservation hardware matrix for later
user execution. It is a docs/tools-only handoff packet. It does not record a
hardware result and it does not satisfy a behavior-changing merge gate.

Scope boundaries:

- This is docs/tools-only.
- This does not change firmware runtime behavior.
- This does not change active profile artifacts.
- This does not implement runtime-loaded config.
- This does not implement WebSerial write.
- This does not implement serial/device write behavior.
- This does not implement an external remapper adapter.
- This does not claim nunchuk hardware validation.
- This does not record a preservation hardware pass or fail result.

## Current post-GFW3 baseline

`configurator` has a post-GFW3 baseline packet. The GFW3 runtime remap result is
recorded as user-reported pass for its own scope only. That baseline keeps these
limits in force:

- Nunchuk hardware validation is not claimed.
- Runtime-loaded config is not implemented.
- WebSerial write is not implemented.
- Serial/device write behavior is not implemented.
- External remapper adapter implementation is not started.
- Active profile artifact change is not required.

The preservation hardware matrix remains blocked on user hardware execution.
This readiness packet only makes the future execution packet easier to run and
review.

## Source inputs

This packet references existing repo source authority and packet infrastructure:

- Existing preservation hardware matrix:
  `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
- Existing preservation result template:
  `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- Existing preservation result template fixture:
  `docs/calibration/fixtures/glyph_ultimate_preservation_hardware_result_TEMPLATE.json`
- Existing preservation result checker:
  `tools/check_glyph_ultimate_preservation_hardware_result.py`
- Identity runtime hardware validation and rollback plan:
  `docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md`
- Post-GFW3 baseline packet:
  `docs/calibration/glyph_post_gfw3_configurator_baseline_2026-06-06.md`
- Roadmap next-work index:
  `docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md`

## User-facing hardware execution summary

The next preservation hardware action is a user-run manual test, not an agent
inference step. The user should run the existing preservation matrix on actual
hardware, fill a result packet from the template, and record row-level statuses
and notes for every applicable row.

Required execution discipline:

- Record tested branch, tested commit SHA, firmware artifact path, firmware
  artifact SHA-256, profile/config, controller hardware identifier, flash method,
  and observation method.
- Use row statuses only from the allowed result set:
  `PASS`, `FAIL`, `NOT_TESTED`, `BLOCKED`, or `USER_ACCEPTED_RISK`.
- Treat `NOT_TESTED` rows as not validated.
- Do not infer untested rows from similar rows.
- Do not claim nunchuk validation unless nunchuk rows are actually executed and
  recorded.
- Do not claim external remapper, runtime-loaded config, WebSerial, device write,
  or active profile artifact changes from this preservation test.
- Record rollback notes if a failure requires rollback or user-accepted risk.

## Future result branch policy

Suggested future branch:

- `glyph/gfw4-preservation-hardware-result`

The result branch must record user-reported hardware data in a result doc, fixture, and checker.
The branch must be inspected before merge. The future
result packet must keep per-row statuses, `NOT_TESTED` handling, failure notes,
the user report source, and rollback notes if needed.

## Merge policy

This readiness branch may merge to `configurator` because it is docs/tools-only
and records no result. Readiness alone does not satisfy a behavior-changing
merge gate and does not mark preservation hardware complete.

## Explicit non-claims

- No firmware behavior change.
- No active profile artifact change.
- No runtime-loaded config.
- No WebSerial/device write.
- No external remapper adapter.
- No nunchuk hardware validation claim.
- No hardware pass/fail result recorded here.
