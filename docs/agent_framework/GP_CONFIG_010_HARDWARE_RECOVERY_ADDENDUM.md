# GP-CONFIG-010 13-Ultimate hardware recovery addendum

Protocol version: `GP_CONFIG_010_HW_RECOVERY_V1`

This source-free addendum normatively incorporates
`docs/agent_framework/GP_CONFIG_010_HARDWARE_PROTOCOL.md` version
`GP_CONFIG_010_HW_V1`. It replaces only that protocol's current-default-mode
test stimulus with the bounded owner-directed recovery stimulus below. The
exact candidate, artifact custody, physical observation, reconnect, result,
independent evidence-processing, and no-merge gates remain in force.

## Exact immutable firmware identities

- Work order: `GP-CONFIG-010`
- Candidate branch: `glyph/gp-config-010-mode-activation-capacity`
- Candidate Git SHA: `f4771e17430fd1ea3f1e3e5339a83dfe648290a3`
- Candidate base: `28426e4ba4763a99f0ca13491c023af77665c79c`
- Candidate tree: `e18a7496125bf485a179d9b8e08f1f47f5090b80`
- Preserved artifact: `local_backups/hardware-artifacts/f4771e17430fd1ea3f1e3e5339a83dfe648290a3/9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a/firmware.uf2`
- Artifact SHA-256: `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`
- Expected size: `791040` bytes
- Accepted rollback candidate: `f657715b26d26587a931074ce7dd12c698785290`
- Accepted rollback artifact: `local_backups/hardware-artifacts/f657715b26d26587a931074ce7dd12c698785290/00dc75b65a080830131c3c260558d4daeff45bb528e43d196b8ad94fcd06f451/firmware.uf2`
- Rollback SHA-256: `00dc75b65a080830131c3c260558d4daeff45bb528e43d196b8ad94fcd06f451`
- Rollback expected size: `792064` bytes

No rebuild, source edit, rebase, replacement candidate, or integration-build
substitution is permitted.

## Owner-original backup gate

Before any firmware flash or persisted mutation, enter the existing
Configurator backend and use its source-supported `CMD_GET_CONFIG` path. Here,
"raw Config payload" means the protobuf `Config` message bytes returned as the
command payload, excluding command byte and COBS transport framing.

Preserve in one timestamped recovery directory:

- the exact raw payload bytes and a base64 representation;
- decoded structured JSON;
- payload byte length and SHA-256;
- UTC timestamp, port, device/firmware identity response, and operator log.

Decode the captured bytes and deterministically re-encode them. Require exact
byte equality. If capture, decode, re-encode, or preservation fails, stop before
any mutation. Restoration must later send these exact captured bytes; JSON
reconstruction is not an acceptable restore source.

## Post-flash preservation gate

After custody verification, the owner may manually flash only the exact
GP-CONFIG-010 artifact. Re-enter Configurator mode and capture the persisted
Config before any temporary write. Require exact byte equality with the
owner-original raw payload. Unexpected drift stops the run.

## Temporary test stimulus

Derive the temporary payload exclusively from the captured owner-original
Config. Exactly one currently accepted Ultimate `GameModeConfig` must be
unambiguous; otherwise stop. Clone it into exactly thirteen entries at indices
0 through 12, name them `Ult01` through `Ult13`, keep every mode
`MODE_ULTIMATE`, and make each GameCube-applicable. GameCube-only applicability
is permitted.

Every cloned Ultimate field must equal the owner source entry except:

- `name`;
- `activation_binding`;
- `applicable_backends`.

Every unrelated top-level Config field, communication backend config, custom
mode, keyboard mode, RGB table, and other configuration value must equal the
owner-original capture.

Use thirteen unique, non-empty activation bindings mapped by
`config/glyph/glyph_mk6/include/matrix_definition.hpp`,
`config/glyph/glyph_mk6/include/button_positions.hpp`, and the current physical
layout evidence. Exclude menu, configurator, bootloader, reset, update, and
manual-debug controls and exclude current backend activation bindings. Prefer
single buttons. If chords are unavoidable, the complete binding set must be a
pairwise antichain: no binding is a subset or superset of another. Guessed,
unavailable, empty, duplicate, or ambiguous bindings stop the run.

Before device access, preserve a machine-readable plan and human-readable diff
and prove:

1. exactly thirteen entries at indices 0..12;
2. exact ordered names `Ult01`..`Ult13`;
3. every mode is Ultimate and GameCube-applicable;
4. every binding is source-mapped, non-empty, mask-representable, unique, and
   non-ambiguous;
5. clone equality outside the three permitted fields; and
6. equality of every unrelated Config field.

## Temporary write and persistence gates

Immediately before writing, perform `GET_CONFIG` and require exact equality
with the owner-original payload. Use only the existing custom backend
`CMD_SET_CONFIG` command and framing path. Record the ordered Revision-2
transaction stages from prewrite read through follow-up read. Require a full
host write, decoded `CMD_SUCCESS`, follow-up `GET_CONFIG`, and exact byte
equality with the intended temporary payload.

Any timeout, ambiguous write completion, unexpected response, or readback
mismatch stops without automatic retry. Preserve the evidence already obtained.

After one owner-performed reboot/disconnect/reconnect into Configurator mode,
rediscover the port and require `GET_CONFIG` byte equality with the intended
temporary payload before GameCube testing.

## Physical test

After connecting through the normal GameCube cable/adapter:

1. Require the Profile menu to show `Ult01` through `Ult13` in order.
2. Exercise each row once, with release before the next row. Immediately before
   each row, show the owner the profile, index, exact button/chord, and physical
   location.
3. Record expected and observed profile name, connection stability, miniscreen
   stability, ordinary directional response, and `PASS`, `FAIL`, or
   `INCONCLUSIVE` for every row.
4. Explicitly identify `Ult11`/index 10, `Ult12`/index 11, and `Ult13`/index 12
   as the former-overflow-boundary observations.
5. After all rows pass, select `Ult13` and perform only representative Ultimate
   directional, face-button, modifier, display, stuck-input, and connection
   sanity. Do not infer Smash angle or radius.
6. Perform a normal power-cycle/reconnect, require GameCube operation and all
   profiles still visible, and reselect `Ult13`.

Nunchuk remains `NOT_TESTED`. Full modifier-table testing in all thirteen
clones is not required. If a discrepancy makes coordinate validation necessary,
publish the complete expected raw/miniscreen table first.

## Mandatory exact recovery

Whether the run passes, fails, or is inconclusive, reconnect in Configurator
mode if hardware state makes writing safe. First capture the current temporary
payload for evidence. Then send the exact captured owner-original protobuf
payload bytes.

Require `CMD_SUCCESS`, immediate `GET_CONFIG` byte equality and original
SHA-256, one reboot, and a second `GET_CONFIG` byte equality and original
SHA-256. Any mismatch stops and makes configuration recovery the priority.
Do not proceed to firmware rollback until exact Config restoration is proved.

After exact Config restoration, the owner may manually flash only the exact
accepted GP-X1-002 custody artifact. Reconnect normally through GameCube and
confirm ordinary Ultimate auto-selection, LT5 X1 activation, at least one
visible value from the accepted X1 table, normal profile/menu state, and no
unexpected disconnect. This bounded sanity check does not reopen X1 acceptance.

## Evidence and disposition

The prior evidence
`git-json:6c858622657b70c8dc964db0cd4ffaac6ca4fb9f:docs/calibration/fixtures/gp_config_010_hardware_evidence_2026-09-21.json`
remains historical `INCONCLUSIVE` evidence and must not be overwritten or
reinterpreted.

Create a fresh evidence identity for this run. It must include both firmware
identities, owner-original and temporary payload hashes, all thirteen exact
bindings and observations, explicit indices 10..12, representative sanity,
power-cycle/reconnect, exact Config restoration before and after reboot,
GP-X1-002 rollback sanity, owner observations, anomalies, and Nunchuk
`NOT_TESTED`. Only complete human observations may support PASS, and PASS is
subject to a fresh independent Hardware Evidence Processor before any merge.

## Stop conditions

Stop on any candidate, artifact, custody, backup, re-encode, post-flash
preservation, intended-diff, binding, write-stage, response, readback,
reboot-persistence, overflow-boundary stability, restoration, or rollback
identity mismatch. Do not automatically retry an ambiguous write. Do not alter
firmware, schema, persistence architecture, modifiers, source-owned stick
tables, GP-VAL-011, Nunchuk status, gameplay semantics, or root-cause status.
