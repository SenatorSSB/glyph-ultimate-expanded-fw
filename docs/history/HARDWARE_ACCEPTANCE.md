# Hardware Acceptance

## Rules

PASS belongs to an exact candidate, artifact and recorded test scope. A rebuild
does not inherit PASS. Build proof is not hardware acceptance; source implementation
is not physical qualification. N/A is not PASS; NOT_TESTED is not FAIL;
NOT_QUALIFIED is neither PASS nor necessarily FAIL. Owner-observed results and
machine-captured evidence remain distinct. Packet-specific limitations remain binding.
[CURRENT_STATE](../CURRENT_STATE.md) owns present qualification.

## Current selected first-beta firmware acceptance

The retained acceptance and physical-result records establish selected-scope
acceptance on 2026-11-17, summarized here with exact
[source correspondence](SOURCE_LINEAGE.md#current-first-beta-lineage):

| Identity | Value |
| --- | --- |
| Tested source | `dcf6e29589f558a95c021bef491578f87e41750f` |
| Tested source tree | `a7731388430ea70dbe666298953795f4018069b0` |
| Retained tested UF2 SHA-256 | `2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42` |
| UF2 size | 1,325,568 bytes |

| Route / feature | Status | What the record establishes |
| --- | --- | --- |
| Windows XInput / joy.cpl | PASS | X1/X2: owner reports working 0738:4726 XUSB identity/driver, both left axes/signs, representative face button, release/neutral and no stuck input |
| Original Switch USB / Ultimate | PASS | S1/S2: selected owner-observed controls and release/neutral scope |
| GameCube → actual adapter → original Switch / Ultimate | PASS | G1/G2: selected owner-observed route; exact adapter model UNKNOWN |
| Config / ProfileStore preservation | Scoped PASS | P1/P2: API-visible 368-byte Config, ordered 27-entry inventory and all raw wrappers/revisions/digests exact against preflight |
| Normal reconnect / usability | PASS | R1: owner reports XInput/Kaz5Test, input/release and usability after restoration/readback |
| DInput | N/A | D1/D2: actual selected beta profile does not expose this route |
| Browser Gamepad API / JoyCheck | NOT_QUALIFIED | XInput HOME-only discrepancy unresolved; no universal browser claim |
| Keyboard | NOT_TESTED / deferred | No physical qualification in this packet |
| Switch 2 | NOT_TESTED / OUT_OF_SCOPE | Original Switch results do not qualify Switch 2 |
| N64 / NES / SNES | NOT_TESTED | Source/constructor checks supply no first-beta physical qualification |
| Fresh Install recovery | NOT_TESTED / post-beta hardening | Existing valid-store update scope does not qualify Fresh Install |
| Nunchuk | NOT_TESTED | No executed nunchuk rows |

Machine evidence consists of three complete 64-exchange captures and 81 healthy
profile observations. The retained preservation replay and independent review
record reconstruction from raw responses and journals, verification of 491 private
manifest files and both retained UF2 copies. This extraction uses those sanitized
records; it has not accessed or rehashed the private firmware/captures.

API-visible preservation is not raw-flash equality. R1 is owner-reported; no later
raw post-reboot Config/ProfileStore comparison is claimed. Installation and matching
DeviceInfo source prefix are owner-supported observations, not cryptographic
flashed-byte attestation. Same-session unit continuity is owner-reported and
supported by distinctive unchanged state; globally unique unit ID UNKNOWN.
Exact adapter model UNKNOWN. Per-modifier coordinates and machine gameplay
recordings are absent. No general adapter or all-profile acceptance follows.

JoyCheck saw only HOME for XInput after HOME activation despite working joy.cpl;
Switch USB showed button activity on the same site. Browser root cause UNKNOWN;
no controller defect is established. Before public Senscope complete-profile/device
release, [complete-path acceptance](../ARCHITECTURE.md#senscope-boundary)
requires physical DInput with an appropriate supported Senscope-authored profile
against an owner-frozen target. That future work cannot broaden this packet.

## Profile and gameplay-specific acceptance

Controller-firmware route acceptance and character-profile gameplay acceptance
answer different questions. Accepted character behavior does not qualify unrelated
firmware routes, arbitrary profiles or universal move recognition.

| Episode | Evidence and limits |
| --- | --- |
| Kazuya v4 / KazTest4, historical ID51 | Gameplay-accepted rollback reference per the later [canonical Kazuya source](../../profiles/kazuya/Kazuya.profile.json) and [accepted identity](../runtime_config/accepted_character_profiles/ACCEPTED_KAZUYA.json). Accepted source commit `5e30341ee06761e20e864ccc013ca6658e42b5ca`; exact source blob `50741602af1b8e5bf70bdc745416ca9a794ee3c7`; wrapper SHA-256 `46084bbcf55646819ab0ce824b9de9ac778d3bc4d9344a8c8bcbfe5d15f6142c`. The original v4 README is a pre-device HOST_VERIFIED / gameplay NOT_TESTED snapshot; its historical status is preserved. |
| Kazuya v5 / KazTest5, ID53 | Owner reports readback verified and gameplay accepted. [Canonical source](../../profiles/kazuya/Kazuya.profile.json) is byte-identical to v5, source commit `510234798d74d4aa29dbc35df030df5530c26c81`, Git blob `64c2825605082701b9252832149535c82ebb7fc5`; wrapper SHA-256 `72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87`. Private controller receipts are unavailable in the checkout; promotion performed no controller operation. |

In the final USB packet the owner calls the executing profile Kaz5Test while the
saved ID53 record is KazTest5. Behavior is owner-observed; saved names and
Configurator identity alone do not attest execution. The machine preservation
comparison establishes retained wrapper bytes, not gameplay recognition.

## Selected historical physical milestones

| Episode | Historical status and lasting boundary |
| --- | --- |
| June 2026 generic active publication diagnostics | HISTORICAL FAIL: [dedicated active storage](../runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md) and [generated baseline view](../runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md). No proven root cause; later native success does not turn these into PASS. |
| June 29 source-owned Y2 port | HISTORICAL owner-reported PASS for the June 29 source-owned Y2 layout (including forced A+Up/A+Down without disconnect); no generic runtime-view acceptance. |
| October 22 selector | HISTORICAL FAIL for `4898951994bcabcaef2846145de2922a674656f8`: GameCube final B→A selection froze at an intermediate menu. Root cause UNPROVEN; separate XInput observations remain bounded. Retained UF2 SHA-256 `7ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e`; original failure record identified below. |
| October 23 repaired selector | HISTORICAL PASS within [accepted integration](../runtime_config/controller_profile_selector/integration_20261023/README.md): exact `8b2c75e35bb990aee06de3165e5780082c4f08ad`, XInput selection/persistence and API preservation; normal GameCube Switch/adapter OWNER_REPORTED_PASS. Conditional physical no-poll remains NOT_TESTED. |
| November 16 GOPT closeout | PARTIAL: preservation/startup/final XInput and owner GameCube observations; distinct-profile output and physical ellipsis undemonstrated. Sanitized closeout retains profile27's inherited context hold. |
| November 17 earlier beta audit | SUPERSEDED OBSERVATION: earlier no-fix conclusion was superseded by the later physical XInput finding and final USB repair; old exact-image Switch evidence remains historical. |

## Evidence locations

Use the [evidence index](../evidence/README.md) for authoritative entrypoints,
[history](HISTORY.md) for corrections in sequence and [source lineage](SOURCE_LINEAGE.md)
for the tested-source/build/acceptance/documentation distinction. Private raw
captures remain private; sanitized records define the public claim boundaries.

## Historical source provenance

The following original development-fork records supplied the selected facts
above at snapshot `5c54d0dcca304f476720655c96f315bac5ed2f6b`. These are provenance
identifiers, not supported public navigation. Preserve the originals privately
when preparing an export; their omission does not broaden any acceptance.

```text
docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md
docs/runtime_config/controller_profile_selector/hardware_failure_20261022/evidence.json
profiles/kazuya/v4/README.md
docs/planning/final-usb-gamepad/README.md
docs/planning/final-usb-gamepad/acceptance/INDEPENDENT_REVIEW.json
docs/planning/final-usb-gamepad/acceptance/PHYSICAL_RESULT.json
docs/planning/final-usb-gamepad/acceptance/PRESERVATION_REPLAY.json
docs/planning/final-usb-gamepad/acceptance/README.md
docs/planning/final-usb-gamepad/acceptance/SENSCOPE_HANDOFF.md
docs/planning/gopt-qualification/PHYSICAL_CLOSEOUT.md
```
