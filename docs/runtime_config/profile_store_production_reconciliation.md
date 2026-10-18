# Clean production continuation

## Superseding hardware acceptance — 2026-10-18

Exact candidate `af69dd91e629db852f1d2371e8d8c2d6b624fc54` has now passed its
bounded normal Configurator/persistence/transport hardware gate. B9/B10 exact
candidate correspondence is closed. The retained power/reserve debt is not
promoted to PASS or a new blocker; RT2 remains deferred/unresolved. See the
[hardware acceptance result](profile_store_production_hardware_acceptance_result.md).

Direct owner e1c7a932-d829-4a8a-ab7d-c42e6144cd0e (2026-10-18) authorizes this
bounded reconciliation. RT2 non-destructive recovery is DEFERRED, not PASS;
underlying USB cause remains UNRESOLVED. No controller action or canonical merge.
See [closure](profile_store_rt2_deferred_closure.md),
[B1–B10](profile_store_production_reconciliation_blockers.md) and
[factory follow-up](profile_store_factory_recovery_followup.md).

## Lineage decision

New branch `codex/profile-store-production-reconciliation` starts directly from
canonical6b73a7c507f35c111745c6bdd341618b490cbdcd. Its parent/merge-base is canonical,
not cb9a5ab5 or an RT2 experiment. The semantic audit covers all79 ancestry commits,
49 active-source changes and382 paths through cb9a5ab5. The4ee snapshot supplies
reviewed functional source because later ProfileStore.cpp is byte-identical;
it is not deemed clean by age. Mixed diagnostics in4ee are explicitly compiled
out or adapted. The [full partition](profile_store_production_partition.json)
and [final source manifest](profile_store_production_source_manifest.json)
record every selected/adapted path; [audit](profile_store_production_source_audit.md)
explains the behavior and exact retained USB call order.

| Class | Disposition |
|---|---|
| A — production retain | Persistent store, nonreused IDs, checkpoint/control roots, checked storage, atomic Config/reference publication, authenticated streaming migration, transaction receipts/reconciliation/high-water, capacity/reserve/GC,32-byte names, lazy health, reboot-bound selection/refusal and ordinary Configurator. Static workspaces/stack repairs remain. d596 outer USB mutex coordination,895 bounded TX servicing/tail drain and4ee RX cache/task servicing remain functional source. |
| B — tests outside production | Fault primitives, candidate protocol controls, trace/counter helpers and resource observers compile only under explicit isolated test flags. Host fixtures/oracles/physical-response fixtures and historical receipts remain. Ordinary glyph_mk6 enables neither STRICT nor RESOURCE and has no _sbrk wrapper. |
| C — RT2 retired | No RT2 setup/IRQ/branch/panic/raw-register/dashboard/LED/scratch observer source, private DCD replacement/build script, warm reset, cold intent or strong USB init is imported into production. ManualRT2 early route is removed. MB1 firmware bootloader route and MDST mode scratch remain. Historical investigation source is preserved in its exact published Git branches and docs; its artifacts remain in owner custody. |
| D — review before retain | No unresolved product/source decision is used as permission to retain code. Exact production preprocessing/linkage, affected host tests, final build/resources and fresh independent review are explicit gates. Hardware NOT_TESTED; no exact acceptance inherited from earlier candidates. |

B7A automatic recovery/refusal keeps initialize_recovery/BeginRecovery and
read-only backend policy. B7B manual RT2 is owner-deferred. Neither the physical
recessed BOOTSEL route nor MB1 software routing proves automatic recovery USB
recognition in the new production snapshot.

## Wire and test isolation

Request tags14–20/22/23 remain known for test compatibility. Production rejects
any nonzero retired control as INVALID before mutation or receipt reconciliation;
empty ARM13 and PULSE14 return UNSUPPORTED. Production does not silently execute
a requested fault/trace operation. Functional protocol2 receipts, token high-water,
incarnation and health remain. Strict/resource response scalars stay default and
are omitted from production wire encoding; removed root/RT2 tags52–217 are
reserved, never reused. Persistent Config/ProfileStore encoding is unchanged.

FaultHook storage/setter and trace state/callbacks do not exist in the ordinary
ELF. ReadTrace production helpers are constant no-ops. RX observations compile
only under STRICT or the explicit CDC coordination test flag; the functional
64-byte cache/task calls remain. Production sends no progress frames or new
telemetry. Tests opt in explicitly instead of making production controls live.

## Validation and resource contract

22 directly affected suites cover checked storage, atomicity/decoder/identity,
real predecessor, migration, Config persistence/reference purity/recovery,
backend packets/protocol/CRUD/replay/selection, USB mutex scheduling and bounded
large TX/RX, LittleFS long histories, StageA/B/C oracles and operator-tool bounds.
ASan/UBSan apply to native memory/transport/persistence harnesses. Production
protocol cases reject all9 retired controls without changing files/generation,
check empty ARM/PULSE refusal and zero diagnostic fields; explicit test variants
retain the former fault campaign. GPIO/reset/MMIO/electrical behavior is not
invented from host tests. All preliminary failures remain in the evidence bundle.

The new production composition checker has4 negative controls and verifies
ordinary weak TinyUSB init, one original DCD and absent retired linked symbols.
The READ stack checker has explicit production mode that refuses observer frames;
its ordinary observer mode still requires them. Both mismatched modes are
negative controls. Resource layout probes add a test-only header to their
analysis copy, never production source. Exact committed compiler database/ELF,
map, stack/ABI reports and immutable UF2 are bound in the final handoff; source
files do not fabricate self-referential Git identities.

Preliminary source measurement: RAM187320B, flash473300B with dirty version text;
heap arena capacity74628B. Backend444B, stream88B, Config31312B, profile2152B,
store4352B, request2304B and response3024B. Final committed values and hashes
supersede preliminary numbers in the handoff. CREATE/READ/RX enumerated bounds
remain within4096B scratch-bank envelope; no whole IRQ/ROM/indirect/runtime bound.
Production resource observers are off: current physical stack watermarks/heap
peak are NOT_MEASURED and historical receipts are not transplanted. This does
not remove static hardening or exact hardware acceptance before integration.

Framework/navigation checks remain required. The old C024 post-integration
scope checker rejects this new owner-authorized product diff at its historical
scope guard; its FAIL is preserved, not weakened or relabeled full framework
PASS. Fresh review must distinguish that frozen scope from actual Tier1/Tier2
product defects. No aggregate PASS or chapter DONE is claimed.

## Next ordinary task

Supervisor reviews this exact source candidate/evidence, records hardware wait,
and prepares a bounded exact-candidate normal Configurator/persistence/affected
transport acceptance issue. Useful authority must be adjudicated/preserved first;
there is no RT2, factory erase, cleanup or mutation permission from this source
pass. Any needed physical mutation fixture requires its separately explicit
owner-approved packet. Actual exact evidence precedes any proposed canonical
integration. No bespoke investigative branch, new standing timer or automatic
merge. Planner is needed only for a new bounded source issue if a concrete
blocker appears; RT2 cannot be the default next task. Factory recovery remains
a separate nonexecuting safety item, with public shipping gated on verification.
