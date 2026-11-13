# Package-aware active-profile display candidate

Owner direction: [2026-11-12](../../agent_framework/USER_DIRECTION.md#package-aware-active-profile-display-repair--2026-11-12).
Classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR; candidate only, hardware untested.
Base c439b7c6aab24ed8a0af3b497b7204ba3cd033c5 (canonical configurator
remains d31a5edd433beca0354e4595c26d0c4b69c085e8). Historical e416cabe
source/fixtures were inspected and selectively adapted; no historical evidence
or acceptance was copied forward.

The shared resolver retains compact/native/singleton/config-context/profile/ID
checks, ready/non-recovery checks and bounded visible metadata lookup. It also
requires the store's active owned/published native view, matching nonzero live
generation, active revision and live matching payload lease. Boot SetConfig
validates context; rendering must not repeat ContextMatches/ValidProfile or full
runtime identity hashing because those use mutable shared scratch. Normal boot
hands immutable gameplay store/activation state to display through the existing
boot mutex. Configurator and unspecified backend return before any store access.
Public Count/EntryAt preserve package visibility/fence filtering. No selection,
reference, activation, storage or protocol code changes.

Dashboard plate comes from the current execution row, including managed synthetic
cases. Supported labels remain Full, FGC, Split FGC, Plat Fighter; unspecified
and unsupported information displays Unknown Plate. Long-name clipping/available
screen space follows existing rendering; this repair adds no scrolling/layout.

Focused tests compile actual native decode/publication/SetConfig, resolver,
InputDisplay and MenuButtonHints on both enum ABIs with ASan/UBSan. Display,
backend and ProfileStore directory ownership are host doubles; managed visibility
is modeled here, not a physical managed activation. Relevant production store/
selection/package regressions must accompany them. No hardware, gameplay,
Nunchuk, timing/highwater or installed-build claim follows from host tests/build.
[Exact source/build/artifact results](VALIDATION.json) bind clean built source
`9e69188d857138a3884bcbe243f22188815e9355`. Evidence-only successor commits do not
change the built source or authorize substituting a rebuilt UF2. The final
independent review is recorded separately in FINAL_REVIEW.md.

See [hardware proposal](HARDWARE_PROPOSAL.md); it is UNAPPROVED and non-executable.

## Parent acceptance scope correction — 2026-11-13

Senscope's canonical [Phase-B terminal summary](https://github.com/SenatorSSB/senscope/blob/acf22010522ac5b2b17392e977d692195d39e154/docs/project/hardware/phase-b-corrected-packet/terminal-evidence/summary.json)
records PASS/HARDWARE_VALIDATED for parent c439 and its exact UF2
f7827890313cabdbcbe962add049d0f6cccc089f5c78afe3033a5b8285f6c37a.
It covers one Kazuya Managed CREATE (ID54/revision1, row3), native readback and
receipt correspondence, and preservation of all26 prior directory entries and
existing Config/default/backend/RGB state. Managed envelope/root bytes were
reconstructed expected bytes, not raw exported storage; Runtime Identity did not
attest the installed build. No activation or gameplay occurred. See
[PARENT_ACCEPTANCE.json](PARENT_ACCEPTANCE.json) for exact source/packet hashes.

The earlier blanket description of parent package behavior as unvalidated was
incorrect. This bounded acceptance does **not** validate the new9e691 display
build, managed activation, gameplay or arbitrary package/migration scenarios.
The accepted CREATE campaign is not rerun by this preparation.

[Post-build stack proof](resource/REPORT.md) closes the affected rendering bound.
The finalized [owner packet](hardware/OWNER_PACKET.md) remains UNAPPROVED.

[Focused independent follow-up review](FOLLOWUP_REVIEW.json) approves evidence
publication and this exact owner-approval handoff only. No physical approval follows.
