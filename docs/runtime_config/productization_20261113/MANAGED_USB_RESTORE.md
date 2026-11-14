# Managed-root USB destination restoration

This isolated host operator is only for the owner's 2026-11-14 Stage F
restoration on combined firmware `84556d904f067bda5a101e6297689239ecd04aae`.
It changes the **one-based backend index** `default_usb_backend_config` from
4 (Switch, backend enum 7) to 1 (XInput, backend enum 2). It is not a generic
Config editor or a Switch repair. The existing root-2 `--native-packet` guard
is unchanged.

## Frozen scope

The exact current and intended 419-byte Config hashes are respectively:

```text
42f7c923047887507fd03539f16d91b113422e8245c452aaeab5f81d923f776c
4f8e05b4780bae18c26b5bebf787934df4507cb88a2c353856b413057a34043e
```

The target must equal the retained original XInput bytes exactly. Root format
3, store format 1, managed format 1/sequence 2, incarnation 1, generation 230,
high-water 17293822569102712134 and the 28-entry snapshot are fixed guards.
The primary selector stays 2; backend default rows stay 3/3/1/3. GameCube
continues to reference row 3/profile 53. Every other Config field, including
managed rows, RGB, receipts and migration evidence, is preserved by exact-byte
comparison. No ProfileStore mutation is sent.

## Source support and limits

`ConfiguratorBackend::PrepareSetConfig` rejects recovery/fences/uncertainty.
The handler reloads durable Config, preserves firmware-owned root/reference/
migration receipts, validates the full proposal and referenced engines, and
calls the ordinary Config save path. `ProfileStore::BeginOrdinaryConfigWrite`
guards managed ownership, rows, RGB and receipts. An unchanged receipt tuple
permits an unrelated default save. There is no root-2-only restriction in this
firmware path; that restriction belongs to the older host helper.

Legacy SET_CONFIG has **no atomic generation fence or transaction token**.
The empty command-6 acknowledgement is correlated by a single exclusive ordered
serial session, not by a token. Close other serial clients, leave the controller
in its established Configurator access, and do not touch controls while the
operator runs. Fresh STATUS 2/4 and byte-exact GET immediately before SET reduce
the race but cannot remove it. DeviceInfo corroborates the advertised build;
it does not attest every byte of installed firmware. The UF2 hash is independent
local artifact evidence. API-visible preservation does not establish raw NOR
identity, power-loss safety or complete restoration capability.

## Offline preparation and tests

Use Python with existing `pyserial`, `protobuf` and `grpc_tools` dependencies.
All commands run at the reviewed Glyph repository root. Private snapshot data
stays outside Git.

```sh
"$GLYPH_PYTHON" -B tools/test_glyph_managed_usb_restore.py \
  --snapshot "$PRESERVED_CURRENT_SNAPSHOT" \
  --xinput-baseline "$ORIGINAL_XINPUT_CONFIG_PB" --uf2 "$EXACT_RETAINED_UF2"

"$GLYPH_PYTHON" -B tools/glyph_managed_usb_restore.py prepare \
  --snapshot "$FRESH_CURRENT_SNAPSHOT" \
  --xinput-baseline "$ORIGINAL_XINPUT_CONFIG_PB" \
  --ledger "$EXISTING_RESOLVED_SESSION_LEDGER" --out "$NEW_EPISODE"
```

`prepare` is offline. It independently constructs the one-field change and
requires exact equality with the retained baseline. Its plan binds the Config
pair, full directory/wrapper hashes, endpoint and controller identity, guards,
fixed candidate, dependencies and canonical persistent ledger path.

Before preparing the final approval, obtain a **new complete read-only snapshot**
with the reviewed Senscope lifecycle `inspect` operator. Compare all 28 wrappers,
ordered directory metadata and complete current Config against the preserved
failure baseline. Do not treat historical hashes as fresh observations.

The separate `tools/check_glyph_managed_usb_restore_source.py` proof compiles
only a host harness. It copies the existing package test harness and adds a
command-4 framing option; production firmware sources are unchanged. Supply
`--repo` (pinned source), `--dependency-repo` (matching source with existing host
dependencies), `--seed-namespace` (a valid retained synthetic managed namespace),
`--framework` (pinned Arduino-Pico3.6.3) and a new `--out` directory. It verifies
all firmware-facing inputs match, then exercises real ConfiguratorBackend,
PacketIO, Persistence, ProfileStore, validators and LittleFS under ASan/UBSan.
The synthetic fixture uses its own backend indices; it complements the exact
private 419-byte pair validator proof and does not reconstruct physical NOR.

## Exact owner approval and execution

Present the plan/frame hashes, candidate, controller, current/target hashes,
one-field change, preserved data and residual whole-Config risks to the owner.
After explicit confirmation, retain that verbatim decision and create an approval
JSON with exactly these fields:

```json
{
  "approved": true,
  "planSha256": "EXACT_PLAN_FILE_SHA256",
  "frameSha256": "EXACT_PLAN_FRAME_SHA256",
  "port": "EXACT_APPROVED_CURRENT_PORT",
  "usbSerial": "EXACT_APPROVED_PRIVATE_USB_SERIAL",
  "approvedAtUtc": "OWNER_APPROVAL_TIME_WITH_TIMEZONE",
  "expiresAtUtc": "AT_MOST_15_MINUTES_AFTER_APPROVAL",
  "exclusiveConfiguratorSession": true,
  "ownerReference": "DURABLE_OWNER_DECISION_RECORD"
}
```

**DEVICE ACCESS — ONE AUTHORIZED CONFIG MUTATION:**

```sh
"$GLYPH_PYTHON" -B tools/glyph_managed_usb_restore.py execute \
  --plan "$NEW_EPISODE/plan.json" --approval "$EXACT_WRITE_APPROVAL" \
  --uf2 "$EXACT_RETAINED_UF2" --exclusive-configurator-session
```

The operator burns an exclusive, fsynced controller/operation-scoped claim in
the existing ledger **before opening the port**. It never removes this claim,
even after preflight refusal. A different episode, approval or request token
cannot replay through the same ledger. Never delete the claim or substitute a
ledger to retry. The serial constructor uses 115200 baud, DTR true, RTS false
and exclusive access; it does not use 1200-baud reset or reboot commands.

It checks advertised DeviceInfo, production STATUS admission, protocol-4 guards,
then exact saved Config. It persists intent, payload, hashes and raw frames;
attempts at most one SET; requires one empty acknowledgement and exact saved
readback; and repeats healthy STATUS/guard checks. A short write, timeout,
extra/missing/partial response or any mismatch is terminal. Missing acknowledgement
never means it is safe to repeat the write.

The operator's success is **Config readback verified**, not full profile or
physical startup acceptance. Follow with a new complete read-only lifecycle
snapshot and compare all 28 directory entries/wrappers and every Config field
against the approved target. Account for any discrepancy; do not compensate.
Only after preservation passes, guide an ordinary all-buttons-released Mac power
cycle if needed and record the owner-observed XInput dashboard separately.
Never retry Switch mode, flash, reset, erase, edit profiles or enter Stages G–H.

## Evidence

Keep the exact source commit, file/dependency hashes, test logs, independent
review, full preflight, plan, owner decision, approval, permanent ledger claim,
execution intent, raw TX/RX, acknowledgement, exact readback and full postflight.
Preserve the original Stage F failure and its later additive records unchanged.
