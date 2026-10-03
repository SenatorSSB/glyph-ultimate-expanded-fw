# GP-CONFIG-020 hardware protocol

Protocol version: `GP_CONFIG_020_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. No physical observations have been recorded.

## Exact handoff identity

- Candidate branch: `codex/gp-config-020-repaired-built-f`
- Candidate Git SHA: `7db4f447d5e796367071b7143fa6c9274c70ae5e`
- Candidate tree: `4b5b63ce56219a508e2b71745438a609dd5661c3`
- Sole parent / authorized canonical base: `de36d24422a67e8be7992217856c76e8420a71f6`
- UF2 SHA-256: `7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500`
- Preserved locator: `local_backups/hardware-artifacts/7db4f447d5e796367071b7143fa6c9274c70ae5e/7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500/firmware.uf2`
- Fresh independent postimplementation review: PASS with no findings for the exact candidate, build output, custody bytes, correspondence, and protocol.
- Build output: `.pio/build/glyph_mk6/firmware.uf2`
- UF2 size: `796160` bytes
- Build: `PASS (`pio run -e glyph_mk6`)`; RAM `78,880/262,144 bytes (30.1%)`; flash `385,984/1,568,768 bytes (24.6%)`.

F is the actual committed-before-build snapshot above. Its sole parent is a
local candidate composition descendant, not a source-free canonical commit.
The source-free canonical starting point is
`ea55cb4a284bfde3812bedccb70c380a6b85d48e`, which includes strict
GP-VAL-043 DONE. The composition merge
`de36d24422a67e8be7992217856c76e8420a71f6` has that canonical commit
as its first parent and repaired C020
`3138ade526cabde23a0abedcb94acae8512579d1` as its second parent.
C_R's sole parent is adopted source-free B_R
`0f7fe50b3b5f385397a9737bc4c0a50ddda683c8`; its tree is
`67a4edd29bcd4c0adfd3ea52790d9a31293f6036`.
Original C `256bf44cea71f6d5c87aa1675c8dac9f6b79259f`, failed F
`0a5dd751c391198140ed146853a69fc825d902c7`, and original GP-VAL-037
DONE evidence remain distinct historical records. C_R-to-F_R critical
source/build entries, all five candidate host files and all three repaired
proof paths are exactly equal. The F_R commit changes only four reviewed
validation metadata paths after the composition merge.

The build is not hardware acceptance. Use only the preserved bytes above;
do not substitute mutable `.pio` output or a rebuild. The operator must run the
native pre-handoff custody check again immediately before a manual update.

## Scope and evidence boundaries

This protocol covers the accepted normal profile, representative valid button
bindings, ordinary startup and input release, reconnect/reboot, and exact owner
Config preservation/restoration on Mk6 GameCube and the owner's ordinary
source-supported USB context. Record the actual backend/host used; do not infer
compatibility with an untested platform. Retain exact 28-table/X1 source equality
and ordinary Ultimate behavior. No new table or gameplay semantics are defined.

The SetConfig validator rejects invalid populated input bindings before save or
live publication. The repaired source was checked under one-byte selected Mk6
and four-byte host layouts; GP-VAL-043's separate source-free correspondence
and real-helper transaction checks are complete. It preserves the remap-disable sentinel and leaves RGB and
stored-load acceptance outside this repair. Host decoder/validator and actual
handler transaction proofs cover the invalid cases. Existing reviewed tooling
has no C020-specific invalid-binding submission suite, so those negative cases
are explicitly HOST_ONLY / physical UNKNOWN and excluded from physical claims.
Do not modify or repurpose the GP-CONFIG-005 or GP-CONFIG-010 specialized tools
or create a new sender to obtain those observations. This protocol does not
establish release-wide safety or repair invalid stored Config acceptance.

Give the owner **one physical action at a time** and wait for the requested
observation before continuing. A mismatch, crash, stuck input, disconnect,
wrong identity, unsafe operator route or restoration failure stops the test.
Record the observation; never convert an omitted or failed required row to PASS.
Nunchuk remains NOT_TESTED and root cause remains unproven.

## First physical action

With the controller still on its existing accepted firmware, connect it once in
its normal gameplay mode. Report the controller model/revision, backend and
host/adapter, whether startup reaches the normal dashboard, and any anomaly.
Do not change firmware or Config yet. Wait for this report before the next step.

## Preconditions before changing firmware or Config

1. Record tester and timestamp, model/revision, normal profile, actual
   GameCube/USB host context, current firmware identity and the first-action
   observation. Resolve any existing failure before testing this candidate.
2. Capture the actual current owner Config using the existing read-only serial
   tool on the owner-selected port in Configurator mode. Save its complete raw
   payload and decoded form under owner-held `local_backups/`. Do not guess a
   port or reuse a historical payload as the current Config.
3. Verify the backup's raw byte count and SHA-256. Extract only its `config`
   object to a separate artifact, and prove decode/re-encode is byte-exact
   against `rawConfigPayloadBase64`. The historical 4201-byte owner Config
   `f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`
   is reference evidence only. A different current payload requires fresh
   preservation and safe-route validation, never automatic overwrite.
4. Validate that extracted artifact with the existing tool's offline
   `--dry-run` and its required-binding guard. Do not edit or bypass the guard.
   If a byte-exact restoration route is unavailable, stop before mutation.
5. Verify the exact accepted rollback UF2 remains available: F010
   `1c0ff22646729d26d45eacb4b8322c5baea7de48`, SHA-256
   `4312f6a64fd1009e231aab2015e3ce67f862abd88a8ea31cd545db0e91e27476`,
   under its native content-addressed locator. This is rollback custody, not
   acceptance of C020. Owner-controlled recovery must be available.
6. Re-hash the preserved C020 UF2 with the native custody tool and require the
   exact F/artifact pair above. Only then give the owner the single manual
   update action. No agent flashing or device-write automation is authorized.

Existing command shapes (the operator supplies the actual port and paths):

```text
python3 tools/glyph_serial_config_tool.py --read --port <port> --backup-out <pre.json>
python3 tools/glyph_serial_config_tool.py --dry-run --artifact <extracted-config.json>
python3 tools/glyph_hardware_artifact_custody.py --pre-handoff-verify --candidate-sha 7db4f447d5e796367071b7143fa6c9274c70ae5e --artifact-sha256 7743fcbe3d71ec4159e6da5026a1b4560cbbef4d1654cb80b8907fcce344b500
```

The tool's backup wrapper is not a write artifact: use only the extracted
`config` object after raw roundtrip equality. GET_CONFIG observes persisted
bytes, not live RAM; physical output is a separate observation.

## Required observations on the exact candidate

Perform and record each row separately, with press/release observations before
moving on. Use the owner's existing accepted mappings; no temporary invalid
payload, new binding or profile-policy change is required.

| Row | Action given alone | Expected observation |
| --- | --- | --- |
| H1 | After the owner manually updates from the verified preserved UF2, connect once in normal GameCube mode. | Clean startup, normal dashboard/profile, stable connection; record device-reported firmware identity matching F's short Git identity. |
| H2 | Exercise one existing horizontal direction, then release. | The accepted direction appears; release returns to neutral, with no stuck input. |
| H3 | Exercise one existing vertical direction, then release. | The accepted direction appears; release returns to neutral. |
| H4 | Exercise one existing face-button binding, then release. | The accepted button appears and releases cleanly. |
| H5 | Exercise one existing modifier/combo binding, then release all inputs. | The established mapping/profile output is preserved; release is clean. Record the actual binding tested. |
| H6 | Exercise an existing remap-disable binding if present in the preserved owner Config. | The established disabled operation remains disabled. If no such binding is present, record NOT_APPLICABLE with the captured Config evidence; do not invent one. |
| H7 | Disconnect and reconnect once. | Clean startup, stable dashboard/profile, ordinary controls and neutral unchanged. |
| H8 | Reboot once using the existing owner-controlled method. | The accepted profile and ordinary bindings return without stuck input or connection failure. |
| H9 | Connect in the owner's ordinary supported USB gameplay context, then exercise one existing direction and face button with releases. | Stable connection and established expected output. Record host/backend and actual observations; no OS-wide claim. |
| H10 | Capture persisted Config again in Configurator mode. | Raw payload exactly equals the pre-test backup. |

For H2/H3/H9, issue each press, release or context switch as a separate action;
the table groups the evidence requirements and is not a batch instruction.
Missing required context or a required physical route remains an evidence gap.

## Config preservation and restoration

A no-write test is preferred when it covers the required valid bindings. If
post-test raw Config exactly equals the pre-test backup, record restoration as
verified without a write. If an authorized valid write is needed, use only the
prevalidated byte-exact original Config and the existing generic serial tool.
Do not submit a novel payload, bypass its binding guard, or claim that its
success message alone proves byte equality or live behavior.

```text
python3 tools/glyph_serial_config_tool.py --write --artifact <extracted-config.json> --port <port> --backup-out <fresh-prewrite.json>
python3 tools/glyph_serial_config_tool.py --read --port <port> --backup-out <post.json>
```

Require explicit write success where used, immediate raw byte/hash equality,
then one owner-controlled reboot and a separate exact readback with the same
pre-test bytes/hash. Restore the normal gameplay mode and verify a stable
profile, ordinary direction/button response and clean neutral. Restoration
failure is the first recovery priority regardless of earlier observations.
Use only the owner-controlled existing rollback procedure and verified accepted
UF2 if needed. Preserve unexpected stored bytes and observations.

## Required human report and processor handoff

The human report must state:

- Full F SHA and exact preserved artifact SHA-256 used; pre-update rehash,
  byte size, manual update method and device-reported firmware identity.
- Tester, timestamp, controller model/revision, backend/host/adapter, profile,
  and the pre-test Config byte count/hash plus preserved backup location.
- Expected and observed result for each H1–H10 row, actual bindings tested,
  any NOT_APPLICABLE reason supported by Config, and every anomaly or omission.
- Immediate and post-reboot final raw Config equality, recovery/rollback steps,
  final controller state, and whether the required GameCube and USB rows ran.
- Physical invalid-binding submission: NOT_TESTED / HOST_ONLY; Nunchuk:
  NOT_TESTED. These excluded observations do not become physical PASS.

The Hardware Evidence Processor separately validates the exact pair, protocol,
source correspondence and complete required rows. It records PASS, FAIL, PARTIAL
or INCONCLUSIVE honestly. No PASS/result JSON is created before that report.
Source-free independent review precedes source-free processor evidence; only
then may separately reviewed source integration and accepted-transition catalog
publication occur. F, preserved artifact and this reviewed protocol stay frozen.
