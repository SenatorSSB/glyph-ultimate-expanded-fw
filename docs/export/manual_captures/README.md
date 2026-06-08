# Official Configurator Manual Capture Directory

Status: `PLAN_ONLY_DIRECTORY_INDEX`

This directory contains operator-facing guidance and templates only.

No official configurator manual capture has been executed in this branch.
No capture artifacts are recorded here yet.

## Files Here

- `.gitkeep` — preserves this directory in git until captures are added.

Future capture folders must use:

`YYYYMMDD_official_configurator_<app-version-or-unknown>/`

Each future folder must contain `input_candidate.json`, `metadata.json`,
`hashes.txt`, and either `output_export.json` or `rejection_note.md`.

Related operator docs live in `docs/export/`:

- `official_configurator_manual_capture_instructions.md` — operator workflow
  template for a future manual import/export run.
- `official_configurator_manual_capture_artifact_layout.md` — canonical
  artifact naming and directory structure for future results.

Captured metadata template lives in `docs/export/fixtures/`:

- `official_configurator_manual_capture_metadata_TEMPLATE.json`

## Baseline Caveat

Before creating any future capture records, verify the baseline artifacts listed
in the layout document are present. If any expected baseline artifact is absent,
record that precondition as blocked and do not continue with operator capture.

## Explicit Non-Claims

- no capture performed in this packet
- no result recorded in this packet
- no production export
- no official configurator compatibility claim
- no device-write, no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no hardware behavior validation
- no nunchuk validation
