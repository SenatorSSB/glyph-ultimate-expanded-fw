# Phase 7A Activation Failure Root-Cause Analysis

status: ROOT_CAUSE_ANALYSIS_ONLY_NO_FIX_IMPLEMENTED

failed branch:
`phase7a-runtime-config-compiled-payload-activation`

failure result branch:
`phase7a-runtime-config-compiled-payload-activation-hardware-failure`

known-good baseline branch:
`phase7a-build-size-and-map-baseline`

current known-good restore branch:
`configurator`

exact failure report:
`I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection from the controller. At least pressing rf5 or rf6 disconnect it according to the game console`

exact recovery report:
`i restored the previous fw, which works fine still`

## Scope

This packet is analysis-only. It does not implement a firmware fix, does not
modify firmware source, does not change parser/runtime activation, does not add
storage, does not add WebSerial/device write, and does not add flashing
automation.

The low-level disconnect mechanism is unknown. The evidence supports isolation
to the failed activation branch because the user restored the previous
configurator firmware and reported that it still works fine. The evidence does
not prove a precise crash, watchdog, USB, stack, heap, timing, or report-level
cause.

## Refs Inspected

| Ref | Status | Short SHA |
| --- | --- | --- |
| `configurator` | inspected as `origin/configurator` | `39cd246` |
| `phase7a-runtime-config-parser-offline-and-compiled-scaffold` | inspected as `origin/phase7a-runtime-config-parser-offline-and-compiled-scaffold` | `9993d07` |
| `phase7a-runtime-config-compiled-payload-activation` | inspected as `origin/phase7a-runtime-config-compiled-payload-activation` | `94b4295` |
| `phase7a-runtime-config-compiled-payload-activation-hardware-failure` | inspected as `origin/phase7a-runtime-config-compiled-payload-activation-hardware-failure` | `4a4bb59` |
| `phase7a-runtime-config-activation-repair-minimal` | inspected as `origin/phase7a-runtime-config-activation-repair-minimal` | `cb9df4c` |
| `phase7a-build-size-and-map-baseline` | inspected as `origin/phase7a-build-size-and-map-baseline` | `2ed1a55` |

No required ref was missing.

## Source And Diff Analysis Commands

- `git diff --name-status origin/configurator..origin/phase7a-runtime-config-compiled-payload-activation`
- `git diff --stat origin/configurator..origin/phase7a-runtime-config-compiled-payload-activation`
- `git diff --name-status origin/phase7a-runtime-config-parser-offline-and-compiled-scaffold..origin/phase7a-runtime-config-compiled-payload-activation`
- `git diff --name-status origin/configurator..origin/phase7a-runtime-config-activation-repair-minimal`
- `git diff --name-status origin/phase7a-build-size-and-map-baseline..origin/phase7a-runtime-config-compiled-payload-activation`
- `git diff --unified=80 ... -- src/modes/Ultimate.cpp src/modes/UltimateRuntimeConfigParser.hpp src/modes/UltimateRuntimeConfigCompiledPayload.hpp`
- Required `rg` search over `src docs tools scripts platformio.ini`

## Changed Firmware Files In Failed Branch

Compared with `configurator`, the failed activation branch changed exactly these
firmware source-visible paths:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigParser.hpp`
- `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`

No `HAL/`, `include/`, `lib/`, `config/`, or `platformio.ini` path changed in
the failed activation branch diff against `configurator`.

Compared with `phase7a-runtime-config-parser-offline-and-compiled-scaffold`, the
failed activation branch made the same source-visible activation delta in:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigParser.hpp`
- `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`

Compared with `configurator`, the minimal repair branch changed no firmware
source files. It added docs/tooling only and chose Option A, leaving firmware
source unchanged.

## Exact Failed-Branch Deltas

### `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`

The failed activation branch added a new compiled payload header containing:

- `kPhase7ACompiledPayloadFixturePath`
- `kPhase7ACompiledPayloadSha256`
- `kPhase7ACompiledPayloadSize = 530`
- `constexpr uint8_t kPhase7ACompiledPayload[530]`
- a `static_assert` that the declared size matches the array size

Source-visible effect:

- adds 530 payload bytes plus metadata strings to the compiled image;
- adds a new header include target;
- does not add storage, transport, WebSerial, runtime config write, or flashing
  source paths.

### `src/modes/UltimateRuntimeConfigParser.hpp`

The failed activation branch did not materially change parser logic compared
with the scaffold branch. It changed comments from "compiled scaffold only" and
"Not runtime-active" to "Source-owned compiled/test payload activation only".

Source-visible effect:

- parser code was already present in the scaffold baseline;
- activation made the existing parser callable from `Ultimate.cpp`;
- comments no longer described an inert runtime path.

### `src/modes/Ultimate.cpp`

The failed activation branch added:

- `#include "modes/UltimateRuntimeConfigCompiledPayload.hpp"`
- a static assertion connecting compiled payload size to parser payload size;
- a global namespace-scope parse result:
  `const UltimateRuntimeConfigParser::ParseResult kPhase7ACompiledPayloadParseResult =
  UltimateRuntimeConfigParser::ParseUltimateRuntimeConfigPayload(...)`
- `ResolveActiveRuntimeConfig()`, which checks
  `kPhase7ACompiledPayloadParseResult.status == ParseStatus::Ok` and
  `ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)`;
- replacement of the local analog-path runtime-config selection with
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`

The failed activation branch did not source-visibly change:

- RF5/RF6 digital button mapping expressions;
- `UpdateDirections(...)` arguments;
- RF6 Z-airdodge override body;
- RF7 hard-Up+B override body;
- C-stick ASDI override body;
- trigger analog assignment logic;
- nunchuk override logic;
- GameCube/N64/backend report packing source.

## Size And Artifact Evidence

The known-good build-size baseline branch records `configurator` lineage
artifacts:

| Artifact | Size bytes | SHA-256 |
| --- | ---: | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | 791552 | `bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085` |
| `.pio/build/glyph_mk6/firmware.elf` | 5407148 | `dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83` |
| `.pio/build/glyph_mk6/firmware.bin` | 395664 | `4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45` |

No failed-activation branch firmware artifact metadata was found in the branch
tree. Therefore a baseline-vs-failed artifact size/hash comparison is
unavailable from recorded branch evidence. The source diff still proves added
compiled payload bytes and additional parser/resolver code reachability.

## RF5/RF6 Source-Path Analysis

This section is source-path analysis only. It does not infer physical mapping
semantics beyond source names and expressions.

### RF5

Known-good `src/modes/Ultimate.cpp` source shows RF5 participates in:

- forced-Up resolution: `state.force_up_active = inputs.rf5 || ...`
- effective Up: `state.up = inputs.lf2 || state.force_up_active`
- Up+A role input: `const bool up_a_active = inputs.rf5`
- digital A carrier: `outputs.a = base_rf1_a_active || inputs.lt6 || inputs.rf5`
- direction-plus-A activation and forced-Up direction selection:
  `state.direction_plus_a_active = down_a_active || up_a_active` and
  `state.direction_plus_a_force_up = ...`
- analog table/direction path through `UpdateAnalogOutputs(...)`,
  `UpdateDirections(...)`, `ApplyTableAnalogOutput(...)`, and
  `ApplyDirectionPlusAOverride(...)`

Implication:

- RF5 is both a digital-output path and a left-stick analog-path trigger in the
  known-good source.
- The failed activation branch did not alter RF5 expressions directly.
- Because RF5 exercises the analog runtime-config reference through table lookup
  and direction-plus-A lookup, it is implicated in the changed resolver/reference
  path indirectly.

### RF6

Known-good `src/modes/Ultimate.cpp` source shows RF6 participates in:

- role state: `state.z_airdodge_override_active = inputs.rf6`
- digital output: `outputs.buttonR = inputs.rf6`
- analog override branch:
  `if (roles.z_airdodge_override_active) { ApplyZAirdodgeOverride(runtime_config, effective_directions, outputs); }`
- low-magnitude table lookup inside `ApplyZAirdodgeOverride(...)` through
  `LookupRuntimeStickPoint(runtime_config, RuntimeTableId::Lt1LowMagnitude, ...)`

Implication:

- RF6 is both a digital-output path and an analog low-magnitude table lookup
  path in the known-good source.
- The failed activation branch did not alter RF6 expressions directly.
- Because RF6 calls `ApplyZAirdodgeOverride(...)` using the active runtime-config
  reference, it is implicated in the changed resolver/reference path indirectly.

### Output Report Shape And Backend Behavior

Known-good `include/core/state.hpp` defines digital output fields and six analog
axes: left stick, right stick, and analog triggers. Known-good
`HAL/pico/src/comms/GamecubeBackend.cpp` packs `buttonR` as `z`, trigger
digital and analog fields, left stick, and c-stick fields into the report.

The failed activation branch source diff does not change `include/core`,
`HAL/`, backend report packing, backend IDs, USB transport code, or output
struct shape. Any USB/backend disconnect explanation is therefore indirect and
unproven from source diff alone.

## Required Analytical Questions

### 1. Exactly what firmware changes existed in the failed branch?

The source-visible firmware changes were the compiled payload header, a
non-`constexpr` global parse result initialized by calling
`ParseUltimateRuntimeConfigPayload(...)`, the `ResolveActiveRuntimeConfig()`
wrapper, and replacing local analog-path validation with that wrapper.

### 2. Which changes were absent from known-good configurator?

All activation-specific items were absent from known-good `configurator`:

- no compiled payload header;
- no compiled payload include in `Ultimate.cpp`;
- no global parse result;
- no parser call during namespace-scope initialization;
- no `ResolveActiveRuntimeConfig()` wrapper;
- no analog-path dependency on a compiled payload parse result.

### 3. Which changes affect specific risk areas?

| Risk area | Source-backed impact |
| --- | --- |
| static/global initialization | yes: global `kPhase7ACompiledPayloadParseResult` calls parser logic before ordinary runtime use |
| flash/rodata size | yes: added 530-byte payload array plus strings and reachable code |
| RAM/BSS/data size | plausible: global `const ParseResult` may occupy static storage depending on toolchain placement; exact map unavailable |
| per-frame analog path | yes: analog path calls `ResolveActiveRuntimeConfig()` and checks global parse status before returning the view |
| RF5/RF6 paths | indirect: RF5/RF6 use analog runtime-config lookups, but their direct expressions did not change |
| output report shape | no source-visible change |
| USB/backend behavior indirectly | plausible only; no backend source changed |

### 4. Did the failed branch introduce the named patterns?

| Pattern | Result |
| --- | --- |
| compiled payload header | yes |
| global non-`constexpr` parse result | yes |
| parser call during static initialization | yes, source-visible namespace-scope initializer |
| new runtime resolver | yes, `ResolveActiveRuntimeConfig()` |
| changed active runtime-config reference lifetime | source-visible selection changed from local conditional expression to function-returned reference; both return static views |
| larger binary/static data | source-visible larger image input; exact binary size unavailable |
| extra per-frame validation or parser work | per-frame resolver status check and validation remain; parser work is global init, not per-frame |
| source-visible storage/write/transport path | no |

### 5. Which hypotheses are evidence-backed and which are only plausible?

H1 through H3 are source-backed as introduced risks, but not proven root causes.
H4 is source-backed for parser execution but plausible-low as the disconnect
mechanism. H5 is source-backed for RF5/RF6 path implication but not for a direct
bug in those paths. H6 remains plausible-low because embedded memory/layout or
timing interactions can be exposed without a direct RF5/RF6 logic change, but no
specific latent mechanism is proven.

### 6. What minimum diagnostic builds would isolate cause without repeating the failed pattern blindly?

Use the diagnostic matrix in
`docs/runtime_config/phase7a_activation_failure_diagnostic_build_matrix.md`.
Start with D0/D1 controls, then isolate compiled payload bytes (D2), global
parse result (D3), resolver/codegen (D4), explicit non-static parse (D5), and
only reproduce the failed branch (D6) if necessary and operator-approved.

## Ranked Hypotheses

### H1. Global/static initialization risk

confidence: source-backed-medium

Evidence for:

- Failed branch introduced global `kPhase7ACompiledPayloadParseResult`.
- Its initializer calls `ParseUltimateRuntimeConfigPayload(...)` at
  namespace-scope initialization time.
- This was absent from known-good `configurator` and from the inert parser
  scaffold.
- Embedded startup order and static initialization are higher-risk than an
  explicit application-controlled initialization point.

Evidence against:

- The parser inputs are a fixed 530-byte `constexpr` array and fixed size.
- Source inspection does not show storage, USB, backend, or device-write access
  from the parser.
- The hardware report identifies RF5/RF6-triggered disconnect, not a guaranteed
  boot failure.

Conclusion:

- H1 is the strongest source-backed risk pattern, but the exact disconnect cause
  is not proven.

Next diagnostic:

- D3: include payload and global parse result, but do not use it in the runtime
  resolver.

### H2. Static image/layout/size risk

confidence: source-backed-medium

Evidence for:

- Failed branch added a 530-byte compiled payload plus string metadata and made
  parser/resolver code reachable from firmware.
- Build-size baseline exists for known-good `configurator` artifacts.
- Failed activation artifact metadata is unavailable, so size/layout delta was
  not recorded.

Evidence against:

- No failed artifact size, map, or memory section report is available.
- A 530-byte source addition alone does not prove image/layout failure.

Conclusion:

- H2 is source-backed as a risk area but not proven as the root cause.

Next diagnostic:

- D2: compiled payload header only, with no parse call and no resolver.

### H3. Runtime resolver/reference path risk

confidence: source-backed-medium

Evidence for:

- Failed branch introduced `ResolveActiveRuntimeConfig()`.
- `UpdateAnalogOutputs(...)` changed from a local conditional reference binding
  to a function-returned reference.
- RF5/RF6 both exercise analog runtime-config lookup paths.

Evidence against:

- The resolver still returns either `kSourceOwnedCurrentBaselineRuntimeConfig` or
  `kKnownGoodRuntimeConfig`, both static views already present in source.
- No source-visible output report shape or backend report packing changed.
- The resolver does not parse per frame.

Conclusion:

- H3 is source-backed as a changed hot-path/codegen pattern, but not proven as
  the low-level disconnect cause.

Next diagnostic:

- D4: runtime resolver only around the existing source-owned view, with no
  payload and no parser call.

### H4. Parser CRC/loop risk

confidence: plausible-low

Evidence for:

- Failed branch calls parser logic on the compiled payload.
- Parser includes a CRC loop over payload bytes and validation loops over order
  data.
- That parser call was absent from known-good `configurator`.

Evidence against:

- Source shows the parser call occurs in the global initializer, not directly in
  RF5/RF6 per-frame handling.
- Parser code does not source-visibly access hardware, storage, USB, or backend
  transport.
- No stack/heap/watchdog/USB evidence is available.

Conclusion:

- H4 is plausible but lower confidence than H1/H2/H3.

Next diagnostic:

- D5: local explicit parse at a controlled startup or cold path, not static init
  and not hot analog path.

### H5. RF5/RF6-specific output path interaction

confidence: source-backed-medium

Evidence for:

- User report names RF5 and RF6 as inputs that disconnect according to the game
  console.
- RF5 source path triggers forced-Up, digital A, direction-plus-A, and analog
  runtime-config lookup.
- RF6 source path triggers digital `buttonR`/Z and the low-magnitude
  Z-airdodge analog lookup.
- Both RF5 and RF6 can exercise analog table lookup using the active
  runtime-config reference.

Evidence against:

- Failed branch did not directly change RF5/RF6 expressions.
- Backend report packing and `OutputState` shape did not change.
- Source does not prove an RF5/RF6-specific crash mechanism.

Conclusion:

- H5 is source-backed for path implication, not for direct RF5/RF6 logic fault.

Next diagnostic:

- D4 plus hardware matrix rows that separately press RF5, RF6, ordinary
  directions, neutral, and non-implicated buttons.

### H6. Latent unrelated interaction

confidence: plausible-low

Evidence for:

- Embedded firmware can expose latent layout/timing/static initialization issues
  when code/data changes, even without direct logic edits to the failing input
  expressions.
- The failed activation branch changed code reachability and static data.

Evidence against:

- No specific latent memory, timing, USB, watchdog, stack, heap, or backend
  failure evidence has been recorded.
- Current `configurator` firmware works after restore.

Conclusion:

- H6 remains a caveat, not a proven root cause.

Next diagnostic:

- Compare artifact sizes and, if available on a future diagnostic branch, map
  sections for each D0-D6 build before hardware testing.

## Conclusion

Root cause is not proven. The strongest source-backed risks are the global
non-`constexpr` parse result/static initialization pattern, static image/layout
change from the compiled payload and reachable parser code, and the resolver
wrapper in the hot analog path. RF5/RF6 are implicated by source because they
exercise analog runtime-config lookup paths, but their direct source expressions
and backend report packing did not change.

The failed activation branch must remain abandoned and must not merge. The next
step must be controlled diagnostic builds with artifact metadata and hardware
gates, not direct repair and not direct continuation from the failed pattern.

## No-Fix And Non-Claims

- No fix is implemented on this branch.
- No firmware source is modified on this branch.
- No runtime behavior change is implemented on this branch.
- No hardware-pass claim is made.
- No nunchuk-validation claim is made.
- No runtime-loaded config is implemented.
- No runtime-config storage is implemented.
- No WebSerial/device write is implemented.
- No firmware flashing automation is implemented.
- No definite low-level disconnect mechanism is claimed.
