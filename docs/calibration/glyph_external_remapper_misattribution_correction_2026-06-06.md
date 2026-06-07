# Glyph External Remapper Misattribution Correction - 2026-06-06

## Purpose and scope

This packet corrects a source-classification error in the Glyph
firmware/configurator/backend workstream.

The user clarified that they did not use or touch the custom external remapper
repo/app. The user-provided `GlyphUserProfilesDefault.json` and
`GlyphUserProfilesBackAndForth.json` files are official Glyph configurator app
artifacts.

They are official Glyph configurator app artifacts.

## Correct source classification

- `GlyphUserProfilesDefault.json` is the official Glyph configurator app default
  profiles JSON.
- `GlyphUserProfilesBackAndForth.json` is the custom profile after the user
  pushed it through and downloaded/exported it back to see what survived.
- These files must not be attributed to `https://lyseste.com/glyph-remapper/`
  or to the custom external remapper repository/app.
- The official configurator corpus is now the primary source for export-shape
  analysis.

## Quarantine rule

Any prior docs implying the user manually used
`https://lyseste.com/glyph-remapper/` or an external remapper import/export
experiment for these files are not valid user-provided evidence.

Existing external-remapper docs are quarantined as non-authoritative,
historical, and pending correction unless independently source-backed.
External-remapper evidence must not be used as primary corpus evidence.

## Corrected corpus

- Corpus: `official_glyph_configurator_2026-06-06`
- Manifest:
  `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- Structural diff fixture:
  `docs/calibration/fixtures/glyph_official_configurator_corpus_diff_2026-06-06.json`

## Explicit non-claims

- No external remapper source is promoted to authority.
- No external remapper user-execution evidence is claimed.
- No adapter output, WebSerial/device write, runtime-loaded config, protobuf
  binary write, firmware flashing automation, firmware behavior change, active
  profile artifact change, nunchuk validation, or gameplay semantic change is
  made here.
