# GP-CONFIG-005 Prior Inconclusive Persistence Event - 2026-09-17

Classification: `INCONCLUSIVE_PERSISTENCE_EVENT`

This record preserves the earlier GP-CONFIG-005 physical attempt separately
from the fresh acceptance run. It is historical evidence, not a PASS and not a
component of the later PASS correspondence.

## Preserved Inputs And Results

- Candidate Git SHA:
  `437f87e8086a50f0dfbd834176b80d245c1ed307`
- UF2 SHA-256:
  `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44`
- Original capture:
  `local_backups/gp-config-005-operator/captured-config.json`
- Rejection result:
  `local_backups/gp-config-005-operator/rejection-result.json`
- Interrupted valid-update result:
  `local_backups/gp-config-005-operator/valid-update-result.json`
- Post-drift capture:
  `local_backups/gp-config-005-operator/post-drift-config.json`
- Detailed preserved diagnosis:
  `local_backups/gp-config-005-operator/drift-diagnosis-20260918.md`

The original capture was 4202 bytes with SHA-256
`26919308427aa081633b0a40c0c83c5762ba9edf35eb912b901e9fa847a4dd84`.
The post-drift capture was 3969 bytes with SHA-256
`fb70c955b7e9813cb730a4749bbfc8dfe4fc5fb3b99b7ecacaafc329a1db8855`.
An offline source-backed probe established that the latter payload is
byte-for-byte identical to the candidate's compiled Glyph default config.

The earlier rejection suite recorded seven mechanically expected
`CMD_ERROR` responses with responsive device-info follow-ups. The subsequent
valid-update result stopped on a serial timeout. Its old `sent: false` field
does not establish that no serial write occurred because the then-current
transport returned only after writing and waiting for a response. The record
does not locate the timeout at a specific transaction stage.

## Bounded Interpretation

The source-supported persistence path makes an interrupted/truncated write,
later boot-time load failure, and compiled-default rewrite plausible. The
preserved evidence does not prove that sequence, establish whether or when a
valid SetConfig write began, or locate an exact persistence-failure window.
The exact compiled-default identity is not evidence that a rejected candidate
value became live or persisted.

The original config was later restored and verified by exact immediate and
post-reboot persisted readback before the fresh acceptance attempt. That
recovery does not convert this event to PASS or establish disk rollback,
atomic persistence, power-loss safety, or recovery guarantees.

The fresh run in `gp_config_005_hardware_result_2026-09-17.md` supersedes this
event only as the current acceptance attempt. This historical record remains
separate and must not be merged into the fresh run's mechanical results.
