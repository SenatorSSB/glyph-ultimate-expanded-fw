# Glyph Post-GFW3 Configurator Baseline - 2026-06-06

## Purpose and scope

This packet records the post-merge `configurator` baseline after
`glyph/gfw3-runtime-remap-rework` was merged.

Scope boundaries:

- This is docs/tools-only.
- This does not change firmware runtime behavior.
- This does not change active profile artifacts.
- This does not implement runtime-loaded config.
- This does not implement WebSerial write.
- This does not implement serial/device write behavior.
- This does not implement an external remapper adapter.
- This does not claim nunchuk hardware validation.
- This does not touch Senscope browser app code.

## Baseline status

GFW3 runtime remap work is complete on `configurator` through post-merge
baseline inspection. The merged integration branch was
`glyph/gfw3-runtime-remap-rework`.

The GFW3 hardware result exists and is user-reported as "everything passing as expected".
That result is limited to GFW3 runtime remap behavior and is recorded in:

- `docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md`
- `docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.json`
- `tools/check_glyph_gfw3_runtime_remap_hardware_result.py`

## Explicit non-claims

- Nunchuk hardware validation was not claimed.
- Runtime-loaded config was not implemented.
- WebSerial write was not implemented.
- Serial/device write behavior was not implemented.
- External remapper adapter implementation was not started.
- External-remapper-compatible JSON generation was not implemented.
- Active profile artifact change was not required.
- No Senscope game-semantic source authority changed.

## Future behavior-changing workflow gate

Any next behavior-changing firmware work still needs its own branch, spec,
deterministic checker or fixture, firmware build, build artifact inspection,
hardware test plan, result recording after user hardware execution, post-result
inspection, rollback plan, and merge gate before merging back to `configurator`.

Runtime-loaded config, WebSerial/device write, protobuf binary write, firmware flashing automation, and external-remapper adapter output remain blocked unless future source authority and explicit approval exist.

## Expected baseline checks

The post-GFW3 baseline expects the GFW3 result checker, identity runtime
behavior evaluator, roadmap checker, next runtime readiness aggregate, forbidden
artifact checker, and `glyph_mk6` build/artifact inspection to pass before a
future behavior-changing branch treats `configurator` as clean.
