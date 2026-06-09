# Phase 7A Activation Failure Diagnostic Build Matrix

status: DIAGNOSTIC_PLAN_ONLY_NOT_IMPLEMENTED

purpose:
isolate the Phase 7A compiled-payload activation hardware failure cause with
controlled hardware-tested diagnostic builds.

warning:
diagnostic branches are not merge candidates into `configurator`. Each branch is
evidence-producing only until artifact metadata and hardware result evidence
support a merge/discard decision.

## Global Rules

- No diagnostic branch may implement storage, runtime-config write, WebSerial,
  device write, or firmware flashing automation.
- No diagnostic branch may claim nunchuk validation unless nunchuk rows are
  explicitly tested and recorded.
- No diagnostic branch may claim hardware pass until a hardware result branch
  records that result.
- Each diagnostic branch must record build artifact metadata before hardware
  testing.
- Each diagnostic branch must use an explicit branch name and result branch.
- Each diagnostic branch must be discarded or separately reviewed before any
  merge consideration.

## Required Per-Diagnostic Evidence

- explicit branch name;
- exact base ref;
- exact source delta;
- build command;
- `.uf2`, `.elf`, and `.bin` size/hash metadata when available;
- map/section metadata when available;
- hardware result branch before merge/discard decision;
- nunchuk status: `NOT_TESTED` unless explicitly tested;
- no storage/write/WebSerial/flashing source changes.

## Proposed Diagnostic Builds

### D0 baseline

Branch:
`phase7a-diagnostic-d0-configurator-baseline`

Purpose:
current `configurator` build control.

Expected source delta:
none.

Notes:
already known-good by user restore report and build-size baseline, but can be
re-recorded as a fresh control if needed.

Required artifact:
known-good `.uf2`, `.elf`, and `.bin` metadata.

Hardware gate:
optional control run before D2-D6.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D1 parser scaffold only

Branch:
`phase7a-diagnostic-d1-parser-scaffold-only`

Purpose:
confirm the inert parser scaffold is not the trigger.

Expected source delta:
match the current known-good parser scaffold if already merged into
`configurator`; no compiled payload header, no global parse result, and no
runtime resolver.

Required artifact:
build metadata compared with D0.

Hardware gate:
required before treating parser scaffold as safe for future runtime-active work.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D2 compiled payload header only

Branch:
`phase7a-diagnostic-d2-compiled-payload-header-only`

Purpose:
isolate static image/rodata/layout effect from the compiled payload bytes.

Expected source delta:
add compiled payload bytes/header, but do not parse it and do not include a
runtime resolver.

Required artifact:
build metadata and size/map comparison against D0/D1.

Hardware gate:
required before proceeding to D3.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D3 global parse result only

Branch:
`phase7a-diagnostic-d3-global-parse-result-only`

Purpose:
isolate static initialization and parser-call effect.

Expected source delta:
include payload and global parse result, but do not use the parse result in a
runtime resolver and do not alter `UpdateAnalogOutputs(...)` active config
selection.

Required artifact:
build metadata and size/map comparison against D2.

Hardware gate:
required before any future global/static initialization pattern is considered.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D4 runtime resolver only

Branch:
`phase7a-diagnostic-d4-runtime-resolver-only`

Purpose:
isolate resolver/reference/codegen effect.

Expected source delta:
add resolver wrapper around the same existing source-owned runtime-config view,
with no compiled payload and no parser call.

Required artifact:
build metadata and size/map comparison against D0/D1.

Hardware gate:
required before using resolver wrappers in runtime-active work.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D5 local explicit parse at controlled startup or cold path

Branch:
`phase7a-diagnostic-d5-explicit-controlled-parse`

Purpose:
if needed, isolate global-init behavior from explicit initialization behavior.

Expected source delta:
parse in an explicit function not in static initialization and not in the hot
analog path. This is diagnostic only and must not implement storage/write or
runtime-loaded user config.

Required artifact:
build metadata and size/map comparison against D2/D3.

Hardware gate:
required before any future explicit parser activation proposal.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

### D6 failed branch reproduction

Branch:
`phase7a-diagnostic-d6-failed-branch-reproduction`

Purpose:
reproduce the original failure only if necessary and operator-approved.

Expected source delta:
original failed activation pattern isolated to a diagnostic branch.

Required artifact:
build metadata and size/map comparison against D0-D5.

Hardware gate:
required and must be recorded on a result branch. This branch is not a merge
candidate even if reproduction does not occur.

Nunchuk:
`NOT_TESTED` unless explicitly tested.

## Recommended Sequence

1. D0: confirm control artifact metadata.
2. D1: confirm parser scaffold remains inert.
3. D2: isolate payload/static image effect.
4. D4: isolate resolver/reference/codegen effect without parser/payload.
5. D3: isolate global parse result and static initialization only after D2.
6. D5: compare explicit controlled parse against D3 if parser activation remains
   worth investigating.
7. D6: reproduce failed branch only if needed, explicitly approved, and isolated
   from merge candidates.

## Non-Claims

- No diagnostic build is implemented by this plan.
- No firmware fix is implemented.
- No hardware-pass claim is made.
- No nunchuk-validation claim is made.
- No runtime-loaded config is implemented.
- No runtime-config storage is implemented.
- No WebSerial/device write is implemented.
- No firmware flashing automation is implemented.

## D5A-N2 Result Update

- D5A-N2 hardware result recorded.
- Result source: user-reported
- Exact user report text: `flashed n2. It works. No disconnects anymore.`
- Diagnostic branch tested:
  `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read`
- Result branch:
  `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read-hardware-result`
- RF5/RF6/LT6 disconnects were not observed.
- D5A-N2 passed.
- The parse-status hot-path read/branch on
  `kPhase7AD3GlobalParseResult.status` is the likely trigger.
- The low-level root cause mechanism is not proven.
- Failed activation branch must not merge.
- Future runtime activation must not read parser result state from
  UpdateAnalogOutputs(...) or analog hot-path resolver.
- Nunchuk: NOT_TESTED
