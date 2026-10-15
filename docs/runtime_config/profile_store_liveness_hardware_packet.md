# Bounded resumed B9/B10 campaign — new candidate only

**PREPARED ONLY; HARDWARE_TEST_REQUIRED.** Do not reuse failed594066d9 for the
campaign. Use the full new SHA/tree/parent/base/branch, exact UF2 SHA-256 and
size from its primary-repository content-addressed HANDOFF. Rehash before an
owner-authorized flash. Never rebuild a custodied candidate. Canonical remains
unmerged. No hardware action was performed while preparing this packet.

First complete the separate device-state adjudication. Preserve that result
and Config/profile readback before the new flash. Enter Configurator through
an established route after flashing exact bytes, with no Clean/factory reset.

Use new `glyph_profile_store_candidate_tool.py` with `--timeout 10`, unique
`--output` and exclusive `--trace-out` files. Inspect `--help`; do not copy
historical ARM-then-ordinary-UPDATE scripts. Every mutation still needs an
exclusive immutable `--request-out`, explicit current incarnation/generation,
full fresh token and appropriate revision. No automatic mutation retries.

1. Capture `pulse`, then `status --trace`, then LIST/READ useful IDs and Config.
   Require candidate/fault capability version2, matching expected state,
   no pending/armed fault, and valid RAM resource margins. Pulse proves only
   dispatcher/RAM/transport liveness; STATUS supplies actual capacity/health.
2. Repeat a bounded20 process-open/close cycle using pulse and STATUS, retaining
   phase journals. Include traced and untraced STATUS. This specifically tests
   changed CDC lock coordination and reconnect behavior; a zero-byte/malformed
   response or timeout stops the campaign immediately.
3. Replay the two previously completed **open-write** fault rows on the existing
   disposable ID only. Repetition is justified because ARM semantics and USB
   access changed. ARM returns `storage_fault_pending=true`, armed=false, a
   nonzero ticket and version2. Pending rules must survive STATUS without
   triggering. For the one intended disposable UPDATE, explicitly copy the
   ticket into `--fault-ticket`. Require the expected failure/unknown result,
   QUERY reconciliation NOT_FOUND, unchanged useful IDs/roots/revisions, and
   pending=false/armed=false afterwards. Retain the zero-byte temp boundary;
   do not improvise cleanup. CLEAR is explicit if an unused pending rule exists.
4. Continue at the previously unexecuted **record/write fail-before** row using
   the same pending/ticket procedure. Issue traced STATUS between ARM and the
   intended UPDATE and immediately after reconciliation. Never infer whether
   ARM was sent from its action name: inspect `status_preflight` versus `arm`
   transmit/response events and `liveness_stage` frames.
5. Resume the remaining unexecuted frozen strict-hardening fault, selection and
   recovery rows from `profile_store_strict_hardening_hardware_packet.md`.
   Use new ARM/ticket syntax throughout. Preserve earlier name/capacity/identity/
   migration evidence as historical PASS; do not repeat unrelated complete
   matrices. Recheck representative ordinary and recovery Configurator access
   and GET_CONFIG because their shared transport now uses the guarded adapter.
6. Preserve final status/list/Config and useful payload hashes. No merge until
   exact new SHA + exact UF2 hash receives owner hardware PASS. Nunchuk remains
   NOT_TESTED unless explicitly exercised/reported by the owner.

If ARM response is lost, its pending rule is inert: a later ordinary command
without its ticket cannot activate it. Make at most one bounded pulse/status
adjudication according to operator authority; if transport is unusable stop.
Do not automatically reuse a saved fault ticket after reboot. A ticket-bearing
exact replay may return an already-durable receipt, but a fresh fault attempt
requires fresh observed pending state and a fresh mutation token.

A failure report must retain the last host phase, write completion, received
stage, final response (if any), candidate/UF2 identity, physical observation,
and last authoritative generation/IDs. If trace stopped before stage4, focus
capacity/USB transmission; before6, Config read; before7, resource sampling;
after9, final transmission/host handling. Missing all stages does not prove
request receipt. USB enumeration alone is never controller acceptance.
