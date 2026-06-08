# Phase 7A Compiled Activation Failure Analysis

status: FAILURE_ANALYSIS_ONLY_NO_FIX_IMPLEMENTED

This packet analyzes the user-reported hardware failure from the Phase 7A
compiled/test runtime-config payload activation branch. It is static/source/diff
analysis only. It does not implement a fix, modify firmware source, create a new
firmware build path, or record a hardware pass.

## Branches

- baseline branch: `configurator`
- inert scaffold branch:
  `phase7a-runtime-config-parser-offline-and-compiled-scaffold`
- failed branch:
  `phase7a-runtime-config-compiled-payload-activation`
- failure result branch:
  `phase7a-runtime-config-compiled-payload-activation-hardware-failure`
- recommended next branch:
  `phase7a-runtime-config-activation-repair-minimal`

`configurator` contains the Phase 7A offline parser foundation and inert
compiled parser scaffold. The scaffold branch is already merged into
`configurator`, so the analysis baseline is the current `configurator` branch.
The failed activation branch must not merge.

The activation branch currently includes the hardware-failure result by merge.
The separate failure-result ref remains available as the source of the original
failure packet.

## User Reports

- exact user failure report: I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection from the controller. At least pressing rf5 or rf6 disconnect it according to the game console
- exact recovery report: i restored the previous fw, which works fine still
- tested baseline status: configurator restored and works fine

Interpretation:

- `configurator` remains the known-good baseline for this report.
- The failure is isolated to the Phase 7A compiled-payload activation branch by
  the recovery report.
- The exact low-level disconnect cause is unknown.
- No firmware crash mechanism is inferred as fact.

## Source And Diff Inputs

Inspected `configurator` files:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `src/modes/UltimateRuntimeConfigParser.hpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `docs/runtime_config/phase7a_runtime_config_parser_offline_and_compiled_scaffold.md`
- `tools/check_glyph_runtime_config_firmware_parser_scaffold.py`

Inspected failed activation files from
`phase7a-runtime-config-compiled-payload-activation`:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`
- `src/modes/UltimateRuntimeConfigParser.hpp`
- `docs/runtime_config/phase7a_runtime_config_compiled_payload_activation.md`
- `tools/check_glyph_runtime_config_compiled_payload_activation.py`

Inspected hardware-failure files from
`phase7a-runtime-config-compiled-payload-activation-hardware-failure`:

- `docs/calibration/glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.md`
- `docs/calibration/fixtures/glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.json`
- `tools/check_glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure.py`

The requested repository search was run for RF5/RF6, runtime parser, runtime
lookup, z-airdodge, hard-Up+B, nunchuk, static/global, and activation symbols.

## Firmware Diffs Summarized

Compared with `configurator`, the failed activation branch made these relevant
firmware-runtime changes:

- compiled payload header added:
  `src/modes/UltimateRuntimeConfigCompiledPayload.hpp`
- `Ultimate.cpp` includes that header in the anonymous namespace:
  failed branch `src/modes/Ultimate.cpp:17`
- static size alignment against the 530-byte parser payload was added:
  failed branch `src/modes/Ultimate.cpp:25-28`
- global parse result added:
  failed branch `src/modes/Ultimate.cpp:30-34`
- `ResolveActiveRuntimeConfig` was added:
  failed branch `src/modes/Ultimate.cpp:249-258`
- `Ultimate::UpdateAnalogOutputs` changed from a direct
  `ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)` ternary
  to `ResolveActiveRuntimeConfig()`:
  `configurator` `src/modes/Ultimate.cpp:465-467`; failed branch
  `src/modes/Ultimate.cpp:487`
- the runtime path now depends on the compiled payload parse result status:
  failed branch `src/modes/Ultimate.cpp:251`
- payload-backed lookup was deferred by design; the failed activation doc says
  the runtime still uses the source-owned current baseline view when validation
  passes
- runtime table and stick-point lookups still use the selected
  `RuntimeConfigView`, including `LookupRuntimeStickPoint` and
  `ApplyZAirdodgeOverride`
- RF5/RF6 logic itself was not materially rewritten; those paths now consume
  the resolver-selected `runtime_config` in analog lookup/override paths
- new static data includes at least the 530-byte compiled payload, fixture path
  string, SHA string, and file-scope `ParseResult`

The activation branch also changed parser comments from "not runtime-active" to
"source-owned compiled/test payload activation only". The parser still did not
add storage reads, storage writes, WebSerial, device-write commands, or flashing
automation.

## RF5/RF6 Implicated Paths

RF5 is source-confirmed as a forced-Up and direction-plus-A path in
`Ultimate.cpp`:

- `state.force_up_active = inputs.rf5 ...` in `configurator`
  `src/modes/Ultimate.cpp:121`
- `const bool up_a_active = inputs.rf5;` in `configurator`
  `src/modes/Ultimate.cpp:133`
- `outputs.a = ... inputs.rf5;` in `configurator`
  `src/modes/Ultimate.cpp:183`
- `UpdateDirections(... effective_directions.up ...)` documents the Up input as
  `RF5, LT2+RF2, and LF4+RF3 forced-Up` in `configurator`
  `src/modes/Ultimate.cpp:470-475`

RF6 is source-confirmed as a z-airdodge / low-magnitude override path and also a
digital `buttonR` carrier in `Ultimate.cpp`:

- `state.z_airdodge_override_active = inputs.rf6;` in `configurator`
  `src/modes/Ultimate.cpp:167`
- `outputs.buttonR = inputs.rf6;` in `configurator`
  `src/modes/Ultimate.cpp:189`
- the analog priority comment identifies `RF6 low magnitude` in `configurator`
  `src/modes/Ultimate.cpp:486-487`
- `ApplyZAirdodgeOverride(runtime_config, effective_directions, outputs)` is
  called when that role is active in `configurator`
  `src/modes/Ultimate.cpp:513-515`

These are source-backed path identifications only. They do not prove why the
console reported a disconnect.

## Ranked Hypotheses

1. Global/static initialization or const parse-result memory/runtime
   interaction.

   Classification: plausible but unproven. Confidence: medium.

   Evidence for: the activation branch adds a namespace-scope
   `const UltimateRuntimeConfigParser::ParseResult
   kPhase7ACompiledPayloadParseResult` initialized by calling
   `ParseUltimateRuntimeConfigPayload` over the compiled payload before runtime
   use. The parse path calls non-`constexpr` parser/CRC code, so this introduces
   dynamic startup initialization rather than pure compile-time validation.
   `ResolveActiveRuntimeConfig` then checks that global result during the analog
   output path. Because `ParseStatus::Ok` is the zero enum value in the parser,
   skipped or disrupted dynamic initialization would be a risk pattern to rule
   out; this is a risk note, not a claim that it happened.

   Evidence against / limits: the parser function is side-effect-free by source
   inspection, the parse result is small, and no direct mutation or storage
   access is present. No obvious parser bounds issue was found in static review:
   the parser checks null, length, exact payload length, table IDs, duplicates,
   and checksum before success. No boot log, debugger trace, disassembly,
   map-file delta, stack trace, or watchdog evidence is available.

   Proposed next check: avoid a persistent global runtime `ParseResult` in the
   next implementation attempt, or prove the object placement and initialization
   with map-file/build inspection before any hardware activation.

2. Static memory/layout pressure from the 530-byte compiled payload or parser
   code.

   Classification: plausible but unproven. Confidence: medium.

   Evidence for: the activation branch adds a 530-byte compiled payload array,
   parser activation, and associated code/data into firmware. Embedded USB
   controller failures can be sensitive to memory layout or budget pressure, but
   this is an inference and not a diagnosis.

   Evidence against / limits: no source evidence shows out-of-bounds access,
   no memory budget report was inspected in this branch, and no build/map
   artifact proves RAM/flash pressure or USB descriptor/report corruption.

   Proposed next check: compare firmware size/map output between `configurator`
   and a minimal activation probe before hardware testing, without changing
   output behavior.

3. Activation boundary changed lifetime/reference behavior.

   Classification: plausible but unproven. Confidence: low.

   Evidence for: `UpdateAnalogOutputs` changed from selecting the source-owned
   view directly to calling `ResolveActiveRuntimeConfig`. That new boundary
   returns a reference based on a parser status gate. Pointer/view lifetime
   remains an important repair-branch risk to control if a later branch decodes
   payload bytes into table buffers.

   Evidence against / limits: both returned references point at existing
   static runtime config views, and the source-owned view is still used when
   validation passes. The diff does not show payload-backed table lifetime or
   pointer ownership.

   Proposed next check: keep the runtime view selection identical to
   `configurator` until a compile-time or explicit one-shot validation path is
   proven safe.

4. Parser validation path triggered unexpected embedded-runtime behavior.

   Classification: plausible but unproven. Confidence: low.

   Evidence for: the parser path is newly active in firmware, and its result
   now gates active runtime-config selection.

   Evidence against / limits: the parser result is computed globally, not per
   RF5/RF6 press; source inspection does not show parser mutation, storage, or
   output-path side effects. The RF5/RF6 symptom may be an interaction with
   affected analog paths rather than parser execution at button press time.

   Proposed next check: prefer host/build-time equivalence checks or a
   compile-time diagnostic before any runtime parser gate is used in the output
   path.

5. Unrelated but activation-branch-specific interaction.

   Classification: unknown. Confidence: low.

   Evidence for: the recovery report makes the regression branch-specific, and
   the activation branch contains both firmware and docs/tooling changes.

   Evidence against / limits: no hardware instrumentation isolates RF5/RF6
   disconnect to a specific low-level mechanism. The analysis has no proof that
   any one activation diff line caused the disconnect.

   Proposed next check: abandon the failed branch and reintroduce activation
   ideas only through a minimal branch with one bounded change, build artifact
   identity, and a hardware gate.

## Recommended Next Strategy

- Abandon the failed activation branch.
- Do not continue implementation directly from it.
- Create a new safe branch from `configurator`.
- Prefer a minimal runtime probe or compile-time-only parser diagnostics before
  activation.
- Avoid a global non-`constexpr` parse result if possible.
- Avoid large compiled payload activation in the hot runtime output path.
- Consider `constexpr`/compile-time validation or a build-time checker instead
  of a runtime parse result.
- If runtime validation is required, compute it in a tightly bounded explicit
  function with no persistent global object and no output-path side effects.
- Keep any later runtime activation behind a hardware plan and hardware result
  before merge.

The proposed next branch name is
`phase7a-runtime-config-activation-repair-minimal`.

## Non-Claims

- No hardware pass is recorded.
- No nunchuk validation is claimed.
- No runtime-loaded config is implemented.
- No runtime-config storage is implemented.
- No WebSerial/device write is implemented.
- No firmware flashing automation is implemented.
- No official configurator compatibility is claimed.
- No Super Smash Bros. Ultimate game-semantic change is claimed.
- No definite low-level crash, USB, memory, watchdog, or parser root cause is
  claimed.

## No-Fix Stop Line

No fix is implemented on this branch. This branch is failure analysis only.
Any future runtime activation must start from `configurator`, remain
source-backed, avoid unsupported diagnosis claims, and pass an explicit hardware
gate before merge.
