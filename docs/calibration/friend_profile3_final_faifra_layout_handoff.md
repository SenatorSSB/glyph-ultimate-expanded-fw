# Friend Profile3 Final Faifra Layout Handoff

Status: firmware candidate pending hardware retest.

Branch: `glyph/friend-fw-final-faifra-layout`

Base branch: `glyph/friend-fw-rf12-force-up-smash`

This is friend-specific firmware only. It must not be merged into
`configurator`.

## User Request Summary

- duplicate LT5 proper SOCD Up to RF6.
- swap LT2 AB with RF12 Up+A.
- move R from RF16 to LF8.
- make Ultimate first/default profile.
- Bump the one-shot marker so Faifra's existing saved LittleFS `config.bin`
  adopts the new baked default profile once.
- Stop treating the old physical/logical identity fixture as the exact target
  for this friend firmware.

## Source-Confirmed Previous Behavior

Inspected source:

- `config/glyph/common/include/glyph_overrides.hpp`
- `config/glyph/common/src/config.cpp`
- `src/modes/Ultimate.cpp`
- `include/modes/Ultimate.hpp`
- `docs/friend-profile3-wip.md`
- current friend handoff docs in `docs/calibration/`
- current friend check scripts in `tools/check_friend_*.py`

Previous behavior on the base branch:

- Ultimate was third in `default_config.game_mode_configs`, after Melee and
  Brawl.
- The baked Ultimate profile mapped physical `BTN_RF6` to logical `BTN_RF6`.
- `ResolveEffectiveDirections(...)` treated RF6 as auxiliary Up-like runtime
  input through `auxiliary_up_active = inputs.lf5 || inputs.rf6`.
- LT5 was the proper SOCD-governed Up source through the friend SOCD helper
  substituting `BTN_LT5` into the configured `BTN_LF5`/`BTN_LF2` `SOCD_2IP`
  pair.
- LT2 produced AB through `outputs.a = ... inputs.lt2 ...` and
  `outputs.b = ... inputs.lt2`.
- RF12 produced forced Up+A through `rf12_force_up_smash_active`.
- RF15 remained the X2 source.
- RF16 produced standalone R through `outputs.triggerRDigital`.
- MB7 produced Start through `outputs.start`.
- The one-shot marker was `/friend_profile3_default_applied.flag`.
- The old exact identity fixture checker still asserted full physical/logical
  identity against
  `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`.

## Final Behavior

- Ultimate is first/default profile in `default_config.game_mode_configs`.
- Physical LT5 still activates logical LT5.
- Physical RF6 now activates logical LT5 in the baked Ultimate profile, so RF6
  duplicates the proper LT5 SOCD-governed Up path through profile/default
  config.
- RF6 is no longer an auxiliary runtime Up-like bypass.
- LF5 remains auxiliary Up-like for modifier direction selection and yields to
  active Down.
- LT2 is forced Up+A / Up Smash: A is pressed and the left stick is forced to
  the Default-table Up point for the report frame.
- RF12 is AB: A and B are pressed simultaneously.
- RF12 is not Up+A and is not X2.
- RF15 remains X2.
- LF8 produces standalone R through the same `triggerRDigital` path RF16
  previously used.
- RF16 no longer produces R and does not produce Start.
- MB7 remains Start.
- X1/Y1, Tilt1, Tilt2/flipper, and Tilt3 source-owned behavior remains present.

No macro, turbo, timing automation, push-to-device workflow, flashing
automation, schema change, or vendor export was added.

## Profile-owned

- RF6 -> LT5 in the baked Ultimate `GameModeConfig`.
- Ultimate first/default profile ordering.
- The final friend layout intentionally deviates from the old physical/logical
  identity fixture.

## Runtime-owned

- LT2/RF12 AB and Up+A swap.
- LF8/RF16 R move using the existing R output path
  (`outputs.triggerRDigital`).
- RF6 removal from the auxiliary Up-like runtime path so profile remap owns the
  duplicate proper Up behavior.

## One-Shot Marker

The marker is version-bumped to:

```text
/friend_profile3_final_faifra_layout_applied.flag
```

The one-shot behavior is preserved. First boot on this branch writes the baked
compiled default config before the normal load path only when that marker is
absent. Later boots use the normal `persistence.LoadConfig(config)` path and do
not overwrite user edits every boot.

## Verification Scope

The final-layout checker is:

```bash
.venv/bin/python tools/check_friend_profile3_final_layout.py
```

It source-inspects the baked profile, one-shot marker, runtime role wiring, and
the historical identity-fixture retirement. The compatibility friend checkers
now point at this final layout contract instead of enforcing stale RF12/RF16/RF6
expectations.

## Hardware Retest Checklist

Hardware retest is required before claiming acceptance.

- Profile 3 adopts through the bumped one-shot overwrite path.
- Ultimate is the first/default profile after adoption.
- A/B normal buttons still work.
- L+R+A still works.
- RF6 behaves the same as LT5 for proper SOCD-governed Up.
- LT5 + Down follows source-owned `SOCD_2IP`.
- RF6 + Down follows the same source-owned `SOCD_2IP` behavior as LT5.
- LF5 + Down does not force Up over Down.
- LT2 alone produces A plus forced left-stick Up.
- LT2 + Down still produces forced Up plus A for the action.
- LT2 + left/right does not select left/right for the forced Up Smash action.
- RF12 produces AB.
- RF12 does not behave as Up+A.
- RF12 does not behave as X2.
- RF15 remains X2.
- LF8 produces standalone R.
- RF16 does not produce R.
- RF16 does not produce Start.
- MB7 produces Start.
- X1 + up/right displays `30 67`.
- Y1 + up/right displays `67 28`.
- X1+Y1 + up/right displays `30 28`.
- RF4/Tilt1 + up/right displays `59 39`.
- RF3/Tilt2/flipper + up/right displays `-59 40`.
- RF3/Tilt2/flipper + left/up displays `59 40`.
- RF4+RF3/Tilt3 + up/right displays `36 44`.

## Branch Boundary

This branch must not be merged into `configurator`, and it must not be used as
a configurator/profile/schema/export source.
