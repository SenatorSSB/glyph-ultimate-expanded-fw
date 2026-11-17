# First-beta installation and recovery contract

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

Owner-selected scope, 2026-11-17. [Readiness matrix](MATRIX.md) · [Non-destructive owner session](OPERATOR.md).
This replaces the audit's broader proposed timing/qualification campaign; the original remains
in audit commit `7908cac88317bbf0d1dee62ab1f8198bba12b4f3`.

The primary supported beta path is a **currently functioning Glyph Mk6 with readable, valid
Config and ProfileStore**, a known supported starting version/pair, preinstall backup/inventory,
an exact verified program-only beta UF2, manual BOOTSEL/UF2 installation and postinstall
Config/ProfileStore preservation verification. Claim only tested pairs and API-visible scope.
The existing exact installation episode is evidence for one unit/version/library pair, not all
historical custom firmware. Retain its [physical result](../gusb/PHYSICAL_RESULT.json).

Before any later manual install, record unit/source, Config bytes, all ordered profile metadata,
wrappers/revisions, incarnation/generation/token high-water and recovery/fences. Keep private,
decodable backups offline. Stop on unreadable, unsettled, unsupported or unexpectedly fenced state.
Verify retained regular UF2 hash/size, RP2040 family and program range against the filesystem.
For the retained de793f34 image: 1,325,568 bytes, 2,589 blocks, end 0x100a1d00 exclusive,
last erase-sector end 0x100a2000; LittleFS starts 0x1017f000. This protects installation address
separation, not runtime preservation by itself. Rehash immediately before any approved copy.

For a separately approved install, use physical BOOTSEL and connect the intended unit to the PC;
verify it is the unique intended RPI-RP2 target, manually copy the one verified UF2, and let it
restart with controls released. Capture source/version, normal operation and complete postinstall
readback before selecting routes. No automated flashing, erasure, retry loop or second copy.
This task prepares instructions and performs no installation.

BOOTSEL is firmware-loading access only. It does not prove profile preservation, filesystem
recovery or state reconstruction. Backups establish comparison evidence; universal restoration
is unqualified. If loading/boot/readback fails, record the last completed step, screen/source,
image hash and available read-only status, retain the backups/fence and stop for a bounded decision.
Do not improvise repair, downgrade, raw restoration or destructive recovery.

Not required for first beta: Switch 2, arbitrary old custom firmware, arbitrary downgrade
compatibility, blank-device provisioning, automatic updater/flashing, automatic repair,
corrupt-store reconstruction, raw flash restoration or universal profile restoration.
Normal storage validation/recovery/fencing remains unchanged.

## Later sacrificial-device Fresh Install proposal

Disposition: **POST-BETA SUPPORT HARDENING**, not a first-beta blocker. The owner selected a
functioning valid-store update path; destructive recovery is outside that support contract.
It is plausible but **NOT VALIDATED** and must not be advertised as proven. If the owner later
adds this recovery promise to the release, require the one-shot test before that promise ships.
No destructive test is authorized or performed now.

Only after later explicit owner authorization for irreversible loss:

1. Name a sacrificial Mk6, exact beta/custom source and UF2, and record a private pre-wipe
   inventory/settings with recognizable nonfactory state. Expect **all previous profiles/settings
   to be wiped**. Keep evidence; restoration is not the goal.
2. Independently verify the official Limit Labs Fresh Install artifact/version/hash and expected
   matching factory/default inventory before selecting it. The archived v1.0.7 / 9a78c7e Fresh
   Install is 1,818,112 bytes, SHA-256 `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200`.
   Official Update is a different file/operation. Revalidate the chosen official bytes at test time.
3. Manually load that exact Fresh Install via BOOTSEL once. Observe normal boot, official source/
   version, expected factory/default state and absence of prior custom profiles/settings through
   an official-compatible UI/readback.
4. Check actual stick/button/release on a supported receiver, then normal power-cycle/usability.
   Record each outcome. Stop on mismatch.

Goal only: **beta/custom state → official Fresh Install → boots normally → expected factory/default
state → usable controller**. This is intentional erasure, not preservation, downgrade compatibility
or restoration qualification. [Archived UF2 analysis](../../project/G12H_UF2_FORMAT_AND_FLASH_RANGE_ANALYSIS.md)
provides historical artifact/range evidence, not a physical custom→factory PASS.
