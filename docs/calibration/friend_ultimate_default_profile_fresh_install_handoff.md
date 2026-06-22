# Friend Ultimate Default Profile Fresh Install Handoff

Status: friend-specific/custom firmware branch handoff.

Base branch used: `friend-profile3-smashbox-import-wip`.

Implementation branch: `glyph/friend-fw-bake-correct-profile`.

Default profile fixture used:
`docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`.

Target C++ default config changed:
`config/glyph/common/include/glyph_overrides.hpp`.

## Scope

This branch preserves the existing friend/custom runtime firmware behavior and
only bakes the fixture's `MODE_ULTIMATE` profile data into the compiled default
config used by `glyph_default_config()`.

The changed `MODE_ULTIMATE` fields are:

- `name`
- `socdPairs`
- `buttonRemapping`
- `rgbConfig`
- `layoutPlate`
- `applicableBackends`
- `menuButtonIcon`

All non-Ultimate game modes are intentionally preserved.

## Adoption Requirement

Fresh Install / wipe profiles is required for the controller to adopt this
baked default profile.

Firmware setup starts with:

```cpp
Config config = glyph_default_config();
```

Then setup calls `persistence.LoadConfig(config)`. If loading fails, setup saves
the compiled default with `persistence.SaveConfig(config)`.

Therefore the baked default profile becomes active only when saved LittleFS
`config.bin` is missing, invalid, or wiped. Update / keep profiles will preserve
an existing valid `config.bin` and will not replace it with this baked default
profile.

## Safety Notes

- No flashing automation was added.
- No profile push/device-write automation was added.
- Persistence semantics were not changed.
- Protobuf schema was not changed.
- Existing friend/custom runtime firmware behavior was preserved.
- This branch must not be merged into `configurator`.

## Verification

Run:

```bash
.venv/bin/python tools/check_friend_ultimate_default_profile_matches_fixture.py
.venv/bin/python -m platformio run -e glyph_mk6
```
