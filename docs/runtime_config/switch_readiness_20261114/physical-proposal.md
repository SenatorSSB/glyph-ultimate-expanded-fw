# Owner-guided physical proposal — recovery correction

Pending supervisory acceptance of the separate
[post-Stage-H restoration tooling](../switch_recovery_20261114/README.md) and
separate explicit owner approvals below. This proposal does not authorize device
access. The firmware source and retained accepted UF2 remain unchanged. Stages G/H
stay closed. The old managed-root restoration operator is not reusable: it pins
previous firmware,28 profiles/five rows/generation230/sequence2/Stage-F hashes.
Do not modify its guards or reuse its one-shot identity.

1. In the eventual owner-guided session, verify the complete original27-profile
   baseline in XInput using the existing approved read-only mechanism for the
   previously installed combined firmware. Compare complete Config, ordered
   directory, every wrapper, healthy STATUS2/STATUS4 and runtime identity against
   retained Stage-H evidence. Required Config hash is
   `b3f03f33c01111eceda1a602cdb30f6e4d003375f495f20008d5a529b804c8b8`, four rows,
   sequence6, incarnation1, generation234, high-water17293822569102712138,
   USB selector1, GameCube default KazTest5/53 and XInput identity53/revision1.
   Stop on drift. Retain the existing controller-specific ledger and all claims.
2. Verify source `0b9ef3afd1834ac7832871bca0651b67147840a2` and exact retained UF2
   `6eb992cda7392b6fb5a52ab48989ef10c94fc97ec77fd733360a863e55cd8a83` (1,327,104
   bytes). Run the retained candidate verifier; ensure original firmware custody,
   complete private snapshots, RT2 recovery instructions and accepted new helper
   are available. Never substitute a rebuild.
3. Obtain separate explicit owner approval to install that exact image by the
   supported non-destructive UF2 procedure without resetting storage. Record the
   exact controller, artifact and method. This approval is not Switch-selection
   or restoration approval.
4. Under that approval only, use the previously supported RP2040 BOOTSEL/UF2
   procedure to install the verified application UF2. Do not use a nuker, erase,
   reset-storage image or any automatic rollback. Preserve the existing store.
5. Confirm ordinary XInput menu/button operation, runtime identity53/revision1 and
   complete preservation. With a separate read approval, the new helper's
   `observe --selector 1` checks the candidate's exact XInput Config, healthy
   store, all27 original entries and complete wrappers. Compare to Stage-H.
6. Obtain separate explicit owner approval for the saved Switch USB selection
   (index1->4). Avoid unrelated menu/profile edits or lifecycle transactions.
7. Test Switch-on-Mac local menu/input liveness with timestamped press/release and
   harmless navigation observations over multiple frames. Record host enumeration,
   receiver state and any observed IN polling. Avoid saved edits. A responsive
   Mac menu is local liveness evidence; it does not independently prove HID
   readiness or successful report delivery. A separate compatible polling receiver
   and correlated received reports/application inputs are needed for that claim.
   Do not claim Nintendo Switch console compatibility without a compatible receiver
   and actual evidence. Do not make an unapproved reconnect or destination change.
8. If needed, use the previously demonstrated owner-guided RT2 recovery path to
   regain Configurator access. Do not rely solely on a responsive patched menu.
   Stop if access cannot be recovered. Under read-only approval run the new helper's
   `observe --selector 4`: capture current Config, STATUS2, actual package STATUS4,
   full directory and all27 wrappers. Compare observed bytes explicitly with the
   prediction; any unexpected unrelated field, identity, guard, health or wrapper
   difference stops before preparation/write. Prediction alone is not observation.
9. Prepare the immutable restoration plan using that fresh observed snapshot, the
   original Stage-H Config and the exact existing ledger. Predicted Switch current
   hash is `b4f242caec602cdc75718ad9805bc847de456f1298ed5be82f632fdb89180028`;
   target is the original Stage-H hash in step1. The only intended change is
   `default_usb_backend_config:4->1`. Obtain exact separate restoration approval
   after presenting the observed guards, complete plan and frame hash, current
   endpoint/controller and expiring exclusive-session commitment. No competing
   writer or local menu edit is allowed during execution.
10. Execute the reviewed bounded helper once under that exact approval. Its durable
    new operation claim precedes serial access; full read-only preflight precedes
    at most one SET_CONFIG. Require the sequentially correlated empty success,
    complete target readback and full27-profile postflight. Any uncertainty is
    terminal: retain the claim/evidence, stop and seek supervision. Never retry,
    reset, erase, guess a Config, or automatically roll back.
11. Confirm all27 original profiles, ordered directory/wrapper bytes, all unrelated
    Config fields/receipts and original baseline hash remain intact. Verify expected
    unchanged incarnation/generation/high-water/sequence, GameCube default53 and
    ordinary XInput dashboard/buttons plus runtime identity53/revision1 after the
    separately guided normal boot. Record controller/host/receiver identities and
    timestamps. A successful host audit does not prove raw flash identity,
    power-loss durability, full installed-image attestation or console compatibility.

The independent source/host tests and exact approval formats are linked in the
recovery README. Hardware use remains gated; no device action was performed for
this correction.
