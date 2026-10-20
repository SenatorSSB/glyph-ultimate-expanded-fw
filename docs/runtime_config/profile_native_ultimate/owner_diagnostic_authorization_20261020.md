# Owner authorization — bounded native diagnostic exception

Direct human owner reply in the active profile-native chapter, 2026-10-20. This record preserves the reply verbatim below. It does not grant device approval.

I authorize the bounded diagnostic exception described in the proposal and its correction, subject to the constraints below.
Authorized scope
1. Retain bounded timing and stack instrumentation in the final tested firmware candidate.
2. Add exactly one narrowly scoped, read-only XInput diagnostic snapshot command for obtaining the specified measurements.
3. Measure:
  - native controller-frame evaluation time;
  - native profile activation/preparation time;
  - runtime stack use observable after the instrumentation has been initialized.
4. Preserve all existing RAM, stack, flash-partition, filesystem, transaction-reserve, and resource limits. No limit increases are authorized.
5. Preserve the existing GP-BIND-003 runtime-identity request/response bytes, status semantics, framing, and behavior unchanged. Do not reinterpret or extend the existing 16-byte request or 72-byte response.
Required safety and implementation constraints
- Reuse existing diagnostic/serial infrastructure where suitable.
- The new snapshot command must not interfere with the existing XInput viewer or runtime-identity transport.
- No writes, profile changes, controller resets, runtime reconfiguration, arbitrary memory reads, or other control operations may be exposed.
- No dynamic allocation, blocking I/O, persistent storage operations, or additional unbounded work in the controller polling path.
- Instrumentation must use bounded fixed-size storage and deterministic execution.
- Preserve normal controller report generation, SOCD history, frame processing, and backend behavior.
- Prove stack instrumentation does not corrupt reserved stack regions, interrupt state, or active controller data.
- Retain independent compiler/call-chain/interrupt stack analysis; observed runtime stack usage does not replace structural safety proof.
- Record instrumentation overhead and measurement conditions. Do not assume instrumented execution times equal uninstrumented execution times.
- Preserve exact source, build, diagnostic protocol, and measurement provenance.
Evidence limitations
Measurements beginning after runtime/core startup do not establish earlier startup stack peaks.
GameCube and Switch timing remain NOT_MEASURED unless separately measured.
Do not extrapolate post-startup measurements to unobserved startup, interrupt, ROM, or backend execution paths.
If the diagnostic cannot operate safely within the existing resource contract, stop and report the concrete constraint rather than expanding scope.
Governance and hardware
Treat this as explicit owner authorization for this one bounded diagnostic exception within the ongoing profile-native chapter.
Complete any required source-free amendment, independent review, focused regression tests, final build, resource proof, and exact artifact custody.
Retain the instrumentation in the final candidate that undergoes hardware testing; do not substitute a different instrumentation-free firmware while claiming the measured evidence applies to it.
This authorization does not approve flashing, ProfileStore mutation, Config changes, recovery procedures, or physical testing.
A separate candidate-specific hardware preparation packet and explicit owner approval are still required before any device mutation.
Continue autonomously through the authorized source, verification, review, and build work. Return only at a genuine hardware approval gate, a resource/safety contradiction, or another substantive owner decision.
