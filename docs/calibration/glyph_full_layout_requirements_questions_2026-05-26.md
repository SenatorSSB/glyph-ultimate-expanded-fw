# Glyph Full Layout Requirements Questions - 2026-05-26

Scope: open questions for filling the full layout requirements without inventing missing user/domain facts.

## User Input Required

- What is the final physical button role map for every physical control in the target layout?
- Which logical post-remap roles are required for the full profile beyond the current RF3/RF4 Tilt routing?
- What should RF5 be, physically and functionally, in the target layout?
- Which modifier states need native Ultimate table support?
- What are the exact raw coordinates for each required modifier state and direction `1..9`?
- What should happen when multiple modifier states are held together?
- Should any disabled/remapped buttons be encoded with omitted `activates`, explicit `BTN_UNSPECIFIED`, or another corpus-proven style?
- What profile/default backend behavior should be required after firmware updates?

## Source Research Required

- Confirm whether any source-backed native Ultimate table layer exists outside the currently inspected hard-coded `Ultimate.cpp` path.
- Confirm any additional source authority for `defaultModeConfig = 0` beyond validation acceptance.
- Confirm active MK6 nunchuk availability from source/build config if nunchuk requirements become relevant.

## Corpus Required

- Capture export corpus from the target configurator version before write-capable adapter work.
- Include fixtures covering omitted `activates`, explicit `BTN_UNSPECIFIED`, many-to-one aliases, duplicate physical entries, backend defaults, and applicable backend metadata.

## Hardware Required Later

- Re-run Tilt1/Tilt2 preservation after any future runtime patch.
- Complete C-stick/right-stick preservation checks.
- Complete trigger preservation checks.
- Resolve RF5 physical identity.
- Complete SOCD/opposite-direction preservation checks.
- Verify profile/default behavior where possible.
