# GP-CONFIG-010 reconnect-completion protocol

Protocol version: `GP_CONFIG_010_RECONNECT_COMPLETION_V1`

This source-free protocol authorizes one bounded completion retest for the
existing GP-CONFIG-010 H3 candidate. It normatively incorporates
`docs/agent_framework/GP_CONFIG_010_HARDWARE_RECOVERY_ADDENDUM.md` version
`GP_CONFIG_010_HW_RECOVERY_V1` for custody, Config transport, transaction,
evidence, and recovery mechanics, but replaces its full thirteen-row physical
activation matrix and final reconnect step with the narrower procedure below.

## Immutable identities and admitted prior evidence

- Candidate Git SHA: `f4771e17430fd1ea3f1e3e5339a83dfe648290a3`
- Candidate base: `28426e4ba4763a99f0ca13491c023af77665c79c`
- Candidate tree: `e18a7496125bf485a179d9b8e08f1f47f5090b80`
- Preserved UF2 SHA-256:
  `9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`
- Preserved UF2 size: `791040` bytes
- Accepted rollback candidate:
  `f657715b26d26587a931074ce7dd12c698785290`
- Accepted rollback UF2 SHA-256:
  `00dc75b65a080830131c3c260558d4daeff45bb528e43d196b8ad94fcd06f451`
- Accepted rollback UF2 size: `792064` bytes
- Prior evidence:
  `git-json:d69b1694c84f803c278b532dbd20a8725eb17a81:docs/calibration/fixtures/gp_config_010_hardware_evidence_2026-09-22_recovery_13mode.json`

The prior evidence remains admissible for this unchanged candidate/artifact.
Its thirteen activation PASS observations, including indices 10, 11, and 12,
and its representative Ult13 sanity PASS are not repeated or downgraded. Do
not repeat the full matrix unless a new discrepancy directly calls those
observations into question. Any such discrepancy stops this bounded run for
independent adjudication.

No build, rebuild, source edit, patch, rebase, replacement artifact, or
integration-build substitution is permitted.

## Fresh state capture and exact temporary stimulus

Before any controller mutation, create a new timestamped evidence directory,
discover the serial port, capture read-only identity/status, and preserve the
complete owner Config as raw protobuf payload plus decoded representation.
Record its length and SHA-256 and require supported deterministic
decode/re-encode byte equality. The current owner Config must be exactly 4201
bytes with SHA-256
`f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.
Any difference stops before mutation.

Reverify both preserved UF2s as regular non-symlink files with the exact sizes
and hashes above. The owner may then manually flash only the exact
GP-CONFIG-010 UF2. After reconnecting in Configurator mode, require GET_CONFIG
to equal the fresh owner backup byte-for-byte before any temporary write.

Recreate the prior temporary Config without redesign:

| Profile | Index | Activation |
| --- | ---: | --- |
| Ult01 | 0 | LF6 |
| Ult02 | 1 | LF7 |
| Ult03 | 2 | LF8 |
| Ult04 | 3 | RF9 |
| Ult05 | 4 | RF10 |
| Ult06 | 5 | RF11 |
| Ult07 | 6 | RF12 |
| Ult08 | 7 | RF13 |
| Ult09 | 8 | RF14 |
| Ult10 | 9 | RF15 |
| Ult11 | 10 | RF16 |
| Ult12 | 11 | LT3 |
| Ult13 | 12 | LT4 |

Require exactly thirteen `MODE_ULTIMATE` entries, exact ordered names
`Ult01` through `Ult13`, GameCube-only applicability, and clone equality with
the freshly captured owner Ultimate profile outside name, activation binding,
and applicability. Preserve all unrelated Config fields, modifier tables, X1,
backend behavior, and firmware. Offline-validate and preserve a new plan and
intended-only diff. The deterministic intended payload must be exactly 6691
bytes with SHA-256
`02a456e4868d659e6c54bff7f2b5d26d069755496089c4ab2cd266b084e5e589`;
otherwise stop before write.

Write only through the existing tested `CMD_SET_CONFIG` path. Require complete
transaction-stage evidence, `CMD_SUCCESS`, exact immediate GET_CONFIG
readback, exact decoded intent, and one Configurator-mode reboot with exact
byte-for-byte temporary-payload persistence. A timeout, ambiguous completion,
or mismatch stops without automatic retry.

## Required completion observations

Give the owner one physical instruction at a time.

1. Move from Mac Configurator mode to the normal GameCube cable/adapter path.
   The first startup attempt must pass the Glyph logo normally. If it freezes
   or remains stuck, stop hardware acceptance immediately; do not cycle until
   it eventually works.
2. Only after the first startup passes, open the Profile menu and record count,
   order, missing entries, and extras. Require exactly `Ult01` through `Ult13`
   in order.
3. Return to the normal dashboard as needed, press and release LT4, and require
   exact `Ult13` display for config index 12, stable connection and miniscreen,
   and ordinary directional response.
4. With Ult13 active, check one horizontal direction, one vertical direction,
   one representative face button, LT5/X1, release to neutral, no stuck input,
   and no disconnect. This is operational sanity only and does not re-accept
   X1 or add gameplay claims.
5. After the required first startup, perform exactly three additional clean
   consecutive normal GameCube disconnect/reconnect startup cycles. For every
   cycle record logo passage and the selected profile/dashboard. LT4-to-Ult13
   may be repeated on the final cycle. Do not expand this into an endurance
   test.

If the frozen/stuck Glyph logo recurs on the required first startup or any of
the three additional controlled cycles, stop immediately and preserve the
recurrence. The expected disposition is `FAIL` unless the evidence clearly
proves an unrelated external cause. Later successful retries must not hide the
recurrence. Another genuinely ambiguous external issue may be
`INCONCLUSIVE` only with its exact reason.

If every required observation passes without a repeated freeze, the operator
may record only provisional `PASS`. Only a fresh independent Hardware Evidence
Processor may combine this completion record with the prior thirteen-entry
record and publish hardware PASS.

## Mandatory recovery and handoff

Regardless of PASS, FAIL, or INCONCLUSIVE, reconnect in Configurator mode when
safe and capture the temporary state. Restore the exact raw owner Config
captured at the beginning of this run. Require successful write, immediate
exact hash equality, one reboot, and exact post-reboot hash equality. Any
restoration failure stops all other work and makes recovery the priority.

Only after exact Config restoration may the owner manually flash the exact
accepted GP-X1-002 UF2. Reconnect normally through GameCube and confirm
Ultimate auto-selection, normal connection, LT5 X1 activation, one
representative accepted X1 coordinate, release to neutral, and no stuck input
or disconnect. Do not rerun full X1 acceptance.

Fresh evidence must reference both the prior thirteen-entry record and this
completion run, including every reconnect cycle and all restoration proof.
On processed PASS, a fresh Implementation Supervisor alone may evaluate exact
candidate integration under current correspondence rules. Inability to
preserve hardware-critical candidate changes exactly stops integration; do not
recreate equivalent firmware. The original GP-CONFIG-010 UF2 remains the
accepted physical artifact.

## Exclusions

This protocol authorizes no firmware build or patch, source/schema/default
change, runtime-loaded profile/config product capability, persistence design,
device/WebSerial/protobuf/backend write addition, flashing automation,
modifier-table or X1 change, GP-VAL-011 work, Nunchuk claim, gameplay-semantic
inference, root-cause claim, evidence overwrite, or pre-PASS merge.
