# Independent review — RT2 phase11 identity timing A/B

Review date: 2026-10-17. Reviewer: fresh independent agent
`/root/fresh_identity_timing_review`. **APPROVED for the bounded diagnostic
candidate and hardware handoff, conditional on final exact committed
build/resource/custody verification. Zero blocking source findings.** This is
not hardware PASS, canonical merge approval, root-cause confirmation or a final
production recovery-identity decision.

## Authority and reviewed snapshot

I read the direct owner phase11 request in the attached `Pasted text.txt`, the
repository AGENTS/current-state/workflow/runtime-boundary/framework/queue and
authorization context, the complete candidate diff, matrix harness and the
result, installed466 adjudication and new hardware packets. The newer direct
request authorizes this bounded diagnosis/A/B and fresh review; historical
campaign instructions do not supply its authority. No source-agent controller
action, canonical write, commit or implementation edit occurred in this review.
My only tracked addition is this review.

Reviewed HEAD/base candidate: `466f91ed867884640375627734d3473e9fb22c32`, tree
`6aab0abcfd8a8c6bddd21d96e31432cbbfd31ba7`, parent
`2e0a608622e8363ec7e2ef2aacc224e0810020ed`; declared canonical remains
`6b73a7c507f35c111745c6bdd341618b490cbdcd`. This review does not independently
claim live remote truth or publication. Exact new commit/tree/artifact identity
must be checked in the separate final receipt after commit/build.

The owner physical sequence on exact466 is established:
yellow → brief green → static yellow, no serial endpoint/controller USB-tree
device within10s. Frozen monotonic phase/color source agrees with
`RT2_PHYSICAL_LAST_PHASE = 11`. Inspection, Serial.begin, constructor, read-only
installation, publication, loop entry and first SendReport return are therefore
completed boundaries for that occurrence. Phase12 was not observed. The supported
boundary remains `RT2_APPLICATION_RECOVERY_RUNNING_USB_NOT_MOUNTED_CONFIGURED`
with `NO_CONTROLLER_USB_DEVICE_IN_HOST_USB_TREE`. Normal466 transport control
at `/dev/cu.usbmodem101`, generation166 is accepted as owner evidence; a fresh
normal read-only adjudication is still required before replacement firmware.

## Independent pinned source and ELF adjudication

I inspected installed Arduino-Pico package1.30603.0/3.6.3, Adafruit TinyUSB2.3.0,
TinyUSB0.16.0: Device/CDC initialization, descriptor callback, USBD/control,
RP2040 USB task port, RP2040 DCD, main initialization and target tusb config.
Installed framework files were not edited.

I independently rehashed the preserved frozen466 artifacts at
`local_backups/hardware-artifacts/466f91ed867884640375627734d3473e9fb22c32/bf7b46c943448fc1468254763a04a7707d3c8d8f752aad7e80a06e40cc4dd2a6/`
in the primary repository. ELF SHA256 is
`19f0f8e31ce7d161107a829800eb64f3925585501af22a6692deb0fb0828ca0e`;
UF2 is `bf7b46c943448fc1468254763a04a7707d3c8d8f752aad7e80a06e40cc4dd2a6`,
988160bytes. Compile DB SHA256 is
`620f98fcbdda32f3003ad1245b5c7b0026c2c1ed57509012ce11e5e68a80afe3`.
Target objdump of that ELF, parsed by exact symbol block, shows:

```text
10006f88 <Adafruit_USBD_Device::setID(unsigned short, unsigned short)>:
strh r1, [r0, #8]
strh r2, [r0, #10]
bx lr
```

The descriptor translation unit's preserved compile command explicitly supplies
USE_TINYUSB, target tusb_config_pico.h, strict candidate1, USB_VID0x2e8a and
USB_PID0x000a. The source audit's eight requested answers are:

| Question | Independently checked answer |
| --- | --- |
| Modified bytes | idVendor bytes8–9 and idProduct bytes10–11, little endian; two target halfword stores. |
| Live/in-place | Yes. Device callback returns the same `_desc_device` member; setID changes that member. |
| Mutex/critical section | None in setID, and no IRQ mask/API call. |
| IRQ concurrency | USB-triggered software IRQ can preempt foreground construction and run tud_task/callback under __usb_mutex. setID does not take that mutex. Foreground does not resume inside that IRQ's copy; no torn PID-byte claim is needed. |
| Detach/re-enumeration | None. setID does not touch pull-up, attach, address, configuration or endpoints. |
| Old/new descriptors | Possible across requests: USBD obtains the live descriptor on each GET_DESCRIPTOR; control copies it into EP0's buffer. Target EP0 is64bytes, complete descriptor18bytes, so each copied reply is stable but a later reply can carry the new PID. |
| After address/before configuration | No VID/PID-dependent state transition in this implementation. USBD address/configuration handling is independent. RP2040 DCD writes hardware address after SET_ADDRESS status completion. Matrix address is an explicit DCD model, not proof of physical address receipt. |
| Normal timing avoidance | Not guaranteed. Normal has substantial optional initialization/detection before Configurator; RT2 constructs early. This explains a plausible window difference but does not establish host policy or physical cause. |

Core TinyUSB initialization precedes setup. CDC is automatically registered
before tud_init/attach; repeated Serial.begin is idempotent. Late CDC is rejected
as the explanation. No detach/attach or gameplay initialization repair follows
from this evidence. Identity inconsistency is a credible A/B hypothesis; host
rejection, hardware IRQ/task progress, pull-up behavior at physical phase11 and
macOS device-node policy remain unproved. Straightforward pinned semantics do
not require Astra escalation.

## Independently executed proof

Both checker commands passed under ASan/UBSan:

```text
python3 tools/check_glyph_rt2_usb_startup.py --identity-matrix --output-dir /private/tmp/glyph-identity-independent-matrix
python3 tools/check_glyph_rt2_usb_startup.py --output-dir /private/tmp/glyph-identity-independent-startup
```

Matrix report SHA256:
`cdfdab5d1806a2fce5aed1bf147309b3286d9e2ab1c57d2f75f580bf53c215ae`.
It contains64cases:32 frozen466 +32 current, each A–H × bootstrap000a/pre-attach
1092 control × first device reply8/18bytes. Frozen mixed identity occurs in11:
C with full18 first reply and D–H with either first length. An initial8-byte
reply contains no identity; C/8 therefore cannot demonstrate observed mixing.
Current recovery has0 mixed cases. All64 configure/mount, open three CDC
endpoints, perform no detach and preserve identical75-byte configuration SHA256
`e7b2772ab1902cb463e3d4db2006fbada600fbb1c897ae2b23aa73a025fd5279`.
The model reproduces descriptor inconsistency, not physical enumeration failure.
It records every descriptor response, configuration bytes, actual USBD
addressed/configuration state and modeled DCD address/endpoint calls. No
invented rejecting-host policy is present.

Default report SHA256:
`00d5e0aec3786ea7d3064ab3efecbf4ed6e4c1b3cef6c5f01f09c24adce9b67e`.
Its24 report cases are22 positives plus two removed-auto-CDC negatives; the
separate production-retain-policy guard also passes. Default frozen baseline
remains2e0, while matrix frozen baseline is466. Normal five-argument constructor
asserts2e8a:1092 and no recovery PIO claim. Compiling strict candidate0 and
explicitly requesting retain still sets1092 and leaves diagnostics inactive.
PIO unavailable/no-SM/fallback/busy and scratch namespace controls pass.

I inspected the six completed focused candidate logs (CDC TX progress, CDC RX
progress, root reconciliation, strict protocol, Config persistence, selection
recovery); each records PASS. These are executor-run regressions, distinguished
from my independently rerun USB checks. The real-stack inspection/refusal cases
exercise deviceinfo, PULSE/STATUS/LIST/full READ/HEALTH, all new mutation types
and whole Config SET refusal, checking persistent bytes and generation unchanged.
No accepted RX/TX/framing/deadline/fault implementation was edited. `git diff
--check` passes.

## Candidate and sticky-boundary findings

The additional named constructor policy is honored only by strict candidates;
only recovery supplies it. Existing normal five-argument construction delegates
to ordinary Configurator identity. No per-instance member or persistence/schema
change was introduced. Retaining attached bootstrap2e8a:000a is diagnostic only.
It does not decide whether bootstrap identity is suitable for production recovery
or whether identity should be selected cleanly before attachment.

Only MB1's top-left pair signals coarse state; LF4 words are zero. RED is
pre-SendReport-return; YELLOW is phase11+ without sampled connected/configured;
BLUE is sampled SETUP/connected without configuration, **not assigned-address
proof**; GREEN is mounted; WHITE additionally requires a completely framed,
nanopb-decoded protocol1/2 supported ProfileStore inspection request. Unknown
command/first byte does not select white. A semantic READ failure or missing
response is not excluded by white; actual response evidence remains required.
GET_DEVICE_INFO alone does not turn it white.

There are no new startup sleeps. The prior changed-marker four-word frame and
200us wire/latch interval remain, with early frames now all red. A decoded valid
inspection can cause a later coarse-state update; this is after request receipt.
Instrumentation still perturbs timing and does not prove identical electrical
scheduling. A color is the last sampled state at Mark, not an independent IRQ
monitor. Missing/unavailable PIO is inconclusive. Detailed monotonic scratch3
phases/flags remain; selectors0..2 and SDK4..7 are untouched. Reset retention is
not promised. Phase13 retains first-byte meaning; diagnostics version2 identifies
the new LED contract without changing schema.

The packets correctly require installed466 read-only normal adjudication first,
healthy generation166/useful1/3/4/22/GET_CONFIG correspondence and no uncertainty
or fault. They then bind the exact new artifact, normal transport proof, one RT2
attempt/10s MB1 and USB-tree/serial observation, inspection/refusals if enumerable,
and one normal reboot/correspondence check after success. Failure preserves state
and stops; no second RT2, retry-to-PASS, GC, selection or cleanup. They remain
prepared/NOT_EXECUTED. Nunchuk remains NOT_TESTED.

## Final conditions

Preliminary executor build reports RAM187452 unchanged from466 and flash482164
(+344). Those numbers are not final committed-build proof. Before declaring
`MULTI_PROFILE_STORE_RT2_IDENTITY_TIMING_DIAGNOSTIC_READY`, independently bind the
committed candidate SHA/tree/parent/base, reviewed input correspondence, successful
canonical Mk6 build, final resources and immutable UF2 hash/custody/readback in the
separate outside-tracked-tree receipt. Any relevant drift invalidates affected
review/proof. No merge before exact candidate/artifact human hardware PASS, and
no automatic production-final identity decision even if the A/B succeeds.

Reviewed input SHA256s (excluding this self-authored review):

```text
0aa59b8aa55bb3ad39c3d1e81714e6f4a508b6f4bcab9e4c7be34badb619244a HAL/pico/include/comms/ConfiguratorBackend.hpp
c032b9f34199ee1eb6a09d8ffe153cfb28411e501538cbd70865f1012c0c9c5a HAL/pico/src/comms/ConfiguratorBackend.cpp
bc1bd32b3d90d0b34db89f613909431e962702fecbb38e77d51bfce902baf36e HAL/pico/src/core/RecoveryStartupDiagnostics.cpp
630bacc6a81c66bc22d20ead7134def29f176d1581eff1ff9111a2d2006b0ed6 config/glyph/common/src/config.cpp
84751a7d9c1f0513822f26a204c762dd8411f8c2719f95fdafe6d4f8b454dd4b include/core/RecoveryStartupDiagnostics.hpp
ab549c22d07c30e52273f0c347352a2092ca576f94d375b9f1bcd862f223f7ea tools/check_glyph_rt2_usb_startup.py
17d494760a91589f560d04e704f7467e89e99842a2796c98521de64b17f6b52a tools/fixtures/profile_store_selection_recovery_host/setup_routes.cpp
6a3bb667d02932985dfe7b58289b349529e7afbe43743cb3c5721ec3bd89e3da tools/fixtures/rt2_usb_startup/startup.cpp
0023861c5e61e9cbbcb6741882a09159456b65823d347502696b6b6ff5451542 tools/fixtures/rt2_usb_startup/identity_matrix.inc
906a27238098e152ef1b20b60afe3385d85dbcb88a824c161705c201c997386c docs/runtime_config/profile_store_rt2_identity_timing_result.md
b148f8c3c65f007c898ed32ebf4bdca66ad58bc82a4b57510199e78967f11711 docs/runtime_config/profile_store_rt2_identity_timing_device_adjudication.md
72b19ee0f3f23afca09feec73d2dadf361f60e771115100b505a37760f9e64aa docs/runtime_config/profile_store_rt2_identity_timing_hardware_packet.md
```
