# Exact display candidate finite resource proof

PASS_FINITE_LINKED_RESOURCE_PROOF_UNCHANGED_LIMITS for source candidate
`e416cabe3e0878e69036d2f75d59eed0d4d05208`, tree
`c071f006e3e21b5e3146a85c8a767264e8822264`. Exact candidate ELF SHA-256:
`97b940dd8dd7b59875e11f4642baa61ddf2c7806b74fd19a59b9ad7a157d8991`.
Fresh canonical baseline ELF:
`95eb7657b01a3febb916ce477ef61cfcb453325719f44e3ad99442574fd5186b`.
[Result](result.json), [evidence manifest](manifest.json), and
[correspondence](correspondence.json) retain exact measurements.

The first copied cache was from an older campaign. Audit identified SSD1306 and
Nanopb drift before handoff; those interrupted/noncandidate builds supply no
acceptance. Root restored the complete accepted menu libdeps cache (Nanopb
0.4.92) and rebuilt both exact baseline and candidate. All259 baseline compiled
source hashes, including the generated descriptor, now match the accepted menu
inventory. Candidate matches257 prior sources; only the two intended display
surfaces differ, with the new bounded resolver as an additional translation unit.
All90 relied SDK/vendor pins and the exact compiler hash match. No dependency
change is included in the firmware source branch.

Fresh accepted-menu-to-canonical comparison preserves all3059 named linked
frame/direct-call/indirect-register/tail signatures, with no added or missing
function. Canonical-to-candidate preserves3057. Only dashboard and viewer
UpdateDisplay bodies differ, each retaining its48-byte linked frame. The sole
new function, current_profile_label, is272 code bytes with a24-byte frame and
only direct calls to existing metadata accessors and bounded strnlen. Its
metadata methods/strnlen have zero linked frame in this target; its composed
bound is24. The dashboard's extra CurrentGameMode virtual read uses the same
existing accessor family; register allocation changes introduce no new virtual
target class. No allocation, I/O, buffer, owner, initializer or recursion is
added. Both surfaces' full conservative bounds remain768.

All318 sized mutable-symbol records preserve exact name/address/size/type.
All153 actual vtables preserve slot target identity, including relocated RTTI
metadata slots;879 relocated words resolve to the same named targets, with zero
unresolved vtable slots. All4 preinit and23 init entries preserve target order.
Code and read-only data relocate in this build. This is a resource proof based
on actual linked stack/call graphs, fresh vtable targets, unchanged source and
SDK predicates, not a claim that all non-display instructions or literal-pool
bytes are byte-identical. Exact disassemblies are preserved for reproduction.

Fresh core1 replay reports setup960, loop976, no unknown targets/cycles, and
outer16+IRQ68+loop976=1060. This remains below the existing1152 retained bound
and2048 reservation. The new resolver does not enlarge the longest route.
Every140 old,39 selector and14 GameCube component equation replays to its prior
maximum2048/2012/1344. Unchanged core0 source/graphs, startup/class targets and
SDK pins permit their existing predicates and finite class union to transfer;
no new profile label caller enters core0 gameplay/storage. Core0 remains
2048/2048 with **zero margin**. No cap increase or new scope exclusion buys room.

Actual .data25044+.bss173244=198288, unchanged and1344 below199632. Both stack
reservations remain2048; heap capacity63660 is unchanged. Names are borrowed
from stable directory metadata; no duplicated name buffer or refresh heap is
introduced. The existing allocation bounds remain applicable. Flash511188 vs
baseline510956 is+232bytes. Root's fresh both-ABI native/layout evidence is
[retained here](abi-layout.json); no layout caps changed. This is the production
small-enum ELF proof, not a second no-short-enum firmware build.

Both current resource checkers were actually run and their failures preserved:

- check_glyph_liveness_resource_safety.py fails identically on exact baseline
  and candidate because its expected legacy InitializeResourceDiagnosticsCore()
  symbol is absent. It is **not PASS**. Its unchanged directly invoked
  reserved-bank/stack-symbol/no-atomic components pass for both ELFs; its
  ASan/UBSan watermark component passes10000 fills and50000 scans.
- check_glyph_resource_diagnostics.py fails identically at its stale
  GLYPH_STRICT_HARDENING_CANDIDATE flag assertion. Root retained both raw logs;
  no checker or build gate was weakened.

These inherited checker applicability failures remain explicit framework debt,
separate from the finite exact resource result. No full checker/aggregate PASS,
physical acceptance, target timing or measured highwater is claimed. Hardware
display acceptance and Nunchuk remain NOT_TESTED. No device or Git operation was
performed by this resource specialist.
