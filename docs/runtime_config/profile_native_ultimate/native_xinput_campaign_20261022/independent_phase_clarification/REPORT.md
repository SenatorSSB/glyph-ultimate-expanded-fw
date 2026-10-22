# CDC phase correspondence clarification

**The existing Configurator metadata procedure is source-supported within the already approved C-event scope. No new owner approval is needed merely to disambiguate its mode-specific VID/PID.** Preserve the conflicting global XInput wording as an engineering discrepancy; do not pretend the sealed packet was internally exact on this detail. No packet/source/report was edited and no live call was made.

This interpretation relies on root's direct report that the owner approved the exact current campaign, including its Configurator events. Historical proposed packets provide technical source evidence, not renewed authority by themselves.

## Precise correspondence

The approved JSON event1/C00 at lines159–182 explicitly calls for one same-unit CDC metadata lookup followed by current Configurator/backend8 identity, normal STATUS and fresh Config backup. The same role appears in24 C events. The26 ordinary B boots instead require XInput/backend2 (e.g.lines538–553). `command_templates.json` lines22–32 separately selects the Configurator identity command with `ACTUAL_CURRENT_CONFIGURATOR_PORT` and `--context configurator`; its generic ports qualification at line335 requires a fresh same-private-unit lookup after each Configurator entry/ordinary boot.

Exact F `HAL/pico/src/comms/ConfiguratorBackend.cpp` line139 sets VID2E8A/PID1092. The existing `configurator_port_lookup.py` SHA a2c79a297214a672df9d7d06429656561bce302ef332832bf80d240aa55a6e43 uses one `list_ports.comports()` call at line19 and retains only2E8A/1092 at lines20–24. Lines32–36 refuse nonunique/unexpected paths without port open or retry. That hash matches the historical entry packet's recorded lookup source hash. Its ENTRY_PACKET.md lines7–9 documents the same ordinary Configurator route and metadata-only procedure. The inherited, currently pinned session_plan.md lines17–26 requires preservation reads on the approved current port; session_plan_addendum.md lines19–31 explicitly requires a separate current Configurator session/neutral identity rather than gameplay identity.

Conversely the pinned stopped rebind source lines42–51 is specifically a gameplay XInput metadata step: it filters0738/4726 at line48, then requires same private serial/location before the XInput identity command at line53. It is not a Configurator VID/PID oracle and its stateful wrapper remains forbidden.

## Discrepancy and bounded resolution

The final MD line74 and `command_templates.json` lines2–18 incorrectly describe the XInput0738/4726 source filter as if it covered all50 lookups. Read literally for C00, that would select no correct Configurator device and cannot meet the separately explicit backend8 event. Neither firmware nor the procedure supports claiming that Configurator enumerates as0738/4726.

Read in the approved packet's event-specific context, this is a mode-label/procedure-generalization error rather than a new product, protocol or authority decision. The already enumerated Configurator metadata operation uses its existing2E8A/1092 procedure; the already enumerated XInput operation uses0738/4726. This satisfies the specific phase, current-port and same-unit requirements without adding an operation, backend, endpoint or write. It is not permission to execute the old wrapper or silently modify the sealed constant.

For each C event, consume exactly its one allowed metadata enumeration using the unchanged Configurator procedure, retain the new exclusive snapshot, then independently require the original private unit's exact serial and location0-1 before any authorized port open. For each B event, retain the XInput filter and the same private-unit check. Never combine both PID pairs into a broad search, fall back from one to the other after failure, reuse a stale port, repeat enumeration, alter counts, or let metadata substitute for required current identity. No-match, multiple matches, wrong unit/location or unexpected mode remains STOP before reads/writes. The existing helper's unique/path check alone is not the full private-unit check; the caller must retain the packet's serial/location comparison.

The source facts and specific24/26 event authority therefore permit that narrow phase interpretation within the owner-approved scope. Root should retain this discrepancy and the selected phase/expected VID/PID in the execution receipt. This clarification does not start execution, republish approval, expand mutation/physical limits, change restoration/STOP requirements or waive any acceptance gate.

All checks here were filesystem reads and hashes only. Original review seal and exact packet bytes remain unchanged. Root owns any execution and publication.
