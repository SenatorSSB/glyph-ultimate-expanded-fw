# Proposed exact operations — not execution authorization

Independent review and a new exact owner packet are mandatory. Root binds the same private unit, exact installed F/artifact/identity, ordinaryUSB restart to default XInput, current session and approved action counts. Do not use historical registry IDs from the earlier boot. No runtime mode/backend chords, automatic reset/reconnect, firmware/profile/configuration write, driver/control/OUT workaround or retry is introduced.

1. After root's separately approved same-unit CDC lookup/identity, one proposed registry-only operation is:

   `mac_hostinterface_observer inspect --approved-session APPROVED_SESSION --output NEW_INSPECT_JSONL`

   Require exit0, no timeout, empty stdout, the pinned source-derived COMPLETE stderr, a unique successful inspect_end with numeric fresh anchor/interface IDs/number0/location1048576, and every bounded inventory/identity record. The session's initial IDs are0 because they are unknown before inspection; final inspect_end supplies them. Location/VID/PID/ancestry is not a unique physical serial. Stop on every failure, unknown, ambiguous or overflow result. This operation cannot open/init/read a USB interface and does not continue to capture.

2. Only the separately authorized one capture may consume those fresh IDs in the same uninterrupted identified XInput boot/connection:

   `mac_hostinterface_observer capture --approved-session APPROVED_SESSION --anchor-entry-id FRESH_DECIMAL_ANCHOR --interface-entry-id FRESH_DECIMAL_INTERFACE --output NEW_CAPTURE_JSONL`

   Fixed VID0738/PID4726/location0x100000; exact number0/FF5D1/alt0/config1; optionsNone; associated descriptors only; one verified interrupt-IN pipe;32-byte buffer; three actual20-byte complete reports;5-second observation/one async abort/1-second grace; internal8-second watchdog. Wrapper must capture argv/binary/source hashes, stdout/stderr/exitstatus, no-timeout result, output hash and fsync/close, with an external10-second deadline and no retry. SDK does not guarantee finite abort completion. Retained pending state survives to process exit. Require exit0 and THREE_PREFLIGHT_REPORTS/end reports3/submissions3/abort0/settled_cleanup true plus three exact raw/decoded/timestamp pairs; use the frozen decoder, never zeros or a partial journal as a report. The old candidate correspondence verifier intentionally refuses preflight evidence and must not be loosened for acceptance.

The associated-descriptor API is documented readonly but the public SDK does not prove zero implementation-internal control traffic. No explicit control/fetch API exists here; nil/invalid metadata stops. Busy/permission/driver ownership errors stop without capture/seize/detach/install/sudo/authorization/config/alternate/stall-clear fallback. Raw reports qualify this host observer path only; no candidate or console PASS transfers.

Only pure/offline commands were actually executed in author preparation. Build and test commands are pinned in offline_evidence.json; none invokes either live operation shown above.
