# First Glyph beta readiness — 2026-11-17

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

Current owner-selected scope; supersedes broader recommendations in historical packets.
Canonical source: `59870835e7cd8e7c52bd3742e4910a7083cd21f5`.
No beta freeze, public distribution, tag or release is authorized by this document.
[Ordered owner packet](OPERATOR.md) · [Install/recovery contract](QUALIFICATION.md) · [Source delta](TRANSPORTS.md)

| Area | Current state | Required before beta? | Evidence still needed |
| --- | --- | --- | --- |
| Switch USB / original Switch / Ultimate | MATERIAL_CUSTOM_DIFFERENCE; exact 5dfc4cc2/de793f34 image has owner-reported sticks/buttons PASS and API preservation PASS | Yes, within this setup | Reuse detected/working-input evidence if exact custody retained; supplement explicit release/neutral and a named face + shoulder/trigger if their coverage cannot be confirmed from prior grouped report. No full repeat needed. |
| GameCube / adapter / original Switch / Ultimate | MATERIAL_CUSTOM_DIFFERENCE; repaired image has connection trial only; earlier GOPT gameplay belongs to its earlier exact image/scope | Yes | Final retained image: left cardinal/diagonal, modifier, face, shoulder/trigger, simultaneous input, release, short normal gameplay/menu return; distinguish intended active profile by actual output. |
| XInput | SHARED_CUSTOM_DIFFERENCE; upstream serializer/transport retained, changed native/shared input pipeline reachable; prior identity alone insufficient | Minimal Windows smoke | Detected via XInput, changing LX/LY, one button, neutral/release; distinguishing profile value if practical. |
| DInput | SHARED_CUSTOM_DIFFERENCE; upstream serializer/transport retained, changed native/shared pipeline reachable | Minimal HID/DirectInput smoke | Detected gamepad collection, changing axes, one button, neutral/release; distinguishing value if practical. |
| Config/ProfileStore preservation | Exact USB installation episode passed Config/all27 wrappers/revisions/ordered inventory/counters, no unexpected fences | Yes, API-visible supported-pair preservation | Current preflight + final readback around route session, accounting for approved selector changes. Existing exact installation evidence reusable; no new install just for testing. |
| Managed profile lifecycle | Historical bounded CREATE/selection/lifecycle and host evidence retained; selected package output distinction not fully demonstrated; profile 27 context hold retained | Existing protections remain required; no new exhaustive lifecycle campaign | Use an existing validated eligible profile/context with distinguishable GC output. Do not create/update/delete packages for this run or treat saved Config as execution proof. Builder/Senscope completeness is separate authority. |
| Boot/startup | Accepted for beta; owner observes about 4.5s USB cable connection→Switch recognition on current setup, including console registration | No optimization or timing campaign | None for beta. Host setup ~4.3 ms and projected duplicate-work ~136 us are host-model results only; second validation catches late faults and remains intact. |
| Update/install path | Functioning Mk6 + valid readable Config/ProfileStore → exact program-only UF2, manual BOOTSEL, backup/readback; one exact pair already accepted | Yes, narrow contract | Bind every advertised starting version/pair to preservation evidence; document limits. No universal historical compatibility claim. |
| Destructive official Fresh Install | Plausible, unvalidated custom→factory route | POST-BETA SUPPORT HARDENING | Separately authorized sacrificial-device one-shot only; outside selected valid-store path and unadvertised as validated. If later advertised as supported, its test becomes RELEASE_REQUIRED for that claim. |
| Switch 2 | Excluded | No | None; no beta blocker. |
| Nunchuk | Excluded / NOT_TESTED | No | None; no beta blocker. |
| Other optional routes (Keyboard, other consoles/accessories) | Unqualified/deferred for first-beta support | No | No new campaign; retain historical limitations without transferring acceptance. |

Source appears sufficient to enter this bounded qualification without another firmware change.
No concrete selected-scope defect was found; hardware PASS is still pending and can reveal one.
No freeze is declared now.

| Remaining class | Disposition |
| --- | --- |
| SOURCE_FIX_REQUIRED | None identified in this bounded audit. A new concrete defect stops the affected row for source evidence and authority adjudication. |
| HOST_VALIDATION_REQUIRED | No new product host gate identified; audit's focused PASS results remain historical. Fresh docs/control/correspondence results are recorded in VALIDATION.json. Full aggregate remains FAIL/CHECKER_TIMEOUT framework debt, never PASS. |
| OWNER_HARDWARE_TEST_REQUIRED | GC final-image gameplay; minimal Windows XInput/DInput; explicit missing Switch release/input detail; current preflight/final preservation. |
| DESTRUCTIVE_RECOVERY_TEST_REQUIRED | None for narrow first beta. Conditional only if destructive recovery is advertised as validated. |
| DOCUMENTATION_ONLY | Record scoped human results and exact unit/source/UF2; bind public install instructions to tested starting pair(s), supported state and exclusions. |
| RELEASE_DECISION_ONLY | Owner chooses future freeze identity, distribution artifact and release after required evidence; no publish/tag/release now. A different rebuild requires its own exact artifact qualification. |
| DEFERRED_POST_BETA | Boot optimization, sacrificial Fresh Install qualification, Switch 2/Nunchuk/other optional-route support, broader restore/downgrade/provisioning support. |

Before a future beta freeze: close required physical rows, final state comparison and result review;
resolve any actual discrepancy; record exact source/artifact and narrow support wording; obtain the
owner's freeze/release decision. No firmware work is scheduled merely to advance the milestone.
