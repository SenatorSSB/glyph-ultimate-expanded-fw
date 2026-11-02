# Proposed Kazuya v5 guarded CREATE work order

Disposition: **PROPOSED — NOT READY — owner/Curator device authorization required**. This is a one-operation packet, not authority to contact a controller.

## Immutable payload

CREATE one separately named v5 test record using wrapper `72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87`, body `30bd0b711e3973527e1d48b59af08aa5c71b6ef8f2dc5b9d932932420d9c0f6f`, protobuf JSON `54821170ddf4916f310e254c09a06f78d6ece8e8304f030761c3d03d5c6a8828`, source blob `64c2825605082701b9252832149535c82ebb7fc5`, schema 5 and preprocessing hash `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.

Future approval must bind a controller fingerprint, fresh generation, approved test name/rank and returned assigned ID. These are blank now: historical IDs/generations/tokens are not live authority. Suggested metadata is `KazTest5`, rank owner-chosen.

## Operator algorithm after approval

1. Open only the approved controller; journal operator, firmware/backend compatibility, health, generation, transaction token and native-record inventory.
2. Back up raw Config and inspected records. Read/hash protected ID27 Ultimate/Pikachu and ID51 KazTest4; prove active reference. Stop for mismatch, unknown native record, degraded health or irrecoverable state.
3. Rebuild and compare every immutable identity above. Stop on mismatch. Scope is CREATE only: no UPDATE, RENAME, DELETE, Config write, active-selection write or flash.
4. Submit one checked CREATE using fresh generation/token fences. Journal request, assigned ID and response; never reuse a stale fence.
5. Read assigned record immediately; require exact wrapper/body, approved name/rank/revision, healthy transaction state and unchanged ID27, ID51, unknown records and active reference. Any discrepancy aborts.
6. Retain KazTest4 as rollback. New-profile selection/gameplay requires another explicit owner approval. Cleanup/two-profile work is separate after replacement acceptance.

## Required authorization to become READY

Explicit owner/Curator approval must name controller fingerprint, test name/rank, allowed CREATE invocation, preflight witnesses, rollback operator and abort authority after fresh inventory confirmation. Until then this packet is non-executable.
