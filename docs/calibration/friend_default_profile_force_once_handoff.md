# Friend Default Profile Force-Once Handoff

Status: friend-specific/custom firmware branch handoff.

Base branch: `glyph/friend-fw-bake-correct-profile`.
Implementation branch: `glyph/friend-fw-force-default-profile-once`.

This exists because the friend's old LittleFS config.bin survived flashing.
The previous friend firmware baked the intended compiled default profile, but
normal boot preserved a valid saved `config.bin`, so the baked default was not
adopted.

On first boot of this friend branch, firmware starts with
`glyph_default_config()`. Before the normal `persistence.LoadConfig(config)`
decision, it checks for `/friend_profile3_default_applied.flag`. If the marker
is absent, first boot overwrites saved config with baked compiled default by
calling `persistence.SaveConfig(config)` while `config` still contains the
compiled default. It then creates the marker file.

The marker prevents repeated overwrites. Future boots see the marker and use
the existing normal `persistence.LoadConfig(config)` path, so user edits made
after the first boot are not replaced on every boot.

Scope and boundaries:

- This is friend-branch only.
- This must not be merged to configurator.
- No USB/configurator/profile push automation was added.
- No flashing automation added.
- No Tilt/Tilt2 runtime formulas changed.
- No protobuf schema changed.
- No vendor export or device write workflow was added.

Source-backed behavior:

- `config/glyph/common/src/config.cpp` initializes `Config config` with
  `glyph_default_config()`.
- `config/glyph/common/src/config.cpp` runs the one-shot helper before
  `persistence.LoadConfig(config)`.
- `HAL/pico/src/core/Persistence.cpp` saves and loads the current protobuf
  `Config` through LittleFS `config.bin`.
