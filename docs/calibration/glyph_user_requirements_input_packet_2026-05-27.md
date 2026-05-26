# Glyph User Requirements Input Packet - 2026-05-27

Purpose: fillable preimplementation packet required before the next runtime patch or hardware run.

Important: blank/unfilled fields are blockers, not defaults.

## Current Confirmed Facts (Pre-Filled Only)

- `RF3 -> logical LT1 -> Tilt1/TILT` for current Ultimate MVP mapping (`docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`).
- `RF4 -> logical LT2 -> Tilt2` for current Ultimate MVP mapping (`docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`).
- `RF5` printed/base location is now known from transcribed mapping, but old RF5 negative check remains `NOT_TESTED_AMBIGUOUS` (`docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`, `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md`).

## Required Input Sections

### Desired physical buttons and printed/base IDs

- [ ] completed
- target board/layout identifier: ____________________
- physical button IDs used: ____________________
- printed/base markings used: ____________________
- source of physical ID confirmation (doc/photo/user statement): ____________________

### Desired logical roles

- [ ] completed
- required logical roles list: ____________________
- logical role per physical ID: ____________________
- any roles intentionally unused: ____________________

### Desired modifier names visible to user

- [ ] completed
- modifier display names: ____________________
- modifier internal IDs (if any): ____________________
- naming constraints/caveats: ____________________

### Exact 9-way raw coordinate tables for each modifier, if any

- [ ] completed
- table state names: ____________________
- explicit `1..9` raw coordinates per state: ____________________
- evidence/source per table row: ____________________

### Neutral behavior

- [ ] completed
- required neutral coordinate(s): ____________________
- neutral conflict behavior, if multiple states apply: ____________________

### Both-held/chord behavior

- [ ] completed
- desired LT1+LT2 behavior: ____________________
- desired behavior for other chord/conflict combinations: ____________________
- explicit precedence/exclusivity rules: ____________________

### Conflict/exclusivity policy

- [ ] completed
- one-state-only vs multi-state composition policy: ____________________
- tie-break order (if needed): ____________________
- unacceptable conflict outcomes: ____________________

### Preservation expectations

- [ ] completed
- right-stick/C-stick preservation expectation: ____________________
- trigger preservation expectation: ____________________
- nunchuk overwrite preservation expectation: ____________________
- SOCD/remap preservation expectation: ____________________

### Test matrix owner and hardware readiness

- [ ] completed
- hardware test owner: ____________________
- target hardware availability date: ____________________
- required manual UF2 test environment readiness: ____________________
- rollback/backup readiness notes: ____________________

### Export/profile adapter expectations

- [ ] completed
- read-only diagnostics only vs future write-capable adapter expectation: ____________________
- required corpus source/version: ____________________
- allowed output formats (if any): ____________________

### Disabled-remap policy: omitted activates vs explicit BTN_UNSPECIFIED

- [ ] completed
- desired outbound representation policy: ____________________
- whether omission must be preserved verbatim: ____________________
- whether explicit `BTN_UNSPECIFIED` must be preserved verbatim: ____________________

## Blocker Rule

If any section remains blank or unresolved, runtime implementation and preservation claims remain blocked.
