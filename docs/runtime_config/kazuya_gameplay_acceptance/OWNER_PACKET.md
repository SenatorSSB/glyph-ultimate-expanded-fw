# KGA-ID48-GC-R1 — stored Kazuya gameplay campaign

**PREPARED ONLY. Execute only after the owner sends the exact approval sentence
at the end.** Preparation selected no profile, accessed no controller, changed no
Config/ProfileStore/profile/source, and flashed no firmware. Gameplay NOT_TESTED.
This packet permits only the later normal selection of existing ID48, the bounded
manual tests below, normal return to ID27, and read-only preservation.

## Frozen campaign identity

Canonical inspected/live-verified: `bf6f1e2e6814c6b6f1eb710175a488961c8295e7`.
Source: `profiles/kazuya/Kazuya.profile.json`, Git blob
`542ef2607457b42f324d4962ed2bb543f317cd21`, file SHA-256
`8f28cdc430a8347cc193f7a8519f5a3e7a4f0ce49558ebb4f7ff26ca61219499`.
ID48, name Kazuya, revision1/schema5, encoding1/ABI1. Fresh offline compile and
validation reproduce these exact values (see [identity](IDENTITY.json)):

| Item | Bytes / SHA-256 |
| --- | --- |
| Protobuf wrapper | 1839 / `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8` |
| Native body | 1834 / `44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405` |
| Preprocessing | `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f` |
| Authored provenance | `09392756ec1fce89479e5008f4653b866f11e31254bec435a0c1c0edf2531ae7` |

Permanent ID27 Ultimate: wrapper1985 bytes,
`30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b`;
body1980 bytes, `ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee`.
Never reinstall, UPDATE, CREATE, delete, edit or reorder either profile.

Installed firmware remains exact candidate
`1de243c7bada73ba85843018058b4f66a06acdda`, tree
`5a25a83705a654480b8db805f20822f4d180d70f`, UF2 1046016 bytes, SHA-256
`a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b`.
No new build or flash. Runtime telemetry does not attest Git SHA/UF2.

Accepted infrastructure: native menu Ultimate → Kazuya; all SEL absent; menu
XInput/owner-observed GC/owner-observed USB Switch PASS; final full preservation
PASS. [Historical hardware adoption](../character_profile_menu/hardware_20261023/evidence.json),
[all24 preserved records](../character_profile_menu/hardware_20261023/preservation.json),
and [exact tested-source integration](../character_profile_menu/integration_20261023/README.md)
remain immutable. Their acceptance does not establish Kazuya gameplay.
The Kazuya README/host fixtures contain older preparation-time installation
statuses; the later installed-ID48 preservation evidence supplies current custody.

Source authorities: canonical Kazuya JSON/README, `tools/test_kazuya_profile.py`,
its host-results/verification/coordinate-evidence fixtures, and exact menu evidence.
Host tests are deterministic controller-output oracles. A gameplay session asks
whether those outputs produce acceptable in-game behavior. Do not reinterpret
their RF matrix or claim raw coordinates were measured by watching gameplay.

## Phase 0 — read-only preflight after approval

One operator and one exclusive serial client. Stop on any command error; never
automatically retry an uncertain operation. Fresh execution facts are the actual
matched unit/port, current runtime observations, Config bytes/CRC, complete
directory, references/defaults/ranks, incarnation/generation/high-water and
health/recovery state. Never substitute historical values for these reads.
No controller command is run during preparation.

After approval, use a dedicated Bash shell:

```bash
set -euo pipefail
ROOT='/Users/rasmus.pekkarinen/.codex/worktrees/character-menu-acceptance/glyph-ultimate-expanded-fw'
PY='/Users/rasmus.pekkarinen/.codex/worktrees/native-profile-menu-cleanup/glyph-ultimate-expanded-fw/.venv/bin/python'
PKT="$ROOT/docs/runtime_config/kazuya_gameplay_acceptance"
CHECK="$PKT/campaign_checks.py"
FROZEN="$ROOT/docs/runtime_config/character_profile_menu/packet_checks.py"
STORE="$ROOT/tools/glyph_profile_store_production_tool.py"
CONFIG="$ROOT/tools/glyph_serial_config_tool.py"
IDENTITY="$ROOT/tools/glyph_runtime_identity_tool.py"
"$PY" "$CHECK" verify
CAPTURE=$(mktemp -d '/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/kazuya_gameplay_R1.XXXXXXXX')
cp "$PKT/RESULT_TEMPLATE.md" "$CAPTURE/RESULTS.md"
cp "$PKT/TEST_MATRIX.json" "$CAPTURE/poses-unexecuted.json"
source "$PKT/capture_readonly.sh"
"$PY" -m serial.tools.list_ports -v
PORT='<fresh matched Configurator endpoint>'
export ROOT PY PKT CHECK FROZEN STORE CONFIG IDENTITY CAPTURE PORT
```

Have the owner enter Configurator through the established **normal** route.
Match the known physical controller's serial identity/location to the current
enumeration; a port string alone is insufficient. Do not use the prior unsuccessful
RT2-held attempt as the Configurator-entry procedure. If return through normal
XInput/menu/Configurator is needed, record the actual route and every selection.
Do not select Kazuya until preflight PASS. STOP on ambiguous unit, missing endpoint,
missing interpreter/dependency/pinned tool, unexpected firmware or recovery.
Do not download packages, repair tools, flash, or substitute a payload.

```bash
capture_all "$CAPTURE/preflight"
"$PY" "$CHECK" snapshot "$CAPTURE/preflight" --accepted
```

Expected: protocol2/mutation2 production STATUS; stable fresh fences within the
snapshot; Configurator identity; valid raw Config CRC; healthy store; recovery
and uncertainty clear; all references resolved and native preprocessing matches.
Both complete profiles exact; no SEL by ID or name; all24 records and metadata
match accepted final preservation; no new native record. The comparison also
requires the accepted Config/store fences unchanged before campaign start.
Any difference STOPs for reconciliation; do not silently adopt a new baseline.
This is not an instruction to restore historical bytes or write a token.

The capture script sends only STATUS, LIST, READ, Config read and identity read;
it captures all bounded LIST pages and every profile, with starting/ending STATUS.
The offline verifier never opens a device. Keep raw journals/Config private.

## Phase 1 — normal Kazuya selection, then Training setup

Only after preflight PASS and this packet's explicit approval:

1. Exit Configurator normally and use **Glyph → GameCube backend → GC adapter →
   Nintendo Switch → Super Smash Bros. Ultimate**. No XInput or USB Switch
   gameplay acceptance is required.
2. Open `.Profile`; require native entries Ultimate then Kazuya, no runtime labels
   or SEL entries. Unexpected entries or freezes mean STOP.
3. Select **Kazuya**, allow the normal committed selection/reboot, verify ordinary
   responsiveness. Record this selection separately, including actual existing
   zero-based Config context row and GameCube backend3. Do not use a guessed row
   or the one-based runtime wire context. Source: `include/core/ProfileSelection.hpp`.
4. Use Kazuya in Ultimate Training Mode, a stable stage/position, passive or
   otherwise recorded controlled opponent. Record game version and controls/button
   assignments, player/facing/position, stage and opponent settings. Use a visible
   input display when useful and available; it is not raw-coordinate measurement.

Normal profile selection persists Config destination/reference and reboots; it
does not mutate the stored profile or store generation. No checked `set-reference`
or other direct Config write is authorized. Record observable menu/reboot behavior;
Configurator identity cannot prove raw GameCube runtime identity.

Timing-sensitive recognition: try the owner's normal manual command setup/order,
record it, repeat enough to assess consistency, and distinguish electric/WGF or
other actual actions. A held pose specifies controller state, not a complete
automated move sequence. Do not invent frame thresholds or blame a failure on
mistiming without evidence. Record deterministic expectation, actual human
execution and game result separately.

## Human test workflow — six groups, small batches

The [177-pose matrix](TEST_MATRIX.json) supplies stable IDs, starting state,
physical held buttons, transition order, LF side, expected native table/effect,
command digital contribution, purpose and exact observation fields.
No binary-mask interpretation is required. All begin NOT_TESTED.
The agent presents **one batch of at most eight poses** at a time, waits for actual
owner results, and saves them privately before continuing. For example:

```bash
"$PY" "$CHECK" show 1 --batch 1 > "$CAPTURE/group1-batch1.json"
```

Present that batch in plain language. Advance `--batch` within that group only
after saving observations; never issue a loop that asks the owner to perform all
poses. Each group ends with an owner checkpoint: results saved, unresolved failures
listed, controller state understood, safe to continue. Preserve skipped IDs/reasons.
No reported FAIL may be rewritten as PASS.

| Group | Poses / batches | Procedure and checkpoint |
| --- | --- | --- |
| 1 ordinary controls | 24 / 3 | SMOKE: four LF directions and four diagonals; RF1 A/RF2 B/RF3 X/RF10 Y; RF6 Z, LT1 L, RF16 R, LT2 L+R; RT3 left/RT4 right/RT2 down/RT5 up C-stick; MB7 Start/MB6 Select/MB5 Home/MB4 Capture as relevant. Record system actions separately, return safely to Training. Any serious control regression: return to Ultimate and STOP before commands. |
| 2 core commands | 24 / 3 | DOWN/DIAG: RF7, RF8, RF7+RF6, RF7+RF6+RF5, RF8+RF6, RF8+RF6+RF5, RF8+RF7, RF8+RF7+RF5; each LF3, neither, LF1. Record crouch-dash, EWGF/WGF-purpose, Hell's-Gate-purpose and Spinning Demon recognition; assess unwanted A/B/Z moves. |
| 3 neutral/back/composition | 24 / 3 | NEUTRAL/DOWNBACK/COMPOSE: none, RF5, RF6, RF5+RF6, RF7+RF5, RF8+RF5, RF8+RF7+RF6, all four RF; all three horizontal states. Test while-rising/CDC cancel, non-Shield down-back, and ordinary RF5/RF6 precedence. Decide no-horizontal fallback consequences per relevant command. |
| 4 Shield and release | 33 / 5 | Five ordinary LT2 directional/diagonal checks plus LT5/RT1 modifier diagonals on both sides, then RELEASE A/B, all three horizontal states. Sequences must stay contiguous across batches. Record every step, Shield retention, roll/spot-dodge, crouch/movement and owner acceptability; repeat whole sequences. |
| 5 LT2 overlap | 36 / 5 | All12 RF command states under broad LT2 gate, each LF3/neither/LF1. Observe without LT2, add LT2, release LT2; digital remains independent. Decide broad gate acceptable / needs narrowing / ambiguous targeted follow-up. |
| 6 SOCD and retained smoke | 36 / 5 | SOCD histories for DownDiagonal and DownBack in both directions; second wins, first resumes when second released, then neutral, no stuck side. Twenty retained-modifier side/diagonal poses. Stop affected subarea on mismatch; preserve main-command results. |

### Controller-output reference for Groups 2–5

Bit-order label is RF5 RF6 RF7 RF8; table below uses physical names.
Independent ordinary face/trigger contributions remain, so isolate listed poses
before adding anything. “None” is no **command** A/B/Z, not a promise of zero
total output when LT2/ordinary controls are held.

| RF inputs | Geometry/effect | Command digital |
| --- | --- | --- |
| none | Default | none |
| RF5 | Default + forced Up | A |
| RF6 | Default + RF6LowMagnitude | Z |
| RF5+RF6 | RF6LowMagnitude wins | A+Z |
| RF7 | ForcedDown | none |
| RF7+RF5 | ForcedDown | A |
| RF7+RF6 | DownDiagonal | A only; no Z |
| RF7+RF6+RF5 | DownDiagonal | A only |
| RF8 | ForcedDown | none |
| RF8+RF5 | CDCNeutral | A |
| RF8+RF6 | DownDiagonal | Z |
| RF8+RF6+RF5 | DownDiagonal | A+Z |
| RF8+RF7 | DownDiagonal | none |
| RF8+RF7+RF5 | DownDiagonal | B only; no A/Z |
| RF8+RF7+RF6 | CDCNeutral | no A/B/Z |
| RF8+RF7+RF6+RF5 | DownBack | no A/B/Z |

Raw points are source expectations; effective points are **prior workbook
measurements**, never new gameplay measurements:

| Geometry | LF3 actual left | Neither | LF1 actual right |
| --- | --- | --- | --- |
| ForcedDown | [128,51] | [128,51] | [128,51] |
| DownDiagonal | [61,51] | [128,128] | [195,51] |
| CDCNeutral | [128,128] | [128,128] | [128,128] |
| DownBack | [195,51] | [128,128] | [61,51] |
| DefensiveDownBack | [179,98] | [128,128] | [77,98] |

Prior effective points: ForcedDown [0,-120]; diagonal sides [-83,-99]/[83,-99];
defensive sides [83,-34]/[-83,-34] in LF3/LF1 order. No facing inference.
DownBack and DefensiveDownBack reverse the actual horizontal column; describe
character-relative back/forward only with recorded actual facing.

With `LT2 && (RF7 || RF8)`, **DefensiveDownBack overrides every command table**,
including EWGF/Hell's-Gate-purpose combinations and all RF5/RF6 additions.
Command A/B/Z contributions remain unchanged; LT2 separately supplies L+R Shield.
Both full sequences are mandatory for LF1/LF3 (also neutral in this matrix):

```text
A: RF8+RF7 → add LT2 → release RF7 → LT2+RF8 → release RF8 → LT2
B: RF8+RF7 → add LT2 → release RF8 → LT2+RF7 → release RF7 → LT2
```

Defensive geometry persists while either RF remains; ordinary LT2 geometry returns
immediately after both release. For ordinary LT2 test usability and absence of
unexpected Z; analog/digital L/R composition is an expectation, not a raw game
measurement. Broad overlap set includes LT2+RF7+RF6, +RF8+RF6, +RF8+RF5,
+RF7+RF5, both singleton RF7/RF8 and every RF8+RF7+RF5/RF6 variant.

Retained smoke covers LT5 Horizontal35, LT4 Horizontal46, LT3
VerticalAsymmetric, LT3+RF3 Horizontal41, LT3+RF4 FlippedHorizontal41,
RF4 FlippedTilt, RT1 CompactTilt, RT1+RF4 AsymmetricTilt, RF4+RF2
FlippedTilt41 and ordinary RF6LowMagnitude. Isolate exact admitted combinations
from unrelated modifiers. The matrix names selected table separately from
analog effects and independent retained digital bindings.

Deferred, **not acceptance failures**: Kazuya-specific angled C-stick tilts;
action-button Shield suppression; additional undesigned left-thumb sublayers;
Nunchuk physical acceptance. Do not implement them here.

## Failure handling and classifications

For a failed command record physical inputs and order/timing, LF state, LT2,
expected table/effect/digital, actual game action, consistency, and optional video
timestamp. No UPDATE ID48, coordinate edit, firmware/source repair or ad hoc
experiment outside the matrix. Continue unrelated tests only if state remains
clear and safe. Systemic control/profile failure, freeze, unexpected menu entry,
loss of response or corruption: STOP testing and use safe return below if responsive.
Do not automatically retry a failed selection/reboot or a frozen route.

Classify controller/profile integrity separately (ordinary controls, leakage,
selection/persistence, corruption). Per command use PASS / FAIL / PARTIAL
(timing-sensitive but usable) / AMBIGUOUS; skipped tests remain NOT_TESTED.
Owner judgments are separate: no-horizontal neutral fallback; defensive coordinates;
broad LT2 gate; each release order; timing-sensitive command recognition.
Host PASS does not decide these judgments. No single undifferentiated gameplay PASS.

## Safe return, final preservation and STOP

1. Leave Training/match normally. Open `.Profile`, select **Ultimate ID27**,
   allow normal committed reboot, verify ordinary **GameCube** operation and
   correct menu. Record the selection/reboot; no automatic retry on uncertainty.
2. Return to Configurator through the established normal route. If the owner
   must pass via XInput/menu, use Ultimate only, and record every actual selection.
   Do not omit intermediate actions to force a Config comparison.
3. Re-enumerate/match fresh `PORT`; capture full final state:

```bash
PORT='<fresh matched final Configurator endpoint>'
export PORT
capture_all "$CAPTURE/final"
```

Before comparing, save `$CAPTURE/selection-events.json` as a JSON array of actual
observed **profile selections**, in chronological order. Each object has exactly:
`profile_id` (48 on GC at start, 27 on return), `backend` (3 GC, optionally2 for
the known Ultimate XInput entry route), `mode_index` (**fresh actual zero-based
Config row**), `owner_observation` (the direct report, not an invented telemetry
claim). Keep all events; bounds1–12 are a safety cap, not a retry allowance.
The execution agent derives context rows from saved Config and the unchanged
source-compatible selection path, and checks them before this offline replay.
If the actual row cannot be established, STOP before declaring preservation.
Normal backend navigation or an unmodeled Config change must be reconciled
against source and observations; this packet permits no write to make it match.

```bash
"$PY" "$CHECK" compare "$CAPTURE/preflight" "$CAPTURE/final" "$CAPTURE/selection-events.json" \
  > "$CAPTURE/final-preservation.log"
```

Require ID27/ID48 exact, all24 records/names/revisions/schemas/ranks/wrappers/bodies
unchanged; no SEL/dangling references; store healthy/recovery clear; incarnation,
store generation and token high-water unchanged. **Store mutation count=0**.
Config CRC is recomputed from actual bytes at each capture, never presumed to
increment. Offline replay permits only actual compatible native references,
backend/default destinations changed by approved normal selections. Every other
field must compare exactly, including checked-reference receipt fields.
Unexpected state: seal evidence and STOP, no restoration, flash or profile repair.

Finally exit Configurator normally to the established GC gameplay route with
Ultimate selected and verify normal operation. Record that actual final boot;
do not describe Configurator as an active gameplay state. If another profile
selection is needed after final capture, record it and repeat final read-only
preservation before closing; do not leave an unaccounted Config write.

If controls are frozen and safe menu return is impossible: stop inputs, disconnect
normally if needed, record last known profile/state, and stop for owner-directed
recovery. Never claim Ultimate active without observing the return. This packet
authorizes no recovery flash, destructive storage repair or automatic retry.

Seal private journals and per-group observations; summarize using
[RESULT_TEMPLATE.md](RESULT_TEMPLATE.md), retaining failures and deferred scope.
Stop after this campaign and safe Ultimate return. No second campaign, repair,
source merge, profile update or firmware change is included.

Preparation status:

```text
Kazuya ID48 selected: NO
Kazuya gameplay tests performed: NONE
ProfileStore mutations: NONE
Profile updates: NONE
Firmware flashed: NO
Canonical source changes: packet/evidence only
Kazuya gameplay acceptance: NOT_TESTED
```

## Approval sentence

I approve KGA-ID48-GC-R1 only: select stored Kazuya ID48, perform its bounded GameCube-adapter/Switch manual tests, return safely to Ultimate ID27 and verify final read-only preservation; no profile update, firmware change, source repair or further gameplay campaign.
