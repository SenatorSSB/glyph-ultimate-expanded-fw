# Frozen native OLED observability inventory

Source `ea137fc1f61d6acc0f1475c4165263eb661775da`, tree `9000056d2584f65a7ae8b40032c480d5a2250d28`. Read-only inventory; no physical result or action authority. Requested/observed model UNKNOWN, not attested. Findings must be checked against the writer's final exact candidate.

Owner reply, relayed directly by root on2026-10-20: “Usually the controller miniscreen, sometimes on Gamecube I use the system and game to see the results are actually what I want.” This establishes a preferred observation practice, not execution/result for this candidate. System/game/view, visible fields and adapter translation remain unknown.

**The OLED has two different observation modes.** `InputDisplay` draws original physical-input circles; `MenuButtonHints` (the source's “Dashboard Menu”) prints all six native analog values and one priority-selected output icon. The latter is meaningfully more than a physical-input viewer, but it still cannot show complete simultaneous digital outputs or transmitted backend reports. H1–H12 full requirements cannot be closed from the stated observers alone.

## Exact visible native numeric values

`config/glyph/common/src/display/MenuButtonHints.cpp:252-257` obtains a reference to `_backends[0]->GetOutputs()`; `src/core/CommunicationBackend.cpp:24-25` returns the live primary OutputState. `MenuButtonHints.cpp:354-373` prints:

| OutputState field | Pixel cursor | Displayed integer | Recover raw byte |
|---|---|---|---|
|leftStickX|(78,10)|raw−128|displayed+128|
|leftStickY|(78,18)|raw−128|displayed+128|
|rightStickX|(84,26)|raw−128|displayed+128|
|rightStickY|(84,34)|raw−128|displayed+128|
|triggerRAnalog|(112,26)|raw|displayed|
|triggerLAnalog|(112,34)|raw|displayed|

There is no additional quantization in these formulas: stick range0..255 is shown as−128..127 and triggers as0..255. Picopixel has2–3pixel-wide,5pixel-high digit glyphs (`config/glyph/common/include/display/Picopixel.h:37-49,120-121`); physical readability is unverified. These are native bytes before backend scaling/inversion, not measured stick angles or game semantics. No numeric button mask or individual digital trigger counters are printed.

## Digital visibility and physical widgets

`currentInputIcon` at `MenuButtonHints.cpp:92-204` returns one icon at the first applicable field in this priority:

`A,B,X,Y,buttonL,buttonR,triggerLDigital,triggerRDigital,start,select,home,capture,DpadDown,DpadUp,DpadLeft,DpadRight,LSClick,RSClick,modX,modY,LSLeft,LSRight,LSUp,LSDown,RSLeft,RSRight,RSUp,RSDown`.

Thus A hides both digitalL/R and all directions; L hidesR; one diagonal component hides another. Absence of a lower-priority icon proves neither that field false nor the complete mask. Native both-digital-trigger+A mask`000000c1` rendersA while showing rawanalog triggers140/140 in the complete fixture. The analog numbers do not directly observe either digital bit. They cannot substitute for H6's actual backend-bit requirement.

Icon labels depend on `iconBackend`, selected as the last non-USB entry in the mode's applicable_backends, falling back to the primary backend (`MenuButtonHints.cpp:286-312`). Default Ultimate listsGameCube last (`glyph_overrides.hpp:120-125`), so evenUSB can receiveGameCube-style Z/L/R icons. Printed backend text uses the captured primary ID at282-284. When iconBackend isGameCube, buttonR→Z, digitalL/R→L/R; Switch usesR andZL/ZR; XInput usesRB andLT/RT. Physical/currentConfig applicable_backends must be known before interpreting labels. buttonL may showLB even onGameCube although the GameCube serializer has no buttonL assignment. select/home/capture can be active with no icon in nonUSBGameCube context.

Bottom MB2–MB7 highlights are original physical bits and static `mode_config.menu_button_icon[]` labels (`MenuButtonHints.cpp:321-351,405-416`), not native digital binding outputs. `CurrentlyPressedButtonText` exists but its calling/display and5ms text-debounce block are commented out at375-392; it supplies no additional observation.

`HAL/pico/src/display/InputDisplay.cpp:30-62` instead reads `instance->GetInputs()`, prints mode/backend labels and draws filled/unfilled circles for the layout. It displays noOutputState bytes or digital outputs. `config.cpp:477-496` selects its physical layout. PC `B0XXInputViewer` is another distinct path: fixed physical input bits plus constants,25ASCII bytes (`src/comms/B0XXInputViewer.cpp:21-60`). It neither reports native outputs nor covers allMk6 inputs. Do not conflate either with MenuButtonHints' native numeric display.

The exact OLED mode is selected by `config.default_dashboard_option` (`config.cpp:418-424`); onlyDASHBOARD_INPUT_VIEWER selects circles, other values selectMenuButtonHints. “Dashboard Menu” and “Input Viewer” names exist at `GlyphConfigMenu.cpp:68-77`, but the top-level Dashboard Option wiring is commented out at88-95. This inventory does not assert a presently reachable manual menu path to change it. About shows firmware/name/device compile-time strings (`AboutMenu.cpp:24-43`), not full active native identity. OpeningConfigMenu unsets the primary game mode (`HAL/pico/src/display/ConfigMenu.cpp:117-122`); MB1 remains a menu/boot shortcut, so originalMB1 stimuli can disrupt observation/evaluation.

## Capture timing and backend differences

Core0 performs backend SendReport and native output generation; core1 independently rendersOLED (`config.cpp:320-338,342-395,437-505`). `IntegratedDisplay.cpp:36-48` clears, renders to the framebuffer, flushes to display, then handles controls. The dashboard references live outputs and reads six fields separately. No frame number, timestamp, generation or full-output latch ties that image to one evaluator iteration or transmitted report. Settled repeated values can support bounded observations; transient order/cadence and atomic tuples remain unmeasured.

| Backend | Source ordering | What the OLED cannot establish |
|---|---|---|
|XInput|FASTscan→UpdateOutputs→report assignments→timeout return or send (`XInputBackend.cpp:44-74`)|It can display updated outputs after a timeout that skippedsend. Report axes use `(raw−128)*65535/255+128`; digital triggers force report255 even when OLEDanalog shows another number.|
|Switch|waitready→FASTscan→UpdateOutputs→serialize/send (`NintendoSwitchBackend.cpp:114-152`)|Native numbers precede1.25scale/Yinversion/bytefields andDpad-hat conversion; no finalreport or delivery shown. Values may remain old while waitingready.|
|GameCube|waitpoll/scans→idleOtherCore→UpdateOutputs/assignments→conditional send→resumeOtherCore (`GamecubeBackend.cpp:26-71`)|Core1 is paused across the explicit critical section. Later OLED still does not prove a validpoll/send or latch one screen frame to one report. Analog bytes are source-assigned directly; digitalL/R aretriggerLDigital/RDigital andZ isbuttonR. Adapter→Switch translation remains unknown.|

GC core-idling prevents concurrent display execution during that section, but it does not latch an entireOLED render across later output iterations. XInput/Switch have no equivalent idling in these SendReport functions. No measured screen refresh interval or transport timing is claimed.

## Concrete indistinguishability in the existing catalog

Read-only projection of the495 immutable expected rows through the six numeric formulas and one-icon priority finds **269 rows with multiple active digital bits and14 groups with identical visibleOLED signatures but different fullOutputState masks**. The catalog has no active select/home/capture cases, so their conditional icon suppression does not affect these counts. This is a static source projection, not new evaluator execution or observed hardware.

For example, compatibility physical`[23]` versus`[23,5]` (RF7 vsRF7+LF5) has masks`00000002` vs`00200002` but identical six analog numbers andBicon; digitalDown is hidden. Other aliases hide an Up/Down component underLSLeft/Right or another output. JSON retains all14groups with original row identities, values and masks. Even flawless reading of this dashboard cannot distinguish those output errors.

## H1–H12 capability map

Every status below is an observation-capability assessment. All physical results remainNOT_TESTED. “Supported” means only the named sub-observation, never complete rowPASS. Requirements are `hardware_acceptance_protocol.md:53-70` and its complete-output/backend-observation rule at14-17.

| Row | Supported with numeric dashboard | Missing for full required row |
|---|---|---|
|H1|Six native analog numbers and one unmasked icon can support bounded held-state checks; physical viewer can identify pressed physical controls.|Full digital mask, actual transmitted backend report and reconnect success require separate actual observations. Owner statement is general use, not candidate result.|
|H2|Output-distinguishing analog values and highest-priority icon can be observed.|Hidden digital side effects/absences and transmitted reports remain unobserved; identical projected outputs cannot distinguish alternative internal outcomes.|
|H3|All4 native stick bytes are recoverable exactly from signed numbers, so static representative table entries can be recorded.|No selected-table/priority/default label; only distinguishable resulting coordinates. FullOutputState and backend report still unavailable.|
|H4|Numbers show analog direction cancellation and reappearance; A icon remains visible when A is set.|Cannot read hidden logical direction/digital bits. Core1 display is not a timestamped every-frame recorder, so capture ordered settled states and mark transitions unobserved where appropriate.|
|H5|Exact native analog coordinates and A highest-priority icon support bounded forced-table/A checks.|No direct winner/priority identity and hidden digital direction bits; actual backend outputs unavailable.|
|H6|Both raw analog trigger numbers and4 stick numbers are displayed; A is visible.|A hides L/R; L hides R even without A. Analog140 does not directly prove digital trigger bits. Actual GameCube l/r/Z, Switch zl/zr, XInput lt/rt report fields are absent. Required full row cannot be established.|
|H7|Six analog values reveal LT6/RS/null outcomes; a lone unmasked Dpad or stick-direction icon may be visible.|Simultaneous directions/Dpad flags and other digital interactions are hidden; Nunchuk remains NOT_TESTED. Many catalog aliases occur here.|
|H8|Use known physical presses and output-distinguishing analog values; isolated icons supply limited digital evidence.|Cannot prove all prior digital intrinsic effects absent or full mask/report correctness. Physical circles alone prove neither native mapping nor outputs.|
|H9|Sample-specific analog differences can be recorded after approved reboot. Complete sample table19 values(78,84)/(79,85) appear as(-50,-44)/(-49,-43).|OLED mode name is Config row name, not active profileID/revision/hash/engine/context; persistence/store readbacks and active identity require separate supported evidence.|
|H10|No native identity fields are displayed by these OLED paths.|Unsupported by OLED or unspecified system/game; requires actual supported XInput identity capture. About labels are compile-time strings, not this attestation.|
|H11|A generic recovery/refusal page or loss of ordinary output could be a bounded symptom if actually observed.|No native rejection reason/status or proof of no legacy fallback. Need preflighted negative case and independently supported identity/status/readback; no ad hoc write authorized.|
|H12|Bounded analog/isolated-button ordinary behavior after reboot can be recorded.|No Config bytes/checksum/store payloads/references or monotonic metadata shown. Full restoration and full output/backend requirements need separate readbacks/observers.|

The owner's unspecifiedGameCube system/game observation does not fill these gaps yet. It can supply accurately described downstream qualitative results once actually reported, but no identified view currently supplies full mask, native byte values, digitalL/R/Z separation, trigger precision or raw backend report. Nogame semantics, directGameCube→Switch equivalence orXInput→GameCube acceptance is inferred.

## All18 source families

Names come directly from the frozen compatibility conversion correspondence. Each family can have useful visible numeric/icon subchecks; **fullOutputState/backend completeness is unsupported for everyfamily with the stated observers**.

|Family|Source family|Visible sub-observation|Hidden requirement|
|---|---|---|---|
|1|LS direction references|Native LS numeric pair; lone logical LS direction icon|Logical direction bits remain independently hidden under higher-priority icons or other directions.|
|2|RS direction references|Native RS numeric pair; lone RS/C-stick direction icon|Simultaneous RS direction bits and combined outputs remain hidden.|
|3|default and Mode nine-way tables|Exact native LS/RS numeric values for representative nine-way entries|Mode/default/table identity is not displayed; digital completeness/backend report absent.|
|4|X1 X2 Y1 Y2 modifiers|Output-distinguishing native analog changes for X1/X2/Y1/Y2|Cannot prove hidden digital interactions or identity from modifier names.|
|5|Tilt1 Tilt2 Tilt3 and minus41|Output-distinguishing Tilt native analog changes|Cannot prove full digital effects/absences or active table identity.|
|6|Mode and normal/flipper/LF4 sublayers|Output-distinguishing Mode/sublayer analog values and first icon|Sublayer/role/winner state and complete digital mask are not displayed.|
|7|deterministic table selection|Coordinates distinguish winners only where outputs differ|Winner table/priority is absent; equal coordinates are observationally indistinguishable.|
|8|A B X Y Z digital terms|One priority A/B/X/Y/Z-style output icon|Other simultaneous digital terms/absence hidden. Z icon is icon-backend-dependent buttonR label.|
|9|L/R digital carriers and trigger effects|Raw analog triggerL/R numbers; one unmasked digital trigger icon|Cannot independently read both digital trigger bits, shoulders vs triggers or actual backend fields.|
|10|independent multiple-output and OR composition|Highest-priority output and analogs|Multiple-output/OR digital completeness cannot be established; A masks L/R.|
|11|clean genuine Down+A|Down numeric value/cancellation plus A icon|A can be seen with analogneutral but logical digital direction mask/history frame details hidden.|
|12|clean forced-table+A|Forced coordinate numbers plus A/filter icon|Table identity and hidden direction/digital flags are not visible.|
|13|historical LT6 post-table override|LT6 resulting analog value plus A icon|Digital Down/simultaneous terms hidden by A; no proof all output bits match.|
|14|RF5 RF6 RF7 compounds|RF5/6/7 resulting analog values and first icon|RF7 B and RF5 A can mask differing direction bits; concrete catalog aliases exist.|
|15|RS diagonal and RF3 vertical transforms|Four native stick numeric values for RS/vertical transforms|Relevant activation/digital direction bits hidden; no report/frame correlation.|
|16|Dpad route/bypass/digital flags and Nunchuk tail|Dpad-induced analog center and one unmasked Dpad icon|Dpad diagonals, bypass/flag state, LS-to-Dpad digital completeness and Nunchuk tail not fully observable. Nunchuk NOT_TESTED.|
|17|both-stick null|Four stick numbers at null coordinates|Null coordinates alone do not establish hidden direction bits/other state; catalog aliases exist.|
|18|all28 literal raw/asymmetric/noncenter tables|Exact native analog numbers for selected raw/asymmetric/noncenter entries|Cannot observe unexercised tables, winner identity, all digital fields or actual backend reports.|

## Remaining concrete facts

Confirm the actual dashboard and its readable fields; identify the specific system/game/view and explicitly visible outputs before assigning them evidence scope. H6 still needs an actual observer for simultaneous digitalL/R/A and relevant backend bits; the OLED source cannot provide it. Runtime identity, backup/reference/payload/checksum readbacks and safe restoration remain separate evidence. No new firmware observer, transport, device action, test-scope reduction or acceptance is authorized by this inventory. NunchukNOT_TESTED. Reconcile the source pins with the final exact candidate before using this report.

## Source SHA-256 pins

- `config/glyph/common/src/display/MenuButtonHints.cpp`: `99bfce1128b8ab25922088a334f8354b1bf8aad0522909122ab5a2962f6c2bcc`
- `HAL/pico/src/display/InputDisplay.cpp`: `761f3a5bb6357a278042356e25c691ef82bb45030ee6588cd6571a08e2e6480b`
- `src/comms/IntegratedDisplay.cpp`: `37213732b17e8d911ecdb22908a005cc792540f4f4cd67b3c986ecfcdeed006e`
- `include/comms/IntegratedDisplay.hpp`: `8b66db83f79a251ac1d6fe80ad88f131c973c3c7b5191579ec787dc2423fdcae`
- `config/glyph/common/src/config.cpp`: `5b407ecb9283ea311cd1c033abcc6a5baff2a8a42ad3ffacbbf4974e683177bc`
- `src/core/CommunicationBackend.cpp`: `9be53fab3470f83a4e9c080a0afe295fadc88afcb2ffc4598657aeb211241575`
- `include/core/state.hpp`: `c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3`
- `src/comms/B0XXInputViewer.cpp`: `4ea39c7bf81929697f881753cb957796dc10e7ffa33f93b68e0ad84a74f23c2e`
- `HAL/pico/src/comms/XInputBackend.cpp`: `b2c18262eeced1db6ee752c8493b3379ab9a8d89ee2c84f219a0853a84fbf862`
- `HAL/pico/src/comms/NintendoSwitchBackend.cpp`: `c55860e0d9ecab5eb033b7fa058bc132a51e51eb7c66df4dcdb998649cc49c25`
- `HAL/pico/src/comms/GamecubeBackend.cpp`: `48f2bfd711c2f44f6b32f030002c018c4ef716e71d917cb28d9f5d881a249329`
- `HAL/pico/src/comms/backend_init.cpp`: `057e4eb529fd9d9fbe94872ee73f0a64799ce77cdfc7f32c367775c9293c27d0`
- `config/glyph/common/include/glyph_overrides.hpp`: `7a1bc4b09745767d7a34d4b2495edfe22af5d3b4b960eb822c361ac16590803c`
- `config/glyph/common/src/display/GlyphConfigMenu.cpp`: `4ef795f0d34a745cf2d96f52be2493808452e2998a371ee5a96747a08207fcf0`
- `HAL/pico/src/display/ConfigMenu.cpp`: `5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be`
- `HAL/pico/src/display/DefaultConfigMenu.cpp`: `4b8f7cdf492a34c70fbd02110b27e5814b4efd910082a05f5b3f205ed334b520`
- `config/glyph/common/src/display/AboutMenu.cpp`: `d53f71f87cb407c477b588f28cbd4ebadb522326f560e1209b8a3bacb832beee`
- `config/glyph/common/include/display/Picopixel.h`: `035c01e6d48efdfef1e4de6152d0d03910210e449236506ec7c8f71799073363`
- `docs/runtime_config/profile_native_ultimate/hardware_acceptance_protocol.md`: `51b3958910c25396851c9cdf4ece95743b20c875e788f3170923834f94574a2d`
- `docs/runtime_config/profile_native_ultimate/candidate_hardware_packet_current.md`: `767889980f181f07cf1e6b9a6240c27cdd5edcfe3e68e9ed14b161990826824f`
- `docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/compatibility/conversion.json`: `6de8b33f40ee23c82189af45320c11db22fb07f754169477988043d5c39fd78d`
- `docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/expected_observations.json`: `e2cf3540b28519c06dc66a9f11a17a19fb08536cecfc4808e1dd2d3d533481bd`

Only `/private/tmp/glyph-native-miniscreen-observability.md` and `.json` were written in this follow-up. No screenshots, device, network, source/profile edits, build or evaluator/generator run.
