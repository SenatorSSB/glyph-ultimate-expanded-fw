# Original Config and all22 original profiles preserved

The owner-approved entry and subsequent same-user sandbox-exempt read exception
completed. [Actual result](readback_result.json) records one Config backup,
three LIST pages,22 first-attempt READs and26 total STATUS queries. The extra
identity attempt returned valid current Configurator status; its earlier
EPERM-before-request failure remains preserved. Real/effective UID remained502.
No sudo, OS permission, driver, Config/profile or firmware change was made.

Custody audit PASS: the252-byte Config raw payload fully decodes and matches
its JSON; all22 complete READ wrappers roundtrip and match retained response
and raw protocol journals. [Private custody references](private_custody_references.json)
contain hashes only. Original Config/profile bodies, names, journals and device
serial remain in ignored owner-local backups. These APIs do not export a raw
filesystem, on-flash record encoding or historical revision archive.

[Independent version adjudication](legacy_version_review/REPORT.md) resolved an
overstrict private host checker. Directory legacy version1 and decoded schema3
are supported by accepted/F READ paths; both values remain recorded. The one
received READ was finalized offline without retry. The original assertion and
failed checker remain unchanged. Historical origin is UNKNOWN; root cause is
UNPROVEN. Native-versus-legacy class checks and all actual error/fence stops remain.

[Actual route review](actual_route_review/REPORT.md) finds no USB Switch backend
in this saved Config. [Reviewed host adapter](route_adapter_review/REPORT.md)
prepares only the exact temporary backend/default changes, preserving other
fields/chords and using existing guarded SET_CONFIG. Its11 pure checks and10
fake-transport cases pass; an initial fake-proxy omission is retained separately.
The adapter has not executed on a controller; frozen F and its UF2 are unchanged.

The owner uses Super Smash Bros. Ultimate gameplay to observe GameCube behavior.
This is functional downstream observation, not numeric analog-trigger or complete
simultaneous report-field capture. Missing fields retain their acceptance gaps.
The existing input-only CDC viewer and identity/metrics cannot replace them.

[Staged installation/qualification packet](../hardware_installation_qualification_20261022/INSTALL_PACKET.md)
is the next separate approval. No candidate install, Config/profile mutation,
physical acceptance or target timing/highwater measurement has occurred.
