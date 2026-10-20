# M1 design and resource freeze

Status: DESIGN_RESOURCE_FREEZE_COMPLETE. Implementation is not authorized by
this research record; complete independent canonical READY adoption is next.

The fresh exact baseline at `976ba2195b72046b32f7ecdd41063e7bad791ded`
passed the owner-terminal fallback build in 832.87 seconds: RAM187344/262144,
flash477452/1568768. [Build/custody record](baseline_build.json),
[full successful log](baseline_build_success.log), and
[actual linker symbols](baseline_linker_symbols.txt) bind the result. The UF2
is baseline-only and has no native or new physical acceptance.

The actual build resolved Nanopb0.4.92. [Production ABI reconciliation](production_abi_reconciliation.md)
reproduced its exact descriptors and confirms zero baseline/proposed ABI or
owner/view/frame-layout drift from the earlier explicitly historical0.4.91
probes. [Current unmodified oracle reconciliation](current_oracle_reconciliation.md)
passes StageA/B/C in both enum ABIs and complete GP-BIND-003. Frozen source and
oracle hashes remain exact. No old partial result is retroactively changed.

The independent architecture review permits this mechanical closure without
a new review loop. Its corrected design/protocol/codec hashes are unchanged.
The known8256-byte added-static layout projects195600 bytes total; the reviewed
12-KiB added-static cap yields199632, leaving62512 of main RAM. The native
7792-byte active/candidate workspace remains below7800. The actual linker
reserves2048 bytes for each core stack in scratch RAM; these reservations,
partition/reserve/store limits are unchanged. Arithmetic is feasibility evidence,
not a native whole-program stack/timing or controller PASS.

The exact normative caps and evidence hashes are in [m1_freeze.json](m1_freeze.json).
Native final build/stack/interrupt composition, polling and activation cost, full
independent semantic/converter proof, twenty complete-profile LittleFS lifecycle,
source review, exact candidate custody and approved physical acceptance remain
mandatory M2–M7 gates. No script/SOCD/coordinate/store redesign, wider transport
or protected budget increase is introduced.
