# Active stored-profile display identity

Status: source candidate preparation; hardware display acceptance NOT_TESTED.

Owner work order: direct 2026-10-25 chat instruction, bounded display/UI only.
Live canonical verified `a6e3bc885d46e2a7412ec697aa822bcd8c4ce495` before work.
The owner reports current ID27 Pikachu selected safely, ID51 Kazuya accepted v4,
and superseded48–50 removed. This newer owner statement supersedes the older
prepared-but-unexecuted cleanup prose; no controller readback occurred here.
Accepted payload sources and all profile/store/selection/evaluation semantics
are outside this chapter. Branch: `codex/active-profile-display`.

## Diagnosis and ownership

Dashboard `MenuButtonHints.cpp` printed `GameModeConfig.name` directly, hence
`Ultimate Runtime`; `plate_name(UNSPECIFIED)` generated `Unknown Plate`.
`InputDisplay.cpp` used the same internal name. Current end-user identity is
`ProfileStore::Entry.name` for the actual executing stored native record.

Shared presentation-only `current_profile_label` checks the actual Ultimate
object, native execution engine, compact Config, requested/active ID equality,
ready/non-recovery store and selected payload identity/schema. It returns a
bounded, nonempty, terminated current native directory name. Otherwise it uses
the existing Config mode name or `gamemode_name`. No cached previous name,
profile-name buffer, heap allocation, storage read or persisted field is added.
A failed `Activate` can retain the old ID: native execution and selected-payload
checks are essential, rather than treating an ID alone as successful identity.

The resolver's read-only safety is lifetime-based, not intrinsic thread safety:
`ActiveId` and directory access are plain reads. `config.cpp` boot-state mutex
publishes completed Begin/backend activation before `setup1` proceeds.
`mode_selection.cpp` activates only at backend initialization; ordinary profile
selection posts the existing mailbox, persists destination on core0 and reboots.
Candidate reads use separate workspace. Directory and active identity remain
immutable throughout normal gameplay/display. Configurator is the only live
store writer; its remapper route returns from `loop1` without normal rendering;
recovery initializes no normal viewer/menu. The resolver excludes Configurator
and unspecified backend before any store access. This matches the existing
`.Profile` browse exclusion in `DefaultConfigMenu.cpp:54`.

This contract must be revisited if future work adds live activation, store writes
alongside gameplay, or normal rendering during Configurator. No synchronization
mechanism or evaluator/display coupling is introduced here.

## Plate semantics and surface inventory

`schema/haybox/config.proto` defines per-mode `layout_plate`. `config.cpp` maps
it to the viewer's button drawing layout; unspecified shares the full drawing
fallback. That does not detect a physical plate. Defaults explicitly use Full;
old mode-to-plate assignments are commented out. Native runtime contexts may
legitimately omit this optional metadata. No character/plate relationship or
authoritative physical detector was found.

Dashboard now leaves line30 blank for unspecified and preserves Full/FGC/Split
FGC/Plat Fighter for specified values. It does not change Config or viewer
button geometry. Invalid unknown enum values retain the old unknown fallback.

Current-identity surfaces changed: dashboard and input viewer, both through one
resolver. Ordinary Config-row text in `DefaultConfigMenu.cpp` remains intentional
mode-selection text. `config.cpp` layout dispatch is geometry, not identity.
A source search found no other current-name miniscreen surface requiring change.

## Evidence and acceptance boundary

[Focused checker](../../../tools/check_glyph_active_profile_display.py) exercises
actual native decode/publication/Ultimate activation, actual resolver and actual
input-viewer rendering on both ABIs with ASan/UBSan. Store metadata is explicitly
doubled; source ownership is audited separately. It covers Pikachu, arbitrary
Fox, Kazuya switch, unresolved/mismatched/invalid metadata, failed native activation,
ordinary modes, specified/unspecified plates and writer exclusion. The checker
also binds both current-name call sites. Existing selector/menu and persistence
checks remain unchanged. Results, exact candidate/custody/resource and independent
review are recorded separately as they become available. No aggregate PASS is
claimed by omission.

[Owner packet](OWNER_PACKET.md) remains unexecuted, requires separate owner
approval, and never creates/updates/renames/reorders/deletes profiles.
Firmware flashed: NO. ProfileStore mutations: NONE. Profiles modified: NONE.
Pikachu gameplay state unchanged; Kazuya accepted gameplay baseline unchanged.
Hardware display acceptance NOT_TESTED. Nunchuk NOT_TESTED; root cause UNPROVEN.
