# Glyph Native Ultimate Table Source Checker - 2026-05-26

Scope: read-only source-shape checker for guarding future native Ultimate table runtime work. This branch does not modify `src/modes/Ultimate.cpp` or require table runtime to exist.

## Checker

`tools/check_glyph_native_ultimate_table_runtime_scope.py` inspects `src/modes/Ultimate.cpp` and reports the current runtime scope.

It confirms:

- current Senscope Tilt patch markers still exist exactly once;
- no push/flashing terms exist in the checked runtime file;
- current Tilt/Tilt2 formulas remain byte-safe for direction components in `{-1, 0, 1}`;
- current absence or presence of native table-runtime markers;
- current `inputs.lt1 && !inputs.lt2` exclusivity;
- current `inputs.lt2 && !inputs.lt1` exclusivity;
- right-stick and trigger outputs are not assigned inside the current Tilt patch markers.

## Expected Current State

Current expected state before any table runtime patch:

- `tilt_patch_markers=present`
- `push_flashing_code_in_checked_files=absent`
- `tilt_tilt2_formulas_byte_safe=true`
- `table_runtime_markers=absent`
- `right_stick_or_trigger_assignments_inside_tilt_patch=false`

## Boundaries

- This checker does not approve a runtime patch.
- This checker does not inspect or change profile schema/configurator behavior.
- This checker does not validate hardware behavior.
- This checker does not change SOCD or remap semantics.
