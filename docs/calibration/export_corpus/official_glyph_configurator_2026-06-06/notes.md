# Official Glyph Configurator Export Corpus - 2026-06-06

## Source classification

This corpus consists of two official Glyph configurator app JSON files that the
user provided for the Glyph firmware/configurator/backend workstream.

These files must not be attributed to the external remapper. The user clarified
that they did not use or touch the custom external remapper repo/app for these
files.

## Fixture roles

- `glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
  is the official app default profiles JSON.
- `glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`
  is the custom profile pushed through and downloaded/exported back.

## Evidence role

This corpus is primary evidence for official configurator JSON export shape in
the current workflow.

The exact official configurator app version/source reference and exact capture
timestamp are unknown unless the user provides them later. The exact
push/download route details are also not fully recorded in this repo beyond the
user clarification above.

## Non-claims

This corpus does not itself implement adapter generation or device write. It
does not implement WebSerial/device write, runtime-loaded config, protobuf
binary write, firmware flashing automation, firmware behavior changes, active
profile artifact changes, nunchuk validation, or universal official
compatibility.
