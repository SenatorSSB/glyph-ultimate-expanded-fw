# Final USB gamepad publication — 2026-11-17

Status: source repair candidate in preparation; HARDWARE_RETEST_REQUIRED. No canonical
source integration, beta freeze or release. [Owner work order](WORK_ORDER.json) ·
[Source audit](SOURCE_AUDIT.md) · [Exact owner packet](HARDWARE_PACKET.md).

Live intake verified canonical `59870835e7cd8e7c52bd3742e4910a7083cd21f5`
and published beta branch `0a1eab885237f7e6ea04f405707fe78269367ef1`.
The repair branch descends from that beta tip, preserving original audit
`7908cac88317bbf0d1dee62ab1f8198bba12b4f3` and earlier accepted Switch evidence.
The owner subsequently reported XInput selected over direct Windows USB, no usable
browser gamepad, and only **Other devices / Pico** in Device Manager. Mac browser
attempts also exposed no usable gamepad. This supersedes the earlier audit's
“none identified” source-fix conclusion; it does not rewrite that audit's knowledge.

XInput: SOURCE_FIX_REQUIRED identified; bounded candidate repair requires host/build
proof and HARDWARE_RETEST_REQUIRED. DInput shares the source-confirmed late-interface
publication defect and requires the same source repair, independent of whether a
selected beta profile exposes DInput. Switch retains previous exact-image acceptance,
but shared repair requires a bounded regression on the new candidate. Configurator
remains excluded. Retro protocols remain excluded regardless of USB-C cable use.
Until exact physical results are accepted, do not mark SOURCE_FIX_REQUIRED: none or
claim beta readiness. The old accepted UF2 `de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518`
is historical Switch evidence, not acceptance of the new candidate.

The chapter uses native internal source-audit and host-fixture specialists and a
fresh independent reviewer under AGENTS Start Here's agent-framework contracts.
The original unrelated dirty checkout remains untouched. No Planner/Curator calls,
new full user chat, device operation or public release is needed for this bounded
owner-authorized candidate. Runtime model/effort identity and token telemetry are
UNKNOWN unless reported by the runtime. Hardware wait begins at final handoff.
