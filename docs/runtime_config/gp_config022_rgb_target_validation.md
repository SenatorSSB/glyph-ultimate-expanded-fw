# C022 RGB target validation host proof

This is focused host evidence for the seven authorized C022 production paths.
It establishes no physical controller acceptance. Nunchuk remains NOT_TESTED;
root cause remains UNPROVEN.

The generic validator walks only populated RGB records after checking the outer
and every populated nested extent. The Glyph adapter obtains its domain from
the selected Mk6 pixel map: 76 pixels and 36 unique named physical targets. The
Glyph wrapper first preserves the existing C021 semantics and error order, then
rejects populated zero, unnamed and nonphysical RGB targets. Counts represent
absence. Duplicates, order, colors and gameplay eligibility are unchanged.

## Execution

The new checker exposes `run_host(root, temporary, negative_controls=True,
pins=None)` for explicit preparatory execution before the root-controlled
candidate freezes. Its command-line entry point authenticates the finite input
inventory before running. Output directories must be outside the repository.
Both coherent enum representations use actual generated C descriptors and
Nanopb C/C++ units, ASan, UBSan, enum and shift checks. Compiler versions,
commands, binary hashes, raw MMD files, dependency pins, run logs and mutant
outcomes are recorded outside the repository.

The retained C021 compiler, process, dependency and whole-application graph
infrastructure is reused. Original C021 harnesses and historical observations
remain unchanged. The new suites install the Glyph wrapper at the actual
Persistence callback, SET transaction and startup seams. Their RGB positives
use named physical targets.

## Matrix

- All 36 physical targets and all 24 other named IDs; zero and every raw byte;
  wide integer boundaries through representation-safe storage and real decoding.
- RGB outer counts 0/30/31, nested counts 0/60/61, first and last positions,
  malformed real wire data, unused poison, immutability, duplicates and order.
- Real CRC-checked load rejects without caller or stored-byte changes and
  follows with a successful recovery. Real SET rejects without a save or live
  publication and follows with successful save/load. Missing/conflicting
  callbacks remain fail closed.
- Whole `config.cpp` startup with both core schedules and working/failed
  display allocation. Invalid RGB and legacy counted zeros refuse normal
  constructors, RGB, reports, menu/transport and storage writes permanently.
- Exact source-default delta: ordinal block 11 count 20 to 11 and explicit LF1
  black; all other source bytes and all 12 other RGB blocks remain identical.
- Actual NeoPixel consumer with current generated types: static, SHIFT and
  XWAVE outputs are unchanged by validation. Legacy and corrected block 11
  produce identical 60 static slots and 76 pixel outputs. Count-only cyan is a
  separate appearance counterexample. The HSV packing is a host stub and
  cannot establish physical FastLED color conversion.
- Archived owner Config is historical evidence. Its expected nine trailing
  empty RGB records reject; the minimal in-memory repair accepts while all
  unrelated fields remain identical. It is not a fresh backup or recovery test.
- Source, pin, mode, omission, type and count controls plus compiled callback,
  target-walk, extent and startup mutants must reject.

## Offline raw validation

The decoder binary accepts `--config-raw <file>`. It reads a raw Config payload,
decodes it with the real schema/Nanopb and invokes the exact Glyph wrapper.
Stdout is JSON with `accepted`, `decoded` and `error`. Exit 0 means accepted;
exit 1 means decoded but semantically rejected; exit 2 means decode failure.
Expected rejection emits no stderr. The execution report pins the binary and
all source dependencies. It performs no filesystem persistence or device write.

Fresh owner backup, exact codec roundtrip, offline minimal correction and
restoration artifacts, independent review, exact committed target build/custody
and the grouped physical block-11 matrix remain separate gates.

## Focused preparatory result

Both enum ABIs pass: 534 short / 539 ordinary pure validation cases; 538 real
decoder cases; 827 actual checked-load cases; 1139 actual SET cases plus a fresh
missing-callback process; 68 whole-startup schedules; 11 consumer executions.
All 16 compiled behavior mutants reject. The archive passes real decode and
C021 base semantics, rejects for the expected RGB target defect, and accepts
the minimal in-memory correction. The two-field undo reproduces the entire
original decoded object byte for byte. The finite input identity controls are
recorded separately in the final execution report.

Preparatory attempts 1–7 include compilation/integration failures and an
initial ineffective nested-extent mutant control. Attempt 8 added direct generic
helper extent coverage and passed; attempt 9 adds archived raw validation and
first/last malformed decoding and passes. These are implementation-stage host
failures and repairs; no firmware build or physical test occurred.
