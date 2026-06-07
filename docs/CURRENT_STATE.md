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

## Current Blockers

- Runtime-loaded config is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
- External adapter output is not implemented.
- External source reuse remains blocked pending source authority, license/code
  review, and explicit approval.
- Firmware behavior implementation is not approved by the current docs/tools
  scope.

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
- Use the generated C++ constants path as the next firmware-build-facing bridge
  only after explicit approval and source-backed review.
- Consider an offline official-configurator export candidate only after the
  profile format exists and the source-authority gates are satisfied.
