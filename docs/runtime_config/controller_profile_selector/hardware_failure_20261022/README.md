# GP-NATIVE-002 exact hardware failure

Result: **FAIL / HARDWARE_FAILED**. Repair is required; no repair or device
continuation is authorized. Exact candidate4898951994bcabcaef2846145de2922a674656f8
and UF2 SHA2567ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e
remain retained and unmerged.

The [owner report](owner_report.json) records GameCube SEL01→SEL20→SEL01,
correct reported values, then final B→A frozen at the intermediate menu before
boot and unresponsive. The owner reconnected and reports recovery. Current
identity and postfailure Config/original record integrity are unknown;
restoration is not confirmed. Twenty owned fixtures IDs28..47 remain.
No retry, automatic cleanup, restoration or flash follows this report.

The [V2 exact failure evidence](evidence.json) preserves XInput ID28→47→28 revision1
runtime-hash matches and owner LF1 offsets(53,0)→(72,0)→(53,0), release(0,0),
plus matching SEL01 identity after ordinary power reconnect. Those observations
remain USB-scoped and do not override the GameCube failure.

[Independent source diagnosis](SOURCE_DIAGNOSIS.md) finds a concrete missing
selector consumer progress guarantee across existing GameCube blocking polls.
It is a plausible mechanism, not established causation. Root cause UNPROVEN.
Host/resource PASS cannot exclude this liveness failure. Original source/build/
resource/handoff evidence and manifest remain immutable; no acceptance transfers.

Pending curation names GP-NATIVE-002 as the new failure. Existing GP-BIND-001/002
subjects accompany it only to satisfy the singleton obligation contract; their
previous resolved disposition and c5415ab0348b9c1db9dce36eda73bf4a7e2f7478
receipt remain unchanged and no previous work is reopened. No repair READY, new
Planner campaign, source integration or physical PASS is created.

The [bounded assessment](assessment.json) retains input hashes, detailed scope and
the complete prior resolved curation obligation without exposing private device
identifiers or original Config/profile bodies.
