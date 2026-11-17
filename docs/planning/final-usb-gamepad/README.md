# Final USB gamepad publication — 2026-11-17

## Exact candidate physical qualification accepted — 2026-11-17

Required first-beta physical scope **PASS** for source
`dcf6e29589f558a95c021bef491578f87e41750f`, tree
`a7731388430ea70dbe666298953795f4018069b0`, retained UF2 SHA-256
`2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`
(1,325,568 bytes). Windows0738:4726/joy.cpl, original Switch USB/Ultimate,
GameCube-adapter/original Switch/Ultimate, final API-visible preservation of368-byte
Config/all27profiles and normal reconnect PASS. Host/source repair proof retains its
focused PASS and recorded framework failures; no full aggregate PASS is claimed.
DInput physical N/A for actual selected profile; future Senscope complete-path DInput
acceptance is required before public complete-profile/device release. JoyCheck/browser
Gamepad API remains NOT_QUALIFIED, discrepancy unresolved. Unique unit ID and exact
adapter model UNKNOWN; independent review accepts same-session owner continuity and
approved bounded route without broader claims. SOURCE_FIX_REQUIRED: none identified
for selected first-beta required scope. Keyboard deferred; Switch2 out of scope;
Nunchuk NOT_TESTED. Canonical integration pending owner authorization; beta freeze
prepared/not activated; no public release. [Accepted evidence and exact next step](acceptance/README.md).
Earlier entries below retain chronological knowledge, not current pending-test status.

Status: exact source repair candidate built and retained; HARDWARE_TEST_REQUIRED / HARDWARE_RETEST_REQUIRED. No canonical
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

## Exact candidate handoff

[CANDIDATE.json](CANDIDATE.json) binds source/tree, exact build input inventories,
UF2 custody and addresses. [VALIDATION.json](VALIDATION.json) preserves all actual
outcomes and debts; [RESOURCE_COMPARISON.json](RESOURCE_COMPARISON.json) records
650,556→650,564B flash (+8), static198,888B and heap63,060B unchanged, 3,302 equal
linked function shapes and unchanged stack models. [LOG_INDEX.json](LOG_INDEX.json)
binds local logs. The full wrapper and aggregate are not PASS. The health count
is corrected only as derived docs metadata after the exact build.

Source `dcf6e29589f558a95c021bef491578f87e41750f`, tree
`a7731388430ea70dbe666298953795f4018069b0`; UF2
`2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`,
1,325,568bytes. Exactly one owner hardware handoff remains. No installation,
canonical merge, beta tag or public release occurred. This dedicated worktree
and owner-primary custody remain retained through hardware wait.

Reproduce the resource comparison with `verify_resources.py --candidate-resource
<extracted-candidate-resource> --baseline-resource <retained-598-resource>
--candidate-elf <retained-candidate.elf> --baseline-elf <retained-598.elf>
--output <new-report.json>`. Extract graphs using the existing GOPT resource
extractor and pinned ARM toolchain; `core0.json` records its actual50-route
composition. Native package/host boundaries and each historical standalone
checker failure remain explicit in VALIDATION.json. The supplemental
[retro constructor smoke](retro-smoke.json) uses [this host body](retro_smoke.cpp)
with the existing gp_config021 console methods; it proves source initialization,
not physical retro protocols.

[Fresh independent review](REVIEW.json): APPROVED_FOR_OWNER_HARDWARE_HANDOFF,
no material findings across source, tests, exact build/custody/resources and final
source-free evidence packet. Canonical integration remains prohibited until exact
hardware acceptance. Network-enabled live readback before publication still shows
59870835 on configurator and unchanged0a1eab8 beta-readiness tip.
