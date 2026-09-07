# One-Time Supervisor Curator Adjudication — 2026-09-07

Status: ACCEPTED_BOUNDED_TRANSITION.

This adjudication applies the exact owner decisions recorded as
`GLYPH-UD-013` through `GLYPH-UD-015` to live canonical source at
`8b4babd8ebea7e4f363b694eeb27435a47befbe7`. It does not broaden those
decisions or replace the immutable initial Planner/Curator receipt for packet
`glyph-portfolio-20260907-1359`.

## GP-VAL-011

Disposition: `REVIEW / OWNER_DEFERRED / NONEXECUTABLE`. The queue retains the
item and all historical evidence but removes `REPAIR_REQUIRED` as a current
liveness signal. This is not DONE, Ready, Preauthorized, hardware-pending, or a
claim that the objective is infeasible. Fresh substantive authorization and a
new complete contract are required to reopen it.

## GP-ART-001

Disposition: H1 `READY` for the exact owner-held local custody policy, tooling,
synthetic adversarial validation, framework-locator enforcement, and hardware
instruction integration in `HARDWARE_ARTIFACT_CUSTODY.md`. The scope has no
build, real firmware artifact, upload, external service, credential, device,
or hardware action. The Planner candidate is fully resolved by
`GLYPH-UD-015`; completion still requires independent review, canonical
implementation ancestry, and separate structured DONE publication.

## GP-CONFIG-005

Disposition: H2 `READY`. Current source fully determines the smallest bounded
architecture:

- use function-static `Config` candidate storage in
  `ConfiguratorBackend::HandleSetConfig()`; a stack object is rejected because
  the generated Config is larger than the current linked automatic stack
  bounds, while a backend member would enlarge the dynamically allocated
  backend;
- reset, decode, and run every existing bounds/type/reference validation only
  against the candidate;
- call existing `persistence.SaveConfig(candidate)` while live `_config`
  remains unchanged;
- on any rejection, keep `_config` byte-for-byte unchanged and preserve all
  existing error packet/text and false-return behavior;
- only after `SaveConfig` returns true, assign `_config = candidate` once, then
  preserve the existing success packet and true return;
- remove the decode-error disk reload because rejected candidates no longer
  mutate live RAM.

`Config` uses fixed embedded arrays in the pinned generated shape. Existing
mode/display/backend objects hold the live object or pointers into those
arrays; assigning into the existing `_config` storage preserves addresses.
The work order does not promise broader successful-update cache/rebind
semantics. Static candidate storage requires canonical build/map/RAM proof.

The existing `Persistence::SaveConfig(Config&)` does not intentionally mutate
its input, but it truncates and rewrites `config.bin`; several write, seek, and
close outcomes remain unchecked. A false save must leave live RAM unchanged,
but the disk may remain partial/corrupt. A true save is not new durability
proof. `GP-PERSIST-001` remains the authority for those limitations and its
source-correspondence packet/checker must be renewed for the changed SetConfig
steps without selecting a persistence mechanism.

Production-path host tests must prove every current rejection class, injected
save false, one successful save/publish, unchanged live bytes/pointees on
failure, stable live/subobject addresses, exact existing response behavior,
and no disk-rollback claim. The exact candidate then requires
`pio run -e glyph_mk6`, memory/map review, independent review, content-addressed
artifact custody, and `GP_CONFIG_005_HW_V1` physical PASS before merge.

Excluded: `Persistence.cpp/.hpp` mechanism changes, boot/load/autoformat or
power-loss policy, schema/protobuf expansion, official configurator, new
WebSerial/device-write paths, successful-update runtime redesign, runtime
tables, gameplay semantics, flashing automation, or device fault injection.

## Packet And Liveness

Both surviving Planner candidates are now represented by canonical work
orders, so the packet becomes `CONSUMED` with no survivors and a material owner
decision event. The immutable receipt retains its truthful initial
`USER_DECISION_GATED` dispositions. `curator_review_required` and the global
wait proposal are false. While the H1 custody order and H2 SetConfig order are
Ready, primary liveness is derived from actual runway rather than the deferred
validation lane. No broad Planner refresh is required merely because the two
known gates were consumed; the ordinary Implementation Supervisor has exact
executable work.
