# Glyph Ultimate Identity Profile Baseline - 2026-05-27

## Scope

- Active Ultimate profile artifact and MVP fixture identity reset.
- No runtime behavior implementation in this branch.
- No schema/proto/configurator structural change.
- No firmware flashing automation.

## Identity Policy

- User-facing button IDs denote physical-position IDs.
- Matching physical/logical button IDs are the development baseline for this iteration.
- During active discovery, runtime owns custom behavior instead of semantic profile remap indirection.

## Files Changed

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`

## Identity Representation

Source convention in this profile JSON format represents identity mapping by omitting `activates`.

For this baseline reset, `MODE_ULTIMATE.buttonRemapping` uses identity entries with `physicalButton` only, preserving the existing physical-button list while removing semantic physical->logical remaps.

## Behavior Consequence

- Previous remap-layer Tilt1/Tilt2/Tilt3/D-pad behavior should not be assumed active after applying this identity artifact.
- Desired custom behavior must be implemented in runtime against the same-name logical fields in the next runtime branch.

If removing prior D-pad semantic remaps changes ordinary D-pad behavior in the current user-facing layout, that behavior must be restored through runtime implementation in the follow-up branch, not through reintroducing semantic profile remaps in this baseline branch.

## Historical Preservation

Previous LT3/Tilt3 and D-pad repair results remain valid historical evidence for their earlier artifact/runtime path, but they are not the design target for this identity-baseline development direction.

## Hardware Caveat

Do not apply this identity artifact expecting full Smash Box X/Y/Mode/LS->DPad behavior until the corresponding runtime implementation branch exists and is hardware-tested.

## 2026-05-28 Amendment

- `glyph/gfw2-identity-runtime-smashbox-modifiers` is the first runtime implementation branch that consumes this identity baseline directly.
- For active development, custom Smash Box behavior is now runtime-owned in `MODE_ULTIMATE` source and not profile-semantic-remap-owned.
- Hardware testing showed omitted-`activates` identity was not reliable for runtime/configurator behavior.
- Active development identity baseline now uses explicit self-activates identity where `physicalButton == activates`.
- Explicit self-activates remains identity behavior and is not semantic remapping.
