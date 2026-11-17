# Smallest final beta hardware session

## Superseding physical finding and repair — 2026-11-17

The later owner XInput smoke found Windows **Other devices / Pico**, no expected
XInput controller and no usable browser gamepad. Mac browser attempts also exposed
no usable gamepad. **XInput: SOURCE_FIX_REQUIRED / HARDWARE_RETEST_REQUIRED.**
Source audit confirms DInput shares late interface publication: **DInput:
SOURCE_FIX_REQUIRED**, regardless of selected profile applicability. Switch's
previous exact-image PASS is retained, with regression required after shared repair.
The new [repair and current state](../final-usb-gamepad/README.md),
[source audit](../final-usb-gamepad/SOURCE_AUDIT.md) and
[replacement owner packet](../final-usb-gamepad/HARDWARE_PACKET.md) control continuation.
Old de793f34 acceptance does not qualify the changed candidate. Configurator and
retro backends are excluded from final gamepad reconnect. No canonical merge,
freeze, tag or release. The prior scope/audit below records its earlier knowledge;
“none identified” was correct before this finding and is now superseded.

## Prior beta-readiness snapshot at 0a1eab8

Prepared 2026-11-17. No controller action has been performed by this documentation task.
Use this checklist with the owner; the assistant handles private read-only captures/comparisons
using the existing Configurator readers. The owner only operates the controller/receivers.
If a reader, expected output or restoration plan is unavailable, stop that dependent step before
changing saved state. No repository interpretation or new profile creation is required of the owner.
[Required rows](MATRIX.md) · [Install/recovery limits](QUALIFICATION.md).

## A. Pre-flight — observation and read-only capture

1. Keep the currently working image installed. Record this run's date and privately name the
   intended physical Mk6 unit. Record original Switch/setup, Ultimate version, actual GC adapter/
   port, Windows host and the chosen XInput and HID/DirectInput viewer. Use existing working cables.
2. Bind the exact image below using its preserved file and continuous owner installation custody.
   Read Configurator INFO/About; expected source/version is 5dfc4cc2. A short version alone does
   not prove the UF2. If source, unit or custody differs, stop and bind a separate candidate.

   - Tested source: `5dfc4cc26ca27d1de15c80e2a59f9637052f1b5c`.
   - Canonical production-equivalent source: `59870835e7cd8e7c52bd3742e4910a7083cd21f5`.
   - UF2 SHA-256: `de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518`.
   - UF2 size:1,325,568 bytes. Use the original preserved bytes, never the audit rebuild.
   - Repository-relative private custody file:
     `local_backups/hardware-artifacts/5dfc4cc26ca27d1de15c80e2a59f9637052f1b5c/de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518/firmware.uf2`.

3. Photograph the ordinary dashboard backend/profile and About before entering Configurator Mode.
   Assistant: capture Config raw bytes plus digest, backend/default rows and selected profile,
   ProfileStore incarnation/generation/token high-water, complete ordered inventory, every readable
   raw wrapper/revision/digest, and health/recovery/fencing state. Use existing GET_CONFIG,
   STATUS/LIST/READ and identity readers only; retain raw evidence privately. Incomplete capture,
   unexpected recovery/fence or unsupported storage state stops the session before selection.
4. Plan the existing eligible profile for each route. Assistant supplies a short expectation card:
   profile name/ID/revision, normal direction, modifier+direction, one distinguishing output versus
   another existing profile where available. Use its actual validated mapping; invent no game values.
   Profile27's inherited context hold remains: do not select it merely to make a test distinct.
   Profiles 53/54 have identical wrappers, so their names alone cannot distinguish output.
   If no safe existing profile/context can demonstrate the required GC distinction, stop that row
   for a bounded profile/context decision; do not install or edit one during this packet.

## Selection changes — before routes B–E

5. Prefer the already executing route/profile. Exit menus to the ordinary dashboard before inputs.
   Use the ordinary existing controller menu only when a route change is needed. Before each saved
   selection, assistant records the exact current and intended after values and owner approval for
   that named change. USB Mode can save both USB destination and that backend's default profile row;
   changing back can leave the other row changed. Plan restoration of every affected field first.
   If ordinary menu actions cannot restore exactly, stop before mutation and prepare a separate
   bounded restore proposal. No generic Config write, lifecycle operation or restore is authorized here.
   Boot normally with controls released; verify the executing backend/profile on the dashboard.
   Saved Config alone is not proof of active profile. Treat expected selection saves separately from
   unexplained changes; no full inventory reread is needed between every route absent an anomaly.

## B. Switch USB — reuse accepted rows; supplement only gaps

6. The exact retained image already has original Switch/Ultimate normal stick and gamepad-button
   PASS plus postinstall preservation PASS. Reuse that evidence while custody is continuous.
   Confirm the earlier grouped report included a mapped face and shoulder/trigger; if not, test only
   the missing named button(s). Explicit release/neutral is not recorded, so add this small supplement:
   connect normally through the supported Switch USB setup, confirm dashboard Switch/intended profile,
   enter Ultimate, press/release left direction and the representative mapped buttons. Observe motion/
   action while pressed and return to neutral/no stuck action after release. Note gameplay context
   where animation outlasts a press; use an input display if available. No latency trials or reflash.
   If exact custody cannot be reused, bind a new row and run detection, left stick, face, shoulder/
   trigger, release and Ultimate response on that exact image before marking PASS.

## C. GameCube — required final-image gameplay

7. Select/verify GameCube as planned. Connect Glyph → the named actual GC adapter → original
   Nintendo Switch. Launch Ultimate in a suitable practice session and return controller menus to
   dashboard. Record actual active profile output using the expectation card, not just a saved name.
8. Press/release left-stick up/down/left/right and a diagonal; observe expected directions.
   Compare one direction with the configured modifier+direction and show the expected changed output.
   Check a mapped face button and shoulder/trigger. Try one ordinary simultaneous case from this
   profile (e.g. direction+mapped action) and release all controls: verify neutral/no stuck input.
   Record the distinguishing expected/observed output. No right-stick or exhaustive mapping campaign.
9. Play normally for a short period (about 1–2 minutes is enough), then use an ordinary menu transition/
   return where relevant and confirm continued inputs/release. Record any freeze, lost input or wrong
   profile as a discrepancy; do not troubleshoot by changing firmware or profiles during this run.

## D. XInput — one minimal Windows smoke

10. Select XInput with the planned eligible existing profile and connect to Windows. Open an
    XInput-capable viewer (one that actually reads XInput, not merely a USB device list).
    Record detected controller, changing LX/LY on left directions, one representative button bit,
    and released axes/button returning to that profile's neutral. If practical, capture one
    profile-distinguishing output from the card. Mark an impractical distinction N/A with reason;
    it does not force a new profile or exhaustive mapping verification.

## E. DInput — one minimal HID/DirectInput smoke

11. Select DInput as planned on the same host if possible. Open a viewer exposing the HID/
    DirectInput **gamepad** values (the keyboard collection is separate). Record detected gamepad,
    changing left axes, one representative button and correct release/neutral. Capture a
    distinguishing profile value if practical; otherwise N/A with reason. No full mapping test.

## F. Restore, final readback and normal operation

12. Restore every approved temporary route/default/profile selection through the preplanned menu
    actions. The default endpoint is the exact original saved state. A different intended final
    state must have its exact values explicitly approved and recorded; never silently keep a delta.
13. Re-enter Configurator Mode. Assistant compares final Config bytes to preflight (byte-exact unless
    a named approved final change), complete ordered profile inventory, wrappers/revisions/digests,
    store incarnation/generation/token high-water and recovery/fences. Store data/counters should
    be unchanged by route selection; explain or stop on any difference. Mark preservation at API
    scope only, not raw flash equality or universal restoration.
14. Exit to normal operation, perform a normal reboot/reconnect, verify intended final backend/
    profile and a representative input/release. Capture a postreboot saved-state readback where
    reachable, or return once to read-only Configurator for it then normal boot again. Record final
    state/normal usability without claiming the full library was read on a route that cannot expose it.

Stop immediately on wrong image/unit, unexpected storage/recovery state, unexplained mutation,
wrong active output, missing input, freeze or stuck release. Keep evidence and stop dependent
mutation; no Fresh Install, erasure, automatic repair, new firmware, profile writes or performance
optimization. Switch 2/Nunchuk and other optional routes are outside this session.

## Result sheet (fill with observations, never assumed PASS)

| Row | Exact source/UF2 + setup | Expected → observed | Result / limitations |
| --- | --- | --- | --- |
| A identity/storage baseline | | | |
| B reused Switch evidence + missing release/buttons supplement | | | |
| C GC left/modifier/buttons/simultaneous/release/gameplay/menu | | | |
| D Windows XInput detected/LX/LY/button/release/optional distinction | | | |
| E HID/DInput detected/axes/button/release/optional distinction | | | |
| F exact restoration + final/postreboot preservation/usability | | | |

Attach private before/after capture references and approved selection log; return a sanitized summary
with PASS/FAIL/NOT_TESTED/N/A per row. Preserve earlier GOPT evidence and aggregate timeout separately.
