# Using Glyph — current guide

This is a barebones guide during public beta/release preparation, not a finished
release/install workflow. Start with [capabilities](CAPABILITIES.md) and
[current qualification](CURRENT_STATE.md).

## Design a profile

You can author finite native Ultimate coordinate tables, conditions, direction
sources, digital bindings and analogue effects. A direction entry may output any
valid raw coordinate, including a non-center output for no-direction key 5.
Coordinated input roles and layers are deterministic mappings, not macros or game
semantics. There is no automatic character-facing awareness.

Read [Profile System](PROFILE_SYSTEM.md) for advanced design and evaluator
semantics. Start authoring at [native Ultimate authoring v1](../profiles/README.md). Its synthetic
examples and validate/compile/report commands are offline; they open no device.
Keep the human JSON: decoding wire bytes does not recover authored names or intent.
The old v0 golden is archival, not the template for a new profile.

## Row, native profile and package

- A **profile row** is a `GameModeConfig` entry, including remaps, SOCD, plate,
  activation/backend applicability and references.
- A **native profile** is the stored Ultimate evaluator data. Compiling it alone
  does not create an installed complete package.
- A **complete managed package** owns one dedicated Ultimate row and one dedicated
  ProfileStore record, plus package metadata and RGB. Manage it as one logical
  profile, rather than sharing its backing objects.

The maximum is **30 profile rows total**, a shared 30-row budget including retained
stock/other modes. ProfileStore's record limit is a separate constraint; it does
not add rows. Profile-owned mappings coexist with device-global backend
configuration, brightness and some mode options.

## Selection, installation and recovery

Current activation is boot-bound, not arbitrary live hot-swap. Existing character
menu work and saved-reference management are distinct from a finished ordinary
backend-filtered managed-package selection workflow. That product workflow remains
outstanding; stored names alone do not establish which profile is executing.

Native/store and complete-package host tooling exists, but offline compilation
is not installation permission or a finished Senscope Builder/install path.
Senscope complete-path acceptance against the eventual frozen firmware remains
separate. Advanced authors should follow the boundaries and existing tool links
in [profiles/README.md](../profiles/README.md).

The accepted manual-update scope is narrow: Mk6 with a functioning valid store,
using the retained exact tested image and its approved evidence/custody procedure.
There is no final public install/update release workflow yet. Fresh Install and
recovery hardening remain deferred/unqualified; this guide provides no device
mutation or flashing sequence.

## What has physical evidence?

Selected Windows XInput/joy.cpl, original Switch USB/Ultimate and GameCube-adapter
routes have scoped PASS on one exact retained image. DInput was physical N/A in
that packet. Browser Gamepad/JoyCheck is NOT_QUALIFIED; Keyboard is deferred;
Switch 2 is out of scope/not tested; Nunchuk is NOT_TESTED. Source support for a
mode/backend is broader than that evidence. See [current state](CURRENT_STATE.md)
for exact source, tree, artifact, preservation scope and limitations.
