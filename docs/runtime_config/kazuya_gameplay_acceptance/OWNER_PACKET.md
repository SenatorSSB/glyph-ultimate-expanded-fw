# KGA-ID48-GC-R2 — stored Kazuya gameplay campaign

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
CAPTURE=$(mktemp -d '/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/kazuya_gameplay_R2.XXXXXXXX')
cp "$PKT/RESULT_TEMPLATE.md" "$CAPTURE/RESULTS.md"
cp "$PKT/TEST_MATRIX.json" "$CAPTURE/checks-unexecuted.json"
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

## Gameplay workflow — 33 required checks, up to 2 optional checks

R2 supersedes R1's 177-pose plan under the owner's explicit direction:

> I will not manually confirm every table's every value.

The existing host verification covers all 16 RF states, horizontal/neutral cases,
SOCD histories, LT2 overlays, exact retained differential behavior, raw coordinate
compilation, digital masks and resources. **Do not reproduce these host tests
manually.** The question here is whether the exact profile produces intended,
acceptable Kazuya gameplay. No coordinate/table-by-table certification is required.

[TEST_MATRIX.json](TEST_MATRIX.json) has 35 meaningful cases maximum, including
two optional inherited-modifier checks. A complete transition sequence is **one
case**, regardless of intermediate states or reasonable repeated attempts.
The agent presents at most **three complete checks** at a time and saves actual
owner observations before continuing. No truth-table batches, new side matrix or
unbounded follow-up campaign. For example:

```bash
"$PY" "$CHECK" show 2 --batch 1 > "$CAPTURE/group2-batch1.json"
```

For each case the owner reports only actual move/state, repeat consistency,
unwanted action, acceptable yes/no/undecided, and optional notes/video timestamp.
Input/chord and purpose are already attached. The agent attaches deterministic
table/output expectations automatically. Do **not** ask the owner to transcribe
raw/effective coordinates, table IDs or masks. Record input order/timing/facing
when recognition is ambiguous; no frame-perfect threshold or assumed mistiming.
Every check begins NOT_TESTED. Save results after each small batch/group; preserve
reported FAIL and skipped checks honestly. A discrepancy may motivate later
offline deterministic investigation, not profile/source edits or extra manual
poses beyond this packet. Any new targeted campaign requires separate direction.

| Group | Checks | Gameplay task |
| --- | ---: | --- |
| 1 ordinary smoke | 1 | One whole-group check: normal movement, A/B/X/Y, cardinal C-stick, ordinary Z and Shield, controller/menu responsiveness. Ask: **Does ordinary movement/basic control feel materially different from your known-good Ultimate profile where it should not?** Serious regression: safe Ultimate return and STOP before commands. |
| 2 core commands | 15 | RF7 and RF8 Down primitives once each; EWGF-purpose, Hell's-Gate-purpose, Spinning Demon and four-button DownBack on both LF sides; CDC neutral in one normal setup and no-horizontal; while-rising-purpose A once. Two single composition checks cover distinct ForcedDown+A and DownDiagonal+A+Z, with no side matrix. |
| 3 neutral fallback | 3 | No LF1/LF3 for DownDiagonal (RF8+RF7), DownBack (all four RF), DefensiveDownBack (LT2+RF8+RF7). What happens; useful/safe; retain neutral fallback or different design? These are owner design judgments. |
| 4 Shield/release | 4 | Both complete release orders on LF1 and LF3. Observe Shield retention, roll/spot-dodge, crouch/movement, defensive-diagonal usefulness, final LT2-only normality. Repeat full sequence for consistency; do not count steps as separate tests. |
| 5 LT2 overlap risk | 5 | EWGF-purpose and Hell's-Gate-purpose overlap on one side plus opposite-side confirmation (deeper repetitions only if direction-sensitive); one rising-A overlap. Decide broad gate acceptable as-is / should narrow / ambiguous follow-up. No permutation matrix. |
| 6 ordinary RF5/RF6 | 3 | RF5 Up+A; RF6 ordinary Z/low-magnitude; RF5+RF6 combined behavior. Normal gameplay setup only; no exhaustive side variants. |
| 7 SOCD sanity | 2 | On RF8+RF7 diagonal command: LF3→addLF1→releaseLF1; opposite history LF1→addLF3→releaseLF3. Second wins, release returns to first, nothing stuck. Whole history is one check. |
| Optional inherited modifiers | 0–2 | LT5 Horizontal35 and RT1 CompactTilt, one representative gameplay check each **only if actually relevant to the owner**. Otherwise mark deferred, not failed. No additional retained table list to certify. |

### Core command purposes and leakage

LF1 is actual right, LF3 actual left. No character-facing inference: record facing
where it matters. DownBack reverses actual horizontal columns, not detected facing.

| Meaningful command | Attached controller expectation | Gameplay observation |
| --- | --- | --- |
| RF7; RF8 separately | ForcedDown, no command A/B/Z | Actual Down consequence; no horizontal repeats unless leakage is surprising |
| RF7+RF6+horizontal | DownDiagonal, A only, no Z | EWGF / WGF non-electric / other action, repeated human consistency, unwanted action |
| RF8+RF6+horizontal | DownDiagonal, Z only | Actual Hell's-Gate-purpose recognition and interference |
| RF8+RF7+RF5+horizontal | DownDiagonal, B only | Spinning Demon recognition; no unwanted A/Z action |
| RF8+RF7+RF6 | CDCNeutral, no A/B/Z | Usable cancel/neutral state and no attack/grab; normal and no-horizontal setup |
| RF8+RF5 | Neutral+A | Actual while-rising-purpose result, normal setup once |
| all four RF+horizontal | DownBack, no A/B/Z | High-priority non-Shield down-back CDC usefulness, both actual sides, no leakage |
| RF7+RF5 | ForcedDown+A | One distinct composition check |
| RF8+RF6+RF5+horizontal | DownDiagonal+A+Z | One distinct composition check |

These digital contributions are from command buttons. Independent ordinary
face/trigger bindings remain; isolate the stated chord when judging leakage.
Timing-sensitive recognition may need reasonable repeated human attempts. A held
chord is not an automatically performed game command; record the actual manual
setup/order, game result and consistency separately.

### Shield transition and provisional overlap decision

For each actual LF side, perform the **entire** sequences:

```text
A: RF8+RF7 → add LT2 → release RF7 → LT2+RF8 → release RF8 → LT2
B: RF8+RF7 → add LT2 → release RF8 → LT2+RF7 → release RF7 → LT2
```

The current gate `LT2 && (RF7 || RF8)` selects DefensiveDownBack until both RF
buttons release; ordinary LT2 geometry then returns. Assess usefulness/safety in
gameplay. In the high-risk EWGF/Hell's-Gate overlaps the gate replaces geometry
while A/Z remains respectively; rising-A overlap retains A. Owner decides broad
gate **acceptable as-is / gate should be narrowed / ambiguous; targeted follow-up
needed**. Do not edit or narrow it here.

### Small Ultimate adjacency comparison and retained scope

Use the initial Kazuya smoke, then the normal safe return to known-good Ultimate
at the end for one bounded comparison: movement, A/B/X/Y, C-stick basics, ordinary
Shield, ordinary RF5 and RF6. This is the completion of SMOKE-01, not another set
of atomic poses. Record any material difference where behavior should be retained.
If none appears, rely on the existing 110,702-frame archival differential rather
than comparing every map/value. A clear mismatch is recorded for investigation;
no automatic expansion, firmware/profile change or raw-byte manual exercise.

RF6LowMagnitude is operationally covered by Group 6. At most two optional spots:
Horizontal35 (LT5) and CompactTilt (RT1), only if owner-intended for current use.
If not intended, mark them **DEFERRED / NOT PART OF INITIAL KAZUYA ACCEPTANCE**.
Horizontal46, VerticalAsymmetric, Horizontal41, FlippedHorizontal41, FlippedTilt,
AsymmetricTilt and FlippedTilt41 are deliberately **NOT_TESTED / DEFERRED** here.
No individual gameplay PASS for a deferred map. They do not block useful core
Kazuya command-system acceptance. Relevant symptoms can be investigated afterward
using deterministic evidence, without modifying ID48.

### Diagnostic reference only — no routine raw-value acceptance

| Geometry | Source raw points |
| --- | --- |
| ForcedDown | [128,51] |
| DownDiagonal | LF3 [61,51]; LF1 [195,51] |
| Neutral / no-horizontal fallback | [128,128] |
| DownBack | LF3 [195,51]; LF1 [61,51], reversed actual side |
| DefensiveDownBack | LF3 [179,98]; LF1 [77,98] |

Prior workbook effective points: ForcedDown [0,-120]; diagonal LF3/LF1
[-83,-99]/[83,-99]; defensive LF3/LF1 [83,-34]/[-83,-34]. These are historical
diagnostic references, **not newly measured gameplay values or manual poses**.

### Classification and failure handling

Separate core Kazuya command system **PASS / PARTIAL / FAIL / AMBIGUOUS** from
Shield-transition design, broad LT2 gate, no-horizontal fallback and optional
retained modifiers. Untested core checks remain NOT_TESTED; a useful partial
conclusion is allowed. Optional maps may remain deferred without blocking core
acceptance. Do not invent one undifferentiated all-profile gameplay PASS.

For a failed command save exact input/order/timing/LF/LT2, observed action,
consistency and optional timestamp; agent attaches deterministic expectations.
Continue unrelated checks only if state is clear and safe. A freeze, systemic
ordinary-control regression, unexpected menu entry, unresponsiveness or corruption
means stop testing and use safe return if responsive. No automatic retry of
uncertain selection/reboot, no UPDATE/CREATE, source repair or flash.

Deferred functionality remains: Kazuya-specific angled C-stick tilts,
action-button Shield suppression, undesigned thumb sublayers, Nunchuk physical
acceptance. These are not failures of this bounded campaign.

## Safe return, final preservation and STOP

1. Leave Training/match normally. Open `.Profile`, select **Ultimate ID27**,
   allow normal committed reboot, verify ordinary **GameCube** operation and
   correct menu. Record the selection/reboot; no automatic retry on uncertainty.
2. While Ultimate is active, complete the bounded SMOKE-01 adjacency comparison
   (movement, A/B/X/Y, C-stick, Shield, ordinary RF5/RF6), save any discrepancy,
   then return to Configurator through the established normal route. If the owner
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
Gameplay performed: NONE
ProfileStore mutations: NONE
Profile update: NONE
Firmware change: NONE
Canonical source changes: packet/evidence only
Gameplay acceptance: NOT_TESTED
```

## Approval sentence

I approve KGA-ID48-GC-R2 only: select stored Kazuya ID48, perform only its 33 required and up to 2 owner-relevant optional GameCube-adapter/Switch gameplay checks, return safely to Ultimate ID27 and verify final read-only preservation; no profile update, firmware change, source repair or further gameplay campaign.
