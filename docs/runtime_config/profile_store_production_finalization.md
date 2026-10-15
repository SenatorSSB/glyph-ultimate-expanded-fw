# ProfileStore production finalization — 2026-10-15

## Hardware reconciliation and strict closure — 2026-10-15

Current disposition: **MULTI_PROFILE_STORE_STRICT_DONE_REVIEW_BLOCKED**.
The owner's final-production hardware result is **PASS** for exact tested
source `f7ba82d4cbe79d4353e8d87b7d1b24be3fc15113`; it does not discharge every
frozen chapter requirement. See the [strict requirement review](profile_store_strict_done_review.md)
and [hashed evidence receipt](profile_store_hardware_acceptance_receipt.json).
This current disposition supersedes pending final-candidate hardware wording
below; earlier sections remain historical evidence, not renewed test requests.

The tested tree is `fea1c14a5775b8f5db5ce85b2fed95ad6411d485`, parent
`08296b0e72f440e6536cff45246c57bb17bc9868`, base/merge-base
`6b73a7c507f35c111745c6bdd341618b490cbdcd`. Its preserved UF2 is 935424 bytes,
SHA-256 `256d6e613750106e8c5f4938179331cc13db75b47e1a02a625de42277cef3a21`.
The About/device revision was `f7ba82d4`. The artifact was rehashed during this
reconciliation; no firmware was rebuilt, flashed, or newly tested.

The final owner packet normalized inherited durable USB3 once to USB1, then
proved menu Configurator entry was temporary. Reference mode1 ID3→ID4 changed
only the requested durable reference; USB1 and all unrelated fields stayed
unchanged. DELETE refused both live ID3 and saved ID4 before reboot. ID4 and
USB1 survived reboot; restoration ID4→ID3 survived the final reboot. Store
stayed generation8 with ID1 rev2 `CRUD Primary` rank20, ID3 rev1 `Migrated 1`
rank0, ID4 rev1 `Migrated 2` rank1, and ID2 absent. Config remained compact1,
zero embedded profiles, references index0 none/index1 ID3/index2 ID4. IDs3/4
were readable and byte-serialized equal to Stage-C source profiles.

The parent4ac255eb CREATE/CRUD and migration mechanics PASS remain valid in
their observed scope. Migration PARTIAL does not mean failed migration: the
missing Runtime-B physical output observation is separate from the repaired
selector-state persistence defect. F1–F6 and intermediate failed candidates
retain their original classifications. The original hang's precise physical
root cause remains UNPROVEN.

The owner authorizes documentation/evidence only in this reconciliation.
Concrete frozen implementation/evidence gaps stop strict DONE; no source
repair, architecture waiver, new candidate identity or canonical merge is
performed. Canonical remains `6b73a7c507f35c111745c6bdd341618b490cbdcd`.

## Historical pre-hardware finalization record

Disposition: production candidate preparation under the direct owner's request,
not canonical integration or strict chapter DONE. Parent hardware lineage is
`4ac255ebc6d2e416e0a7945614f3a3dcdbbd7922`; canonical remains
`6b73a7c507f35c111745c6bdd341618b490cbdcd`. The owner's attached request has
SHA-256 `e15a11c4aa5ea60c11d5a16a12e9fc13dbd9972c80822f318f2835aa581180c6`.
It explicitly authorizes this bounded reference-transaction repair, diagnostic
retirement, evidence update, review and exact production candidate. No device
operation or canonical merge is authorized or performed here.

## Defect and complete live mutation audit

`SET_MODE_REFERENCE_PERSISTS_TRANSIENT_RUNTIME_SELECTION_STATE` is a Config
transaction-purity defect, not migration or stable-ID failure. The hardware
fixture's durable USB selector started at1. Configurator watchdog selection set
live USB selector3; reference SET saved the entire live object, unintentionally
making3 durable, then restored only its two temporary reference fields.

Source inventory below refers to the accepted parent; class A means deliberate
immediate persistence, B means a live change without immediate persistence, and
C means unresolved source/product intent. Menu-field eventual persistence intent
is undocumented, but their lack of immediate persistence is source-proven: they
must not join an unrelated reference transaction.

| Live mutation | Classification and source |
|---|---|
| `default_usb_backend_config` | Conditional A/B: watchdog selection in `HAL/pico/src/comms/backend_init.cpp` `get_backend_config_default`; `initialize_backends` saves only non-Configurator selection. Configurator selection remains B. |
| `default_backend_config` | Same conditional A/B path and save guard. |
| `communication_backend_configs[i].default_mode_config` | Same conditional A/B: temporary mode override in `initialize_backends`, non-Configurator save guard. |
| `rgb_brightness` | B: `HAL/pico/src/display/RgbBrightnessMenu.cpp` increment/decrement; no immediate save. Eventual durability intent C. |
| `default_dashboard_option` | B: `config/glyph/common/src/display/GlyphConfigMenu.cpp` selection; no immediate save. Eventual durability intent C. |
| target mode reference and legacy profile index | Requested A, formerly unsafe temporary live edit in `ConfiguratorBackend::HandleProfileStore`; now durable-only candidate edit. |
| whole Config after explicit SET | A: `ConfiguratorBackend::HandleSetConfig` publishes live candidate only after save succeeds. |
| whole Config after migration | A: `config/glyph/common/src/config.cpp` publishes compact candidate after save/completion. |

`DefaultConfigMenu` and `OopsieMenu` selector paths write watchdog scratch then
reboot into the selector code above. Runtime mode selection changes backend/mode
state, not Config fields. Commented SOCD editing is not an active mutation path.
The four Config persistence callers are explicit whole-Config SET, reference
SET, non-Configurator boot selection, and compact boot migration. No other
ProfileStore CRUD operation saves Config. Tests assert its save-call count.

## Repair and generation contract

The two Configurator write handlers share one existing static Config scratch,
owned synchronously by core0. This avoids adding another approximately31KB
object or a large automatic frame. Reference SET never edits `_config`:

1. Check expected store generation and cached Config generation.
2. Load and validate currently durable Config into the separate candidate.
3. Compare expected Config generation again after checked load. The generation
   is the existing checked protobuf-body CRC, not a monotonic counter or a new
   on-disk field; `ConfigGeneration` returns persistence's cache, not a live hash.
4. Check compact format, target index, MODE_ULTIMATE and selected profile
   existence (ID0 remains the built-in selection).
5. Change only target `ultimate_profile_id` and `ultimate_profile_config = 0`.
6. Validate the candidate, then `SaveConfigIfGenerationMatches` rechecks the
   cache and freshly reads/verifies the authoritative durable file's CRC before
   staging. A changed generation conflicts; unreadable/corrupt storage fails.
7. Atomically publish through the existing compact save primitive and return
   the new checked generation. Do not copy the candidate into live Config.

All Config writers execute synchronously on core0; there is no Config writer
callback between the final fence and publication. The fresh durable check also
rejects a valid on-disk replacement not reflected in the cache. CRC collision
resistance and physical ambiguous I/O are not new guarantees of this existing
protocol. Reboot remains the activation boundary, and consecutive reference
saves derive from latest durable Config, not old live session selections.

DELETE also checks the union of live and freshly loaded durable references.
This closes the directly coupled gap where newly saved ID4 could be deleted
before reboot while live still referenced ID3. Both IDs remain protected during
that interval. Durable-load failure refuses deletion without store mutation;
this preserves the frozen design's referenced-delete rule.

## Independent-review root recovery repair

Fresh review reproduced a pre-existing frozen-contract violation in current
production source: CREATE IDs1/2/3, corrupt newest root, reboot into generation2,
then CREATE allocated ID3 again. This is a concrete identity-safety defect, not
framework debt, and the requested root-recovery regression made it blocking.

Root loading now distinguishes absent files from existing invalid/unreadable
files, clears stale in-RAM directory entries before every reload, rejects both
invalid roots and conflicting valid incarnations/equal-generation contents, and
keeps a valid fallback read-only when its companion is damaged. A missing
companion after generation1 is also ambiguous and read-only; the first valid
generation1 root remains writable. No schema or automatic repair/reset is added.
Boot selects existing recovery/refusal; STATUS exposes `directory.recovery`,
readable fallback records remain inspectable, and CRUD allocation plus reference
SET are fenced. This also conservatively fences some interrupted inactive-root
removals after reboot: no implicit claim about the missing high-water mark.
A namespace reported as having neither root still follows the existing empty
initialization path; Boolean filesystem existence cannot certify arbitrary
physical I/O or distinguish all external loss scenarios. No orphan scan or
activation is introduced.

Regression tests reproduce and prohibit ID3 reuse, cover both-invalid, missing
companion, unequal-incarnation and equal-generation conflicts, retain initial
CREATE, and prove empty reload cannot inherit stale entries. Stale-file and
rotating-fault fixtures explicitly test recovery refusal before restoring only
their injected root fault for independent subsequent cases. Production performs
no such repair. These new recovery restrictions require final-candidate hardware
acceptance; the earlier4ac255eb hardware PASS does not cover them.

## Compact save failure boundaries

Staged Config is closed and checked before any root rotation. Successful
`config-v2.tmp` to `config-v2.bin` rename is the publication point. The former
post-publication reopen could return false after new bytes were already durable
and leave the generation cache stale; it is removed, and successful publication
immediately updates generation. This is not removal of staged verification.

When current exists, an existing prior file must be removed successfully before
rotating current to prior. When only prior exists, preserve it as the recovery
anchor through both failed and successful publication. Failed final rename
attempts rollback; if rollback also fails, the same prior bytes remain selected
by existing compact recovery. The immutable legacy `config.bin` is never a write
target. Host fault tests model definite no-op failures and interrupted rotation;
they do not prove physical power-loss, LittleFS close/sync acknowledgement or
flash timing. A real lost acknowledgement after commit remains an observational
uncertainty, not a host-proven unchanged-disk claim.

## Diagnostic retirement and retained repairs

Removed the CREATE probe header, eight-second watchdog arming, scratch stage
writes, `create.hang.stage`, `create.last.stage`, probe-only boot routing and
mutation refusal, all stage calls, and fake-watchdog/probe-only host tests.
Historical diagnostic reports remain evidence, explicitly labelled superseded;
they do not describe the new production binary. The normal RT2 recovery branch
and its MB1 priority remain unchanged.

Retained: small CREATE/DUPLICATE frames, static boot migration candidate,
separate bounded readback and exact expected-byte comparison, cached CREATE
replay, two-second ProfileStore TX deadline, partial-TX delimiter recovery for
legacy commands, direct directory decoder, valid short temporary filenames,
and contextual `record.*`/`directory.*` diagnostics. No protocol, schema, profile
format, controller/game semantics or core1 flash lockout redesign.

## Accepted owner hardware evidence

These are the owner's explicit observations for parent4ac255eb, not tests
performed by this agent. Its previously frozen clean-label UF2 was936960 bytes,
SHA-256 `13d22547a963e0eb8a1e919aab218b1a71c655d5351f8f3944082107b546ca51`.
The new production descendant does not inherit exact-artifact hardware PASS.

| Evidence | Accepted scope |
|---|---|
| `MULTI_PROFILE_STORE_CREATE_PATH_HARDWARE_PASS` | First real CREATE, directory publication/reboot, stable ID and source payload equality. |
| `MULTI_PROFILE_STORE_NONREFERENCE_CRUD_HARDWARE_PASS` | UPDATE, DUPLICATE, RENAME, REORDER, DELETE and reboot reconstruction. Generation6; ID1 rev2 `CRUD Primary`, rank20; deleted ID2 absent. |
| `MULTI_PROFILE_STORE_MIGRATION_REFERENCE_HARDWARE_PARTIAL_PASS` | Persistence rows PASS: exact6248-byte Runtime A/B fixture; generation6→8; IDs3/4 allocated, ID2 not reused, ID1 retained; payload equality; compact format1, no embedded profiles; mode1→ID3 and mode2→ID4; no replay after reboot; reference3→4 persisted at store generation8; DELETE ID4 refused and readable; restore4→3 persisted. |

Final reported parent store: generation8; ID1 rev2 `CRUD Primary` rank20;
ID3 rev1 `Migrated 1` rank0; ID4 rev1 `Migrated 2` rank1; ID2 absent.
PARTIAL is confined to missing physical runtime-output observation and the
selector-persistence defect; migration/reference persistence itself passed.
The historical CREATE hang's precise physical root cause remains unproven even
though the combined repaired candidate passed physically.

Runtime-B `Z + down-left -> (-38,-39)` remains
**NOT_TESTED — PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE**. No replacement is invented.
`mode_selection.cpp` calls `profile_store.Activate(mode_config.ultimate_profile_id)`
and passes the result to `ultimate_mode.SetConfig`; this proves source routing,
not observed controller output. The specific physical discriminator is not an
explicit frozen closing gate; stored/migrated Stage A/B/C oracle correspondence
is a required host gate. Separate frozen target geometry/interruption evidence
and exact final-candidate affected hardware acceptance still apply. This
bounded handoff cannot silently close missing chapter-wide evidence. Nunchuk
remains NOT_TESTED. No strict DONE, merge or public-release claim.

## Validation, resources and independent review

Full directly affected suites are run on final source: real retained backend,
ProfileStore atomic/decoder/lifecycle/migration/recovery/path/stale-file/replay,
pinned LittleFS RAM model, real predecessor Config and frozen Stage A/B/C.
New current-source Persistence tests exercise compact atomic save, generation
fences, durable replacement races, prior-only recovery and failure publication.
The reference regression asserts exact durable encoding except the two intended
fields, whole live Config byte equality, reboot load, ID0, consecutive saves,
both DELETE reference guards, and11 failure/race cases. ASAN/UBSAN are enabled
for backend, current Persistence and pinned LittleFS suites.

The historical SetConfig aggregate rejects changed lineage at its frozen C024
scope gate before running the harness. It is not waived or reported PASS.
The initial preliminary build refused unstaged tracked probe-file deletions at
the repository integrity guard; staging the intended deletions resolved that
build-input issue without weakening the guard. All attempts remain in custody.

Production compilation database measurements now also include Persistence load,
conditional save and save frames (512-byte individual gates). The final clean
committed build, RAM/flash, BSS/data deltas, exact cumulative stack report,
review receipt and artifact identities are recorded in the content-addressed
handoff manifest after commit; no self-referential source SHA is fabricated.
Static scratch reuse avoids a new Config allocation. Whole-target stack/IRQ/ROM
and runtime heap sufficiency remain bounded by the same disclosed limitations;
a successful build alone is not physical controller acceptance.

Delegation: native collaboration discovered; bounded mutation/source-authority
audit and actual Persistence tests, retained-backend regression worker, and a
fresh independent production reviewer. Requested Sol medium for finite workers,
Sol high for coupled independent review; no stronger execution identity inferred
beyond runtime-reported selection. Root retains integration/publication. No new
user chats, Planner/Curator, canonical publication or device action.

## Minimal next final-candidate hardware packet

Preserve the parent's exact durable Config/store backup and the new candidate's
exact UF2 custody. Owner performs only the separately authorized manual update.
In normal Configurator, establish ready STATUS, generation8 and IDs1/3/4 with
ID2 absent; unexpected state stops the packet. Record current durable selector
and mode defaults from Config without normalizing or rewriting them. The prior
campaign may already have persisted USB3; this repair deliberately does not
invent a restoration of historical durable defaults. A discriminating test must
start from an explicitly prepared/backed-up durable baseline differing from the
temporary Configurator selection (for example the accepted fixture's USB1).
Any required baseline restoration is an explicit test setup, not part of the
reference transaction or an automatic migration.

Save mode1 ID3→ID4 with the freshly observed Config/store generations. Confirm
only the requested two reference fields changed in persisted Config, including
all selector/default/brightness/dashboard fields. Before reboot, DELETE ID4 must
return REFERENCED; current live ID3 remains protected. Perform one approved
reboot/load, confirm ID4 and unchanged durable defaults, generation8, IDs1/3/4,
ID2 absent and no migration replay. Restore reference ID4→ID3 with fresh fences
and confirm persistence on the agreed restoration reboot. No new CREATE/CRUD
campaign, factory reset, physical runtime-discriminator substitution or automatic
flashing. Final controller-output acceptance and any outstanding frozen
geometry/interruption evidence require their own real evidence; do not infer
strict DONE from this packet alone.
