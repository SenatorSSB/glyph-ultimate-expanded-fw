# G13c Playtest Build Verification and UF2 Gate

Status: verification and read-only artifact gate for experimental playtest build path.

## Purpose

Define required checks before any human-controlled flash decision involving the `glyph_mk6_senscope_playtest` experimental build path.

This document does not authorize flashing.

## Required Checks Before Any Human Flash Consideration

1. Build normal `glyph_mk6`.
2. Build experimental `glyph_mk6_senscope_playtest`.
3. Inspect generated UF2 artifact(s) read-only.
4. Confirm generated candidate is app-only Update-style UF2.
5. Confirm generated candidate does not contain a Clean-style high-flash wipe segment.
6. Confirm official Update UF2 reference remains archived for comparison.
7. Confirm a documented recovery path exists before any spare-device action.

## Build Commands

Normal build:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

Experimental build:

```bash
./scripts/pio-local.sh run -e glyph_mk6_senscope_playtest
```

Optional quiet experimental wrapper:

```bash
./scripts/build-glyph-mk6-senscope-playtest-quiet.sh
```

## Read-Only UF2 Inspection Gate

Before any flash approval in a later branch:

- record generated UF2 path, size, and SHA-256;
- verify UF2 magic and family metadata;
- compare target ranges against archived official Update/Clean references;
- verify no unintended overlap with Clean-only high-flash wipe range;
- archive inspection output in docs for reviewer sign-off.

## Authorization Boundary

- This branch does not authorize flashing.
- This branch does not authorize upload commands.
- This branch does not authorize copy-to-device workflows.

## Next Branch Expectation

The next G12/G13 continuation branch should run read-only generated UF2 artifact inspection and document results before any human-controlled spare-device flash discussion.

