# Calibration Archive Policy

Status label: CURRENT.

Calibration evidence files should not be deleted. They preserve source
authority, branch decisions, blocker history, correction history, and hardware
result context.

Old packets may be archived later only when every impacted path, reference,
checker, fixture, and index is updated. Prefer normal Git history and explicit
review over broad file moves.

Quarantined docs remain preserved but are not source authority. These
quarantined records are retained for history and correction context. In particular,
external-remapper records remain non-authoritative unless independently
source-backed after the misattribution correction.

New current-state docs should summarize the operating state and link evidence;
they should not duplicate every historical detail from calibration packets.

Future agents should update `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, and
`docs/WORKFLOW.md` when roadmap state changes. Historical blocker packets may
remain in place as dated evidence.
