# Host-only storage-fence repair

Owner direction is retained by Senscope's separate
`FULLPKG-B2-STORAGE-FENCE-REPAIR` Goal. This candidate descends from
`9108324fbcd6a119aea6e3811864b3d6af408ff7`; it is not an accepted source pin,
physical validation, or permission to merge into `configurator`.

## Strongest supported explanation

The HW4 recovery backend was freshly constructed and received only Identity and
STATUS. `_reference_unknown` initializes false and its sole true assignment is
the uncertain SET_MODE_REFERENCE save path. Thus `config.commit_unknown` implies
`Persistence::IsMutationFenced()` for that supplied history.

On the source-supported path to stage6, Config load completed. Its only possible
write was restoration of a selected prior; that rename is denied before package
classification/writer admission and would prevent reaching stage6. A nonempty
namespace then either passes complete package observation or refuses before any
bootstrap write. Recovery resets directory state and observes again. Under
ordinary source execution and consistent reads, the local Config fence remains
false and package classification supplies the fence. No physical memory-fault or
filesystem-content assertion follows.

Incarnation0/generation0/RootInvalid/LegacyUpgradeRequired can all result from
not admitting any root after `PrepareBeginState`, irrespective of disk format.
Neither the missing transaction-uncertain flag nor missing migration flag proves
healthy metadata. HW4's large high-water comes from a successful durable Config
reread; absent bit20 additionally supports root2 or managed root3 Config layout.

The exact HW4 Config CRC223169280 and token17293822569102712132 match the healthy
historical G6/HW5 observation: incarnation1/generation228/count26. Its exact
280-byte Config body SHA256 is
`804c2f86b78a70c5b25ce4eb5c8c301e8cd867d64a15dd023c9e75d98913363d`.
This is historical evidence, not proof of current roots, control, previous
revisions, migration provenance or retained filenames.

A concrete reachable refusal family is healthy compact-v2 metadata coexisting
with retained `config.bin` encoded before fixed32 Config fields205/209 existed.
The old writer retains that file. Both the current source observer and frozen
B1-R2 oracle reject its noncanonical encoding. Other possible refusals include
missing/corrupt peer/control, invalid Config/prior, incomplete publication temps,
migration proof mismatch, ownership or shared-receipt disagreement. Which exists
on the actual device remains UNKNOWN. Host fixtures model these separately.

## Repair and preserved refusal

Package-enabled Config selection is now read-only, including prior-only
selection, recovery, STATUS and reconciliation. It never restores/renames a prior.
A bad current still cannot fall back to prior or legacy. A selected prior never
counts as active G6 QUERY/SET_MODE_REFERENCE success evidence. A prior-only read cannot
clear the local publication fence in ReconcileConfig (nor can a current read while
the package fence remains set), and the strict package
observer continues refusing missing-current authority.

No classifier acceptance predicate, B1-R2 format, allocation, receipt, token,
writer lease, QUERY checkpoint, or filesystem byte is changed. Legacy-only,
missing-peer, staged, historical noncanonical and genuinely ambiguous namespaces
remain fenced. This candidate does not promise Normal boot on unknown HW4 bytes.
Automatically admitting/re-encoding the historical family would change frozen
B1-R2 source/canonicality rules and requires a separate boundary decision. Never
infer permission to delete `config.bin`, restore a Config, or clear the fence.

Fresh package-enabled STATUS also refuses health when its current Config reread
fails or only a predecessor is selected. It reports config.read_failed or
config.not_current and mutation_feasible=false; no persistent fence is cleared
or established by this diagnostic.

## Bounded read-only diagnostics

Protocol2 STATUS retains its schema and status/fencing meaning. The existing
96-character diagnostic distinguishes backend reference uncertainty, local
Config fence, package observation failure, root0/root1/control, slot pairing,
Config selection/validation, migration proof and shared receipts. The initial
failed boot observation's literal survives scratch destruction and recovery observation.
A fence arising after successful startup is labeled `package: runtime fence`.
No private contents or arbitrary filename are copied into it.

Additional informational bits in existing `recovery_flags` (not authority):

| Bit | Observation |
|---|---|
|21|Local Config mutation fence|
|22|Package MutationFenced (combined)|
|23|Package mount availability false|
|24|Last selected checked Config is current|
|25|Last selected checked Config is prior|
|26|Last selected checked Config is legacy|
|27|Package sticky fence|
|28|Package classification Unclassified|
|29|Package classification Unsupported|
|30|Package classification Unresolved|

Bits24–26 are mutually exclusive; none means no successful selected load. They
are emitted only during refusal/recovery; healthy Normal STATUS retains flags0. Existing bit18 remains the combined
backend/Config/package condition. Recovery still forces read-only status.

## Reproduction

Use the existing transaction build with `--boot-probe`, then run
`storage_fence_regressions.py --binary <built-harness> --corpus <frozen-corpus>
--out <new-dir>`. Optional `--historical-config <private-280-byte-body>` verifies
the exact historical hash before pairing it with explicitly SYNTHETIC roots.
That optional tuple has no reconstructed directory/payload correspondence and
is only a classifier/startup seam probe; backend initialization remains a stub.
No test image represents the actual physical filesystem. Test `seed` alone
formats synthetic NOR; all production startup/recovery/STATUS paths assert
unchanged raw NOR and zero program/erase calls. Thirty-four focused cases with the
historical witness and the existing58 boot families cover finite Normal/refusal.

Future physical work needs one new exact UNAPPROVED Phase-A packet: install once,
boot against untouched storage, require Normal/ordinary Configurator/Identity2
backend8 and healthy unfenced read-only STATUS. On recovery capture diagnostics
and stop without cleanup/retry. PhaseB is disabled. No physical operation occurs
in this software Goal.
