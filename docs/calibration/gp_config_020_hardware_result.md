# GP-CONFIG-020 hardware result

Status: **HARDWARE_VALIDATED**. Result: **PASS**, bounded to the exact tested
candidate/artifact pair and `GP_CONFIG_020_HW_V1`; evidence gaps: empty.
Physical observations are project-owner reports. Neither the processor nor its
independent reviewer performed controller testing.

## Identity and chronology

- Candidate branch: `codex/gp-config-020-repaired-built-f`
- Candidate Git SHA: `7db4f447d5e796367071b7143fa6c9274c70ae5e`
- Candidate tree: `4b5b63ce56219a508e2b71745438a609dd5661c3`
- Sole composition parent / queue base: `de36d24422a67e8be7992217856c76e8420a71f6`
- Source-free reviewed handoff R: `040735f6916c7a77924ef53f1b4a873281f2cb7f`
- Protocol: `docs/agent_framework/GP_CONFIG_020_HARDWARE_PROTOCOL.md`,
  `GP_CONFIG_020_HW_V1`; frozen SHA-256
  `ca6914ea8526e871760c7033a0b3df5aa1e07ba7e4c266cfbaa0aae5193a3421`.
- Exact preserved UF2: `local_backups/hardware-artifacts/7db4f447d5e796367071b7143fa6c9274c70ae5e/7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500/firmware.uf2`
- UF2 SHA-256: `7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500`; size: `796160` bytes.
- Native actual pre-update custody: `PRE_HANDOFF_VERIFIED`, followed by owner
  manual copy to `RPI-RP2`; processor independently rehashed the same preserved
  regular non-symlink bytes. No candidate rebuild or device operation by processor.
- Device About screen: `Glyph HayBox`, `7db4f44`, `glyph_mk6`; short identity
  MATCH. Full SHA is unavailable on the existing screen. Candidate
  `config/glyph/common/src/display/AboutMenu.cpp` displays `FIRMWARE_VERSION`;
  `builder_scripts/arduino_pico.py` derives short Git HEAD.
- Structured Revision-2 record: `repo-json:docs/calibration/fixtures/gp_config_020_hardware_evidence.json`.

This source-free evidence E descends from R and precedes separately reviewed
source integration I. Candidate source remains unmerged in this publication.
The composition parent is not a source-free canonical base; the build's
source-free starting canonical was `ea55cb4a284bfde3812bedccb70c380a6b85d48e`.
Original C020/failed F and GP-VAL-037/043 history remain separate and unchanged.

## Owner context and observations

Tester: project owner; date `2026-10-03`. Preservation session began
`2026-10-03T17:28:06Z`; individual physical-row times were not supplied.
Controller: Glyph Mk6; profile: Ultimate throughout.
GameCube: docked Nintendo Switch, Official Nintendo GameCube Adapter
`MOD.WUP-028`; Glyph USB-C -> GameCube cable end -> adapter -> dock USB-A.
USB: this Mac, XInput. These contexts/backend identities are owner reports.

| Row | Result | Observed |
| --- | --- | --- |
| Baseline | PASS | PASS, owner-reported: connected to this Mac through normal USB, neither flash nor Configurator mode; all normal as the last time. Host enumerated Raspberry Pi Pico USB; no anomaly. |
| H1 | PASS | PASS, owner-reported: all good on those; clean GameCube startup, stable Ultimate profile. Supplemental existing About screen: Firmware Glyph HayBox; Version 7db4f44; Device glyph_mk6. Short identity matches F; full SHA is unavailable on this screen. |
| H2 | PASS | PASS, owner-reported: Left X=-67; back to 0, and nothing stuck. |
| H3 | PASS | PASS, owner-reported: Up Y=77 as expected; releasing put it back to 0 and nothing is stuck. Owner also reported expected Right, Down and diagonals. |
| H4 | PASS | PASS, owner-reported: miniscreen showed A and game registered A. Owner explicitly confirmed release and stated all buttons are released at the end; consolidated human report confirms clean release. |
| H5 | PASS | PASS, owner-reported: LT5 (X1 modifier) gave the expected [35,77] offset table to the nine directions. Owner explicitly stated inputs are always released; consolidated human report confirms clean release. |
| H6 | NOT_APPLICABLE | NOT_APPLICABLE: fresh pre-test Ultimate Config independently decoded and inspected: 42 remaps, zero omitted activates, zero BTN_UNSPECIFIED/zero activates. No remap-disable binding in the tested Ultimate profile; no temporary binding invented. Other profiles are outside this row. |
| H7 | PASS | PASS, owner-reported: did that and repeated all previous tests, still identical; explicitly tested all of them with the same results as the previous power cycle. Stable Ultimate profile and neutral confirmed in consolidated human report. |
| H8 | PASS | PASS, owner-reported: already doing that for the past two power cycles, all normal. Consolidated report confirms accepted profile/bindings with no stuck input or disconnection. |
| H9 | PASS | PASS, owner-reported: this Mac, XInput; redid previous tests, all identical, all good. Owner explicitly confirmed all prior tests were repeated; Left X=-67 to 0 and A registration/release identical. Backend identity is owner-reported, not device-reported; no other platform claim. |
| H10 | PASS | PASS: operator read-only GET_CONFIG capture at 2026-10-03T17:51:49.285092+00:00; independently compared pre/post raw bytes: 4201 bytes each, SHA-256 f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480, exact equality. No Config write/restoration/rollback required. |

## Config preservation and provenance

Fresh owner captures: `local_backups/gp-config-020-hw-20261003T172806Z/pre-test-backup.json`
(`2026-10-03T17:28:52.442906+00:00`) and `post-test-backup.json`
(`2026-10-03T17:51:49.285092+00:00`). Both complete raw payloads are
`4201` bytes, SHA-256 `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`, and exactly equal. The extracted
`pre-test-config-restoration.json` equals the captured Config; native decode/
re-encode is byte-exact; offline dry-run and required-binding guard PASS.
GET_CONFIG observes persisted bytes, so physical output remains separately
owner-reported. H6 N/A applies to tested Ultimate only: independently decoded
42 remaps, no omitted `activates` or explicit `BTN_UNSPECIFIED`/zero.

Final state: exact C020 UF2, unchanged Config, Ultimate, normal GC gameplay;
owner confirmed all prior tests identical. No restoration write or rollback.
Accepted F010 rollback UF2 custody was verified before update.

Primary human report: daemon chat `01a0fcbd-2b4c-7d31-9088-42a22e260b57`,
user message `01a102f8-96bf-7ec3-a0e2-d5b9fe49b4a7`. Original observations and
captures: operator chat `01a102c8-e3ce-77b2-a776-7776b8283cf0`; actual native
pre-update custody command `exec-4a00548b-60f3-4f6f-9b56-baf6e513111b`,
successful pre-test read `exec-00df5646-168c-416d-bea3-6789b887a468`,
roundtrip `exec-cc5e0321-b28d-4d20-80e6-4f4e937f81b4`, dry-run
`exec-81654ccb-44e3-4e4b-89a2-70a6ab088a93`. Supplemental device identity and
context complete older omissions without contradicting them.

Physical invalid-binding submission remains **NOT_TESTED / HOST_ONLY**;
physical invalid-input rejection is UNKNOWN. Nunchuk remains **NOT_TESTED**;
root cause remains **UNPROVEN**. No stored-load/RGB, platform-wide, other-profile,
release-wide or rebuilt-artifact acceptance is claimed. Earlier unexplained
aggregate fingerprint failure and bounded successful repeat remain historical.

## Processing and next action

Processor verified live refs, exact Git object/tree/parent, frozen protocol,
preserved UF2 identity, actual pre-update custody, device short identity,
all required rows, Config-supported N/A, and exact raw Config preservation.
Fresh independent native Sol evidence review is required before publication;
the complete worker result records its verdict and validation provenance.
This publication changes only the two native evidence/result literals and
directly coupled queue/current-state/runway records. Firmware behavior is unchanged.

After reviewed source-free PASS publication, immediately dispatch a separate
Implementation Supervisor for exact C020 post-hardware integration under the
GP-VAL-043 accepted-transition contract. It must independently verify live F,
original artifact custody, processor PASS and R -> E -> I chronology; review
source integration and validate all required current/historical gates, then
publish strict DONE correspondence. No new Planner/Curator is needed absent
actual substantive drift. GP-VAL-040/KBD remains human-paused; no lane resumed.
