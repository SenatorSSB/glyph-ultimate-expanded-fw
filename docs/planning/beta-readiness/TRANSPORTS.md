# Transport correspondence for Glyph Mk6

## Exact candidate physical qualification accepted — 2026-11-17

Required first-beta physical scope **PASS** for source
`dcf6e29589f558a95c021bef491578f87e41750f`, tree
`a7731388430ea70dbe666298953795f4018069b0`, retained UF2 SHA-256
`2c77e2b7e50af2fd3b516d1ee7d0b8a67bcf992d6fcf0e3109a837422740cd42`
(1,325,568 bytes). Windows0738:4726/joy.cpl, original Switch USB/Ultimate,
GameCube-adapter/original Switch/Ultimate, final API-visible preservation of368-byte
Config/all27profiles and normal reconnect PASS. Host/source repair proof retains its
focused PASS and recorded framework failures; no full aggregate PASS is claimed.
DInput physical N/A for actual selected profile; future Senscope complete-path DInput
acceptance is required before public complete-profile/device release. JoyCheck/browser
Gamepad API remains NOT_QUALIFIED, discrepancy unresolved. Unique unit ID and exact
adapter model UNKNOWN; independent review accepts same-session owner continuity and
approved bounded route without broader claims. SOURCE_FIX_REQUIRED: none identified
for selected first-beta required scope. Keyboard deferred; Switch2 out of scope;
Nunchuk NOT_TESTED. Canonical integration pending owner authorization; beta freeze
prepared/not activated; no public release. [Accepted evidence and exact next step](../final-usb-gamepad/acceptance/README.md).
Earlier entries below retain chronological knowledge, not current pending-test status.

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

At the original audit intake, both the fork's merge base and the then-live Limit Labs configurator ref resolved to `9a78c7eeec87527b68644573e4c29fbdfb543239`. Limit Labs identifies that short version as release 1.0.7. The comparison below uses that committed Mk6 source against `59870835e7cd8e7c52bd3742e4910a7083cd21f5`. The official release bytes and the source lineage have different forms of provenance. [Official source](https://github.com/LimitLabs/FW-Glyph/tree/9a78c7eeec87527b68644573e4c29fbdfb543239) · [Official releases](https://limitlabs.com/pages/glyph-resources)

| Input path | GameCube | Nintendo Switch USB | XInput | DInput |
| --- | --- | --- | --- | --- |
| Classification | MATERIAL_CUSTOM_DIFFERENCE | MATERIAL_CUSTOM_DIFFERENCE | SHARED_CUSTOM_DIFFERENCE | SHARED_CUSTOM_DIFFERENCE |
| Constructor and setup | Default GC report and Joybus initialization. Vendored driver adds bounded idle admission and invalid-poll recovery. | Switch descriptor registration, HORI/POKKEN strings and 0f0d:0092 retained. Final executing Switch alone gets a 10 ms disconnect/reconnect. | Constructor, XUSB interface, 0738:4726 and original driver pin retained. | TUGamepad initialization, composite gamepad and keyboard descriptor registration retained. |
| Report structure | Inherited GameCube report layout, digital fields, sticks and analog triggers. Both-ABI normal poll fixtures cover bytes. | Inherited descriptor, packed eight-byte short-enum report, ID zero, hat and four axes. | Same XInput report type, axes, button bits, D-pad and triggers. | Same local composite HID gamepad report, hat, six 16-bit axes and numbered buttons. |
| Axis conversion | Copies four OutputState stick bytes. | Scales deviations from 128 by 1.25, inverts Y. | Four axes use (value − 128) × 65535 / 255 + 128 with integer arithmetic. | X passes through, Y inverts around 255; setters multiply the byte by 257. |
| Buttons, triggers, D-pad | A/B/X/Y, Z from buttonR, digital L/R, separate analog L/R and independent D-pad bits. | Buttons, ZL/ZR digital, hat from four directions. | Face/shoulder/system buttons and discrete D-pad. Digital trigger forces 255, otherwise analog value. | Numbered buttons, including digital triggers, and hat. Analog trigger passes value + 1 through a byte setter. |
| Scan and output | SLOW/MEDIUM, FAST during poll wait, then mode evaluation and valid poll response. New idle exits/service gate and invalid-poll reset affect liveness. | SLOW/MEDIUM, bounded HID readiness (1 ms), FAST/evaluate and readiness recheck before send. Upstream could wait indefinitely. | Same SLOW/MEDIUM, bounded ready wait (~50 ms), FAST/evaluate, send unless timed out. | Same SLOW/MEDIUM, wait until HID ready, FAST/evaluate and send. |
| Shared mode/profile resolution | Selected backend row binds the mode to the GC backend. | Saved USB destination resolves to its row and the executing Switch mode. | Saved USB destination can bind a compact/native Ultimate row to XInput. | Saved USB destination can bind a compact/native Ultimate row to the DInput gamepad. Keyboard is a distinct mode. |
| Routing, remaps and SOCD | All four call the same backend-aware UpdateOutputs on the bound game mode. The fork preserves raw, remapped and post-SOCD input in ResolvedInputContext. | Same shared path feeds Switch serialization. | Same shared path feeds XInput serialization. A configured modifier can change the stick value Windows receives. | Same shared path feeds the HID gamepad. A configured digital route can change a button or hat value the receiver sees. |
| Startup/backend selection | On ordinary detection the provisional USB backend may be replaced by detected Joybus. Pending selection is gated by receiver idle. | Validated USB saved index, boot chords/committed destination and finalized primary govern enumeration. | USB-connected detection returns an XInput sentinel. Ordinary setup resolves the saved USB backend, so a USB connection alone cannot establish XInput selection. | Same detection and destination logic. An ordinary USB boot can resolve to DInput. |
| GOPT and custom profile | GOPT's terminal boot gate precedes every report. Mode binding can activate a schema-5 native profile. | Same terminal gate and native evaluator, followed by Switch-specific readiness. | Same terminal gate and native evaluator. Identity-only diagnostics omit actual receiver values. | Same terminal gate and native evaluator. Shared changes apply before TUGamepad expands the bytes. |

In the compact Ultimate path, set_mode activates the configured record ID and binds its view. Ultimate::SetConfig checks published view ownership and Config context. Ultimate::UpdatePreprocessedOutputs can evaluate the native program against raw, remapped and post-SOCD inputs or emit neutral on native evaluation failure. These branches are reachable on both PC gamepad routes. This shared custom difference warrants one minimal receiver-input smoke on each, with a distinguishing value if practical; no exhaustive mapping campaign. The GOPT CRC buffering and dashboard ellipsis provide no independent reason to test either PC transport. A plain upstream-equivalent row alone would miss the changed path. [Mode selection](../../../src/core/mode_selection.cpp) · [Controller input pipeline](../../../src/core/ControllerMode.cpp) · [Ultimate evaluator dispatch](../../../src/modes/Ultimate.cpp) · [Shared scan/dispatch](../../../src/core/CommunicationBackend.cpp)

Direct comparisons of both PC backend sources and headers, TUCompositeHID and CommunicationBackend.cpp produced an empty diff. The four serializers retain their upstream axis and button formulas. GameCube uses the local Joybus fork of f2f59c0a, including the per-state-machine activity marker. Switch keeps the upstream report layout and changes when the endpoint is opened and serviced. [GC source](../../../HAL/pico/src/comms/GamecubeBackend.cpp) · [Joybus changes](../../../lib/glyph-joybus-pio/UPSTREAM.md) · [Switch source](../../../HAL/pico/src/comms/NintendoSwitchBackend.cpp) · [XInput source](../../../HAL/pico/src/comms/XInputBackend.cpp) · [DInput source](../../../HAL/pico/src/comms/DInputBackend.cpp) · [HID axis setters](../../../lib/TUCompositeHID/src/TUGamepad.cpp) · [Backend construction and selection](../../../HAL/pico/src/comms/backend_init.cpp)
