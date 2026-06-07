# Glyph Current State

Status label: CURRENT.

This is the concise current-state entrypoint for the Glyph/HayBox-side
firmware, configurator, and backend realization workstream. Detailed evidence
packets remain under `docs/calibration/`.

## Firmware Baseline

- GFW3 runtime remap work is merged, user hardware-tested, and recorded in
  `docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md`.
- Preservation hardware pass is recorded for applicable non-nunchuk scope in
  `docs/calibration/glyph_ultimate_preservation_hardware_result.md`.
- Nunchuk remains NOT_TESTED / unvalidated / unavailable because the controller
  has no nunchuk port available out of the box.

## Official Configurator Corpus

- Official Glyph configurator corpus is present when
  `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
  exists.
- The manifest records two user-provided JSON fixtures: default profiles and a
  back-and-forth custom profile.
- The exact official configurator app version, exact capture timestamp, and
  exact push/download route details may remain unknown.
- External-remapper docs are quarantined unless independently source-backed.

## Current Readiness Categories

- Complete/current baseline: GFW3 runtime remap and applicable non-nunchuk
  preservation evidence are recorded for their stated scope.
- Ready for engineering design: generated-config/evaluator bridge work,
  generated C++ constants design/checker work, and offline export target
  contract design may proceed when scoped to docs/tools and source-backed
  artifacts.
- Ready for source research: transport/source-authority research, official
  configurator metadata capture, and external source audit planning may proceed
  when scoped and non-authoritative caveats remain intact.
- Waiting for user artifact: exact official configurator app version/source
  reference, exact capture timestamp, and exact push/download route metadata may
  be supplied if available, but the user is not currently blocking routine
  engineering design.
- Waiting for hardware artifacts: hardware tests are required only after a
  candidate or firmware artifact exists for that test scope. Nunchuk remains
  unvalidated for current hardware.
- Future phase requiring product approval before implementation:
  runtime-loaded config, WebSerial/device write, protobuf binary write,
  firmware flashing automation, generated firmware source changes, external
  adapter output, and Senscope neutral profile schema changes.
- Forbidden by policy: macros, turbo, timing automation, hidden device write,
  unsafe flashing automation, and external source reuse without license/source
  review.

The user is not currently blocking runtime-loaded config, WebSerial/device
write, generated constants, protobuf binary write, or exporter work as a domain
input matter. Those items are not implemented because they are future
engineering, source-research, or product phases.

Engineering design and source-research branches may proceed when prioritized
and scoped. Firmware behavior implementation, device-write implementation,
runtime-loaded config implementation, protobuf binary write, firmware flashing
automation, external adapter output, and schema changes still require explicit
product approval before source changes.

User domain input is required only for product/domain choices, not for routine
engineering decisions.

## Implementation State

- Runtime-loaded config is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
- External adapter output is not implemented.

## Non-Claims

- No nunchuk validation is claimed.
- No universal official configurator compatibility claim is made.
- No direct device write is implemented or claimed.
- No runtime-loaded config, WebSerial/device write, protobuf binary write,
  firmware flashing automation, or external-remapper adapter output is
  implemented.
- No Super Smash Bros. Ultimate game semantics are changed here.

## Practical Next Steps

- Continue Senscope neutral profile work outside this Glyph repo when that
  workflow is explicitly requested.
- Continue the generated-config/evaluator bridge inside this repo using
  source-backed firmware/controller evidence only.
- Use the generated C++ constants path as a ready engineering-design target, but
  stop before firmware source implementation until explicit product approval and
  source-backed review exist.
- Consider an offline official-configurator export candidate only after the
  profile format exists and the source-authority gates are satisfied.
