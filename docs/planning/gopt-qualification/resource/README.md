# GOPT linked resource qualification

Source-only offline proof bundle. No ELF, BIN, map, UF2, device data, or disassembly is included. Qualification results describe model bounds on the named exact input, not measured hardware stack highwater. New candidate hardware acceptance remains separate.

## Reproduction

Use Python3 and the pinned ARM toolchain used for the actual Mk6 build. No special Python packages are required. All machine-specific locations are CLI arguments:

```sh
python3 compare.py \
  --repo "$GLYPH_REPO" \
  --source "$CANDIDATE_F" \
  --elf "$CANDIDATE_BUILD/firmware.elf" \
  --map "$CANDIDATE_BUILD/firmware.map" \
  --toolchain "$ARM_TOOLCHAIN_BIN" \
  --baseline-dir "$RETAINED_INTEGRATION_EVIDENCE" \
  --out "$RESOURCE_OUTPUT"
```

`CANDIDATE_F` is the full40-character commit matching the source inputs and ELF embedded identity. `GLYPH_REPO` contains that exact source, canonical history, and the retained ledger below. `ARM_TOOLCHAIN_BIN` holds arm-none-eabi-nm/objdump/size/readelf from the same pinned compiler. `RESOURCE_OUTPUT` is a fresh analysis-only directory outside the repository; scripts copy the supplied ELF/map there and generate linked evidence. Do not publish that output directory wholesale.

`RETAINED_INTEGRATION_EVIDENCE` must contain:

- `firmware.elf`: exact retained e07019b59f370e4853f0eac56de97d91bcea430e integration ELF, SHA2561c42f32ca4dcb18c54dcb591f64ed97d3372c99a51874f258e5f64d0dcdf52b2.
- `resource/functions.json`, `resource/summary.json`, and `resource/core1-bound-graph.json`: the matching retained linked records. Their digests are in SCRIPT_PROVENANCE.json.

The baseline ELF and graph are mandatory digest-checked inputs, not bundled firmware. The gzip ledger is already versioned at `docs/runtime_config/package_active_profile_display/resource/baseline-resource-source-predicate-ledger.json.gz` in the canonical repository. SCRIPT_PROVENANCE.json pins it and the source scripts. The original accepted0b9ef3af and canonical2bcb5104 active source paths compare equal; replay-accepted results additionally compare the actual accepted ELF's3301 linked function shapes with this retained integration inventory.

## Scope and fail-closed gates

The scripts extract every named linked frame, direct/tail/indirect shape, ELF sections and vtables. Only named GOPT loop/CRC/dashboard changes are admitted; other changed shapes, unexplained added/removed symbols, unknown core1 targets, new special-leaf shapes, a loop frame over32, static growth above198888, heap-capacity loss below63060, changed stack reservations, or failed route equations stop the run. The static ceiling remains199632; each stack reservation remains2048; core1 retained modeled budget remains1152.

The retained50 core0 equations are recomposed. CRC is checked separately through every current linked ancestor and its inline clones, including the synchronous migration-reader callback's actual ImportLegacyStream/ExecuteLegacyImport/PrepareImportedLegacyRecord frames. CRC branches use the unchanged accepted checked-I/O upper540 and conservative physical IRQ408 even in configurator contexts. Inlined wrapper frames must not increase, protecting their later hashing, raw-output, write and rename siblings. The noinline CRC overload gives the32-byte buffer a returned frame before callers resume those phases. New helper leaf shapes and source predicates remain review obligations.

Core1 uses the retained concrete display/graphics/LED object and callback union, source-pinned ROM/time/no-RTOS bounds and SIO IRQ68. The GOPT label helper can only invoke the same concrete SSD1306's Adafruit_GFX::write(unsigned char). Existing graphics descendants are fully composed. Loop and setup envelopes include outer wrappers16 and IRQ68. Directory I/O and visitor alternatives remain explicitly max-composed; the candidate does not change directory layout.

All unchanged shape/source/SDK/IRQ/ROM assumptions retain their original scope. The comparison does not assert arbitrary-mode, panic/corruption, RTOS or unsupported-device bounds, allocation success, physical highwater, electrical timing, Nintendo Switch console compatibility, gameplay, or Nunchuk acceptance. Source/dependency/artifact closure and host regression controls are separately required.

## Reliability disposition

No separate speculative GOPT-3 resource source group is recommended. The inherited lifecycle rename envelope has four bytes modeled margin; inherited legacy stage-write has zero. Neither a stack fault nor physical highwater has been reproduced. Safely improving those lower storage/transaction envelopes needs a broader proved lifetime or algorithm change. Do not add static/heap scratch merely to shorten a local frame. The CRC noinline lifetime boundary is a directly coupled GOPT-1 repair and is assessed against the final linked image. Candidate-specific host qualification and exact hardware gates remain required.

## Exact final result

F55739675e5706ea8799265c4221724ac4f2dce9b/tree87ad82c2302353d50325ff3b8445464b62fc92e9 passes the finite resource proof. Exact ELF53b53879b203ca2ef77de346352d1763cb89970560577fd3074a743a9eecfb0b and mapb53db2eeb9235f3930b3807ffc560b889f4c605ed5aaa86e7b1c88afece845ff are inputs only, not bundled.

Flash650484 is808 bytes smaller; static198888 and heap63060 are unchanged. All3301 named functions remain:3295 shapes unchanged and six expected CRC/dashboard changes. Core0 retained50-route maximum2048/lifecycle2044;42 current CRC ancestor routes max1556. Core1 setup968/loop984 +outer16 +IRQ68 =1068, unchanged and within1152. Dashboard renderer own frame grows48→64; its full conservative subtree grows768→784 but does not dominate the core1 envelope. CRC overload grows72→96; formerly inlined wrappers remain264 or reduce264→248 and272→264, protecting later sibling phases.

CANDIDATE_RESOURCE_SUMMARY.json, CORE0_ROUTES.json, CRC_CALLER_ROUTES.json, LINKED_GRAPH_DELTA.json, ACCEPTED_BASELINE_CONTROL.json and RESOURCE_SIGNOFF.json retain the exact signed-off derived results. The initial script review found an invalid two-argument startswith call; it was corrected before these final candidate/control runs. Seven injected unknown-edge/frame/symbol cases are all rejected, including known malloc inserted under CRC. ADVERSARIAL_CONTROLS.json records the results.

Reproduce adversarial controls after the normal comparator extracts the candidate graph:

```sh
python3 test_graph_gate.py \
  --baseline-functions "$RETAINED_INTEGRATION_EVIDENCE/resource/functions.json" \
  --candidate-functions "$RESOURCE_OUTPUT/resource/functions.json" \
  --output "$RESOURCE_OUTPUT/graph-gate-controls.json"
```

For the accepted baseline control, invoke compare.py with source0b9ef3afd1834ac7832871bca0651b67147840a2, its retained ELF/map and the additional `--baseline-control` flag. That flag only accepts the exact physical-source ELF SHA25643b3b7b0630d66d0b17266580e2cd6be0862cd9059694cf805b1c90d5b21fd1f. It bypasses only working-source equality with the accepted commit, since the current checkout holds F. It still verifies accepted-versus-canonical source equality, artifact digests, linked graphs and all model gates, and emits PASS_BASELINE_CONTROL instead of candidate PASS.
