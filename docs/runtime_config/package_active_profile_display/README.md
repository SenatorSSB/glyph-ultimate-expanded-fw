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
Exact source/build/artifact/review results will be recorded in a separate
post-build record, referencing the already-existing clean source commit.

See [hardware proposal](HARDWARE_PROPOSAL.md); it is UNAPPROVED and non-executable.
