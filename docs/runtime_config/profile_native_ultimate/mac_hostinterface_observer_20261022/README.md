# New Mac IOUSBHostInterface observer — exact V2 approval gate

The [V2 owner packet](reviewed_owner_packet/QUALIFICATION_PACKET.md) and its
[machine bounds](reviewed_owner_packet/QUALIFICATION_PACKET.json) are ready for
explicit approval. **No live invocation is approved or executed.** Device access
remains STOP in Configurator. F334f, its build/artifacts/resource proof and all
limits remain unchanged. [Original-state API preservation](../postinstallation_preservation_20261022/README.md)
remains independently verified; native hardware acceptance is still open.

[SDK source feasibility](source_feasibility/REPORT.md) establishes a distinct
IOUSBHostInterface API path. Its ordinary optionsNone init exclusively owns only
the verified vendor interface; access may refuse. Associated descriptor getters
have no proven absence of SDK-internal USB traffic. No generic fetch, application
control/OUT, seize, driver, settings or privilege fallback is permitted. Successful
qualification would cover this host route and current legacy profile only.

The [parent source and evidence](prefinding_parent/REPORT.md), its
[initial independent PASS](independent_prefinding_review/REPORT.md), custody and
[unexecuted V1 packet](prefinding_owner_packet/QUALIFICATION_PACKET.md) remain
exact historical evidence, **UNADOPTED / DO NOT EXECUTE**. Root then found a
[deadline defect](deadline_finding.json): a receipt clock sampled before fallible
journal fsync was reused to authorize another read while the serial deadline
timer could not run. Both author and independent actual-source mocks reproduce
the parent enqueue at6s against5s. The original PASS is qualified by that concrete
finding; its bytes and failed witness are preserved.

The [corrected child](deadline_repair/REPORT.md) adds a fresh-clock check after
buffer preparation immediately before each enqueue. Expired or clock-failed
unqueued reservations settle without abort. The [same-reviewer repair and V2
correspondence ACK](independent_deadline_repair_ack/REPORT.md) passes independent
actual-source sanitized past-deadline, equality, clock-failure and timely-positive
cases and a byte-identical host rebuild. No further broad review/build loop ran.
Receipt timestamps retain their original meaning; end.submissions counts logical
reservations, which bound actual enqueues, rather than proving all were queued.
SDK call or cleanup completion within5s is not promised. Complete State storage
is retained on uncertainty;5s/3report/1abort/1sdrain/8sinternal/10sexternal bounds
and all API/ownership limits stay fixed. Tests used mocks, never the controller.

[Exact owner-local host custody](host_artifact_custody.json) and
[review binding](host_artifact_review_binding.json) identify binary108e64 and
sourcef0e246. Binary proof artifacts and SDK excerpt/command inputs remain in
private content-addressed custody referenced by each archive manifest. Public
code is inert text; no private serial, original Config/profile payload or raw
device journal is published. The seven original custody files stay unchanged.

Only a new explicit V2 approval can lift the prior access stops for one familiar
ordinary reconnect, same-unit lookup/unchanged identity, one new registry-only
inspect and one new bounded capture, then STOP. The frozen packet includes its
exact exclusions. No Config/ProfileStore/native/target-metric/Switch/WUP action,
physical campaign, HEP, integration or DONE is authorized. Nunchuk NOT_TESTED,
timing/highwater NOT_MEASURED, RT2 deferred and prior root cause UNPROVEN remain.
