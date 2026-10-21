# Frozen35e8 joint-state continuation and lifecycle erratum

Frozen `35e8e5af99badf425fd832968040e8fd6a23441a` tree `bc53491c921c082bd43d72d9ad4cbbaf0eeb4546`. Eight relevant source files were read from Git and independently matched the immutable9cff archive; ef22 exact ELF remains `5d3f25e40b1b3765f891f3bc8f3fa16ff3c67483104c6f08f609a8569bede78f`. No source/device/new-image work.

## Explicit correction

The earlier report remains unchanged as history. Its direct Configurator Reconcile2116/2140 rows are **conditional generated-state compositions**, not established first-writer witnesses with initial positive-orphan state. The earlier lifecycle proof omitted boot reconciliation and permanent recovery-only state. Boot Reconcile2140/2164 remain established and adequate concrete C evidence; this correction does not remove them. The other eight supported original rows remain: boot2140/2164, Update2052, Duplicate2052, legacySET2196, copy2308, Identity2168/2200.

## Query retry

**Initial unchanged boot-state joint predicate is excluded; general generated-state retry remains OPEN.** Query/LoadDirectory guards alone do not prove exclusion.

- setup must successfully load Config then Begin before normal backend initialization. Bootstrap phase3 sets uncertain and invokes Reconcile. On failure setup calls enter_recovery_configurator, which calls initialize_recovery→BeginRecovery. PrepareBeginState sets _recovery_only=true; every LoadDirectory sets _read_only_recovery = _recovery_only || !root0 || !root1. Later Reconcile stops before phase3 writes.
- Normal successful phase3 Begin clears uncertain before normal service. Phase2 Begin leaves uncertainty false while initial unrelated positive-orphan may remain.
- During service, failure of first PublishDirectory control3 before a filesystem operation may set uncertain=true without clearing initial orphan. However durable control remains the old phase2. A subsequent successful Reconcile compares phase2/current directory and clears uncertainty read-only; it does not enter control2/abort writer.
- Producing durable phase3 in service requires successful control3 temp writable-open/consistency and rename. That already consumes initial pending recovery. Any positive-orphan at a later retry requires separately proved generated recovery provenance.
- Query(token) can retry failed direct Reconcile because uncertain remains; identity overload inlines token logic and adds64, token-only24 is an alternative. If LoadControl/LoadDirectory failures recover, guards can admit second writer for service-generated phase3. No physical transition establishing all required state and second-success was found.

## Actual fault sources

- CheckedStorage hook is null until PrepareProfileMutation→BeginMutation, reached only AFTER PrepareStoreMutation Query and Load. EndMutation clears hook on every original scope exit; prepared tickets alone are inert. A prior rule cannot generically inject an initial direct-Reconcile/Query read failure.
- Pinned SDK lfs_flash_read memcpy returns0; sync is no-op return0; program/erase also return0 after actual operation. A random transient Read ERR_IO is not an evidenced production source, and a host-double failure is not target feasibility.
- Persistent corrupt/invalid control/root does not become valid merely because another read is attempted. No concurrent IRQ/core1 filesystem writer exists. These facts do not by themselves prove every cache/allocator/badblock failure and generated-repair sequence unreachable.
- Potential lfs allocation/CRC/program-verification/relocation failures require an exact recoverable source history and retained pending state; no arbitrary RAM corruption, disappearing mount, external concurrent filesystem mutation or generic synthetic fault is assumed.

## Nested PriorCompact restore

**Initial unchanged boot-state joint predicate is excluded; later generated or partial-repair histories remain OPEN.** Recovery/fence status alone does not suppress PrepareStoreMutation's load.

- select_config_filename selects current whenever Stat(current) succeeds. Current-but-invalid data is rejected; it does not fall back to prior. PriorCompact requires current absent and prior present.
- Normal setup LoadConfigChecked restores selected valid prior before Begin/backends. A failure enters recovery; initialize_recovery again loads/restores before creating Configurator. A successfully restored prior is now current before nested service loads.
- If recovery load remains invalid, legacySET refuses (_recovery_service/_recovery_config_invalid). STATUS load is guarded by !config_invalid, but PrepareStoreMutation still calls LoadConfigChecked before later recovery/fence refusal. Thus recovery guard alone is not a blanket proof that all nested prior loads are unreachable.
- In normal service, only Save rotation makes existing current absent. Save publication failure with current=true attempts rollback; rollback failure or uncertain publication fences mutation. LegacySET rejects that fence. Dispatch attempts ReconcileConfig BEFORE PrepareStoreMutation, so ordinary successful prior restore occurs at shallower prefix first.
- A failed earlier restore can partially change metadata/cache/repair state; a later PrepareStoreMutation Load might then succeed. Whether it can retain applicable generated positive-orphan and reach the deeper compaction path is unresolved. It is not excluded merely by the fence, since Prep load is unconditional before its fence-status branch.

## Conditional accounting, not additional witnesses

| Unproved joint branch | Foreground | Premask | CDC IRQ | Conditional total |
|---|---:|---:|---:|---:|
| QUERY-TOKEN-CONTROL | 1896 |16|340|2252|
| QUERY-IDENTITY-CONTROL | 1936 |16|340|2292|
| QUERY-TOKEN-ABORT | 1920 |16|340|2276|
| QUERY-IDENTITY-ABORT | 1960 |16|340|2316|
| PREPARE-MUTATION-PRIOR | 1744 |16|340|2100|
| LEGACY-SET-PRIOR | 1968 |16|340|2324|
| RECONCILE-CONFIG-PRIOR | 1712 |16|340|2068|

These numbers quantify the consequence only if an ordinary source-generated state and recoverable earlier failure are established. No such complete history was proved here. Identity64 and token24 are alternative callers; no double-count. Query abort adds PublishDirectory24. C retirement changes every Reconcile composition; E retirement may change legacy receipt loading. Existing source-authorized edits must be measured before using these pre-repair totals as new scope evidence.

## LegacySET witness unchanged

Already valid current compact/rootformat2 Config, healthy phase2 control/roots, valid compact receipt, no MigrationPending. setup Load/Begin/receipt check performs no marker Save, migration, or control3 publication. Existing pending orphan can survive all read-only validation and legacySET decode/validate/profile reads until Save first Remove.

Its2196 total therefore remains an initial-state source-feasible composition. The newly identified prior-restore joint condition is not needed for that Save-first-Remove witness.

## Decision and limits

No additional named source retirement is justified as a concrete defect by these two joint states yet. If a generated-state history later establishes them, candidate methods are PrepareStoreMutation (return query/receipt/loading phases before retry writer), HandleSetConfig receipt-loading preparation, and the ReconcileConfig result wrapper. These are conditional method names, not adopted edits or permission requests. Preserve exact query identity/token/status/high-water and Config/fence order.

This narrow role is complete. Ordinary boot/service invariants exclude only the named initial-state histories; they do not prove all generated filesystem/error histories safe. Remaining final31/all-path ELF/source/bothABI/build/custody/hardware gates remain OPEN. Runtime model/effort observed UNKNOWN.
