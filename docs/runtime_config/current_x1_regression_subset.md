# Current X1 regression subset

Status: current offline evidence correspondence for `GP-VAL-008`.

This lane binds the exact nine normalized-axis rows accepted for the existing
sole/non-mode X1 path. It checks current source structure and the extracted
`kX1Table` bytes against the immutable Revision-2 evidence record. It does not
simulate firmware, execute a controller, or create a new hardware result.

The abstract boundary is `mode_active=false`, `x1_active=true`, with every
other table modifier inactive and axes restricted to `-1`, `0`, and `1`.
Direction index is the current row-major mapping `((y + 1) * 3) + (x + 1)`.
The nine raw points are the exact offset-41 observations from
`GLYPH-UD-010`, `GLYPH-UD-011`, and `GLYPH-UD-012`.

The checker intentionally excludes the historical May-28 behavior fixture and
evaluator. It makes no claim about physical button binding, mode+X1/MX1,
other modifiers, gameplay, Nunchuk, root cause, firmware simulation, or a new
hardware test.
