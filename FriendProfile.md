# Friend Ultimate profile

Private source-owned Glyph Ultimate profile. Install by flashing its single UF2;
the baked profile adopts once using `/friend_ult_20261012_v3.flag`.

## Tables (raw absolute coordinates)

- Default: `(61,51) (128,51) (195,51) (61,128) (128,128) (195,128) (61,195) (128,195) (195,195)`
- Tilt1: `(69,87) (128,87) (187,87) (69,128) (128,128) (187,128) (69,167) (128,167) (187,167)`
- Tilt2: `(187,88) (128,88) (69,88) (187,128) (128,128) (69,128) (187,168) (128,168) (69,168)`
- Tilt3: `(92,83) (128,83) (164,83) (92,128) (128,128) (164,128) (92,172) (128,172) (164,172)`
- Y1: `(61,100) (128,100) (195,100) (61,128) (128,128) (195,128) (61,156) (128,156) (195,156)`
- Y2: `(81,81) (128,81) (175,81) (81,128) (128,128) (175,128) (81,175) (128,175) (175,175)`
- X1: `(98,51) (128,51) (158,51) (98,128) (128,128) (158,128) (98,195) (128,195) (158,195)`

Priority: Up-smash, Mode, Tilt3, Tilt1, Tilt2, Y1, Y2, X1. RF6 maps to logical LT5; RF9/RF14/RF15 are blank. LF4 is L/light shield (108); LF4+LT3 is Y1 plus R (255). RGB is off.

The complete owner-normalized specification is `friend/profile_spec.json`.
Coordinates are source-owned, not runtime-loaded from Config. The owner's
2026-10-12 correction changes Default entry 2 from (-77,0) to (0,-77), raw
(128,51). This is the only coordinate delta from storage-recovery-v2. Tilt2 X
inversion remains intentional. All other coordinates are unchanged.

The v3 refresh intentionally reinstalls the complete baked friend Config once,
even on a device with the old valid v2 marker. The owner explicitly approved
replacing later saved settings after the friend's stored-Config refusal. No
Config push is needed. After verified v3 adoption, later user edits are preserved.

Physical C-stick: RT3 Left (39,128), RT5 Right (217,128), RT2 Down (128,1),
RT4 Up (128,255); diagonals combine these components; neutral (128,128).
RF8 maps to LF3 before the existing Left/Right SOCD pair. LF5 and RF6 both map
to LT5 before the existing Down/Up pair. SOCD_2IP retains second-input priority
with reactivation; initially simultaneous opposing directions cancel.

Ultimate remains Config index 3 and is default on XInput, DInput, Switch and
GameCube. Other profiles are retained. Ultimate references RGB Config 3, whose
empty STATIC mapping leaves all gameplay pixels black. Boot/recovery screens
and bootloader indicators are not gameplay RGB and remain source-default.

The boot-only installer validates the full baked Config, saves it, loads and
validates it, and compares every deterministic encoded byte (3,779 bytes in
this snapshot). Only then does it write/flush/close/reopen the exact marker
payload `friend_ultimate_20261012_applied_v3\n`. Mere existence, empty, old,
truncated or trailing marker contents never count as applied. A valid marker
skips provisioning; ordinary production stored-Config loading/validation still
runs, preserving later legitimate user edits. Failures use existing safe boot
refusal. This is a private one-shot full Config replacement, not a merge of an
old device Config. No flashing-time high-flash/filesystem wipe is added.
The private v3 refresh retains canonical no-autoformat mounting first.
If that mount fails (but setConfig succeeded), validated baked defaults authorize
an explicit format/remount of the linked LittleFS partition. Mounted storage is
never formatted. This private recovery also applies to a future unmountable
filesystem and can erase all persisted settings; first install and later
corruption cannot be distinguished when the only marker is inside that FS.
The original failed build used an overlong 37-byte marker basename; v2 uses a
27-byte basename accepted by the selected wrapper's <32-byte limit. Old v1/v2
markers do not suppress v3 adoption; a valid v3 marker preserves later edits.

Both the readback Config and bounded expected-encoding buffer are static;
readback resets before every attempt. The helper is called only by core0 setup
before the normal boot gate releases core1. No heap allocation is introduced
by the private helper. Host tests do not establish hardware acceptance.
