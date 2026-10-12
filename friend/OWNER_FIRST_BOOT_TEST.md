# Owner/friend first-boot protocol

Status until a human reports the exact artifact test:
NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST.
For this full-Config refresh v3, first pass CONFIG_REFRESH_V3.md on the owner's
Glyph; only then run this wider matrix against the NEW artifact in its manifest.
The first v3 adoption replaces the complete saved Config, as owner-authorized.

Record the private commit and complete firmware SHA-256 from BUILD_MANIFEST.md,
controller revision, cable/adapter/console, backend and date. Test this exact
firmware only. No assistant-controlled flash has been performed.

1. Install by the four README steps. Confirm one reboot, no recovery/refusal
   message, and Ultimate selected on the intended GameCube setup. Gameplay
   button RGB should be black. Bootloader/recovery indicators retain defaults.
2. Check all 34 physical button bindings against FRIEND_PROFILE_NORMALIZED.md
   and friend_profile_normalized.json. In particular, LF3 and RF8 both Left;
   LF5/LT5/RF6 all Up; RF9/RF14/RF15 inert; RT4 C-Up and RT5 C-Right;
   LF6/LF7 D-pad Right/Left; LF8 R; LT6 Y2; RF10 L+R+A; RF12 A+B.
3. Check neutral and eight directions for Default, X1, Y1, Y2, Tilt1, Tilt2,
   Tilt1+Tilt2 (Tilt3), Mode and LT2 Up-smash+A. Where a trusted raw report
   viewer is available, compare exact numbers in the normalized JSON. Tilt2's
   horizontal flip is intentional. Default direction 2 was owner-corrected to
   (0,-77), raw (128,51), straight Down. LT2 forces (128,195)+A even without direction and
   wins over Mode; Mode otherwise centers only the left stick.
4. Check physical C-stick: RT3=(39,128), RT5=(217,128), RT2=(128,1),
   RT4=(128,255); diagonals combine these values, neutral=(128,128).
   Confirm left-stick modifiers do not change C-stick magnitudes/routing.
5. Check LF4 gives L with analog108 and remains L while held. LT3 alone gives
   Y1; LF4+LT3 gives Y1 plus R255. Check priority with held lower modifiers:
   Up-smash > Mode > Tilt3 > Tilt1 > Tilt2 > Y1 > Y2 > X1.
6. Check opposing Left/Right and Down/Up: initially simultaneous inputs cancel;
   second input wins, releasing it restores the held first input. Repeat Left
   using RF8, Up using each duplicate and holding duplicate Up sources together.
7. Power-cycle twice. Confirm no refusal, same profile and working mappings.
   If you later make a legitimate Config edit using an already-supported local
   workflow, power-cycle and confirm the firmware does not restore baked Config.
   Such an edit is optional, not an installation requirement. Do not delete the
   marker or deliberately corrupt storage on the friend's device to test faults.
8. If USB is used, check Ultimate default on XInput, DInput and Switch separately.
   Report untested backends explicitly. Nunchuk remains NOT_TESTED.

Report PASS/FAIL with the exact commit and full UF2 SHA-256. On failure, report
physical key/chord, backend, observed versus expected result and recovery text;
stop use. Host validation/build PASS is not hardware PASS and does not authorize
merging this private fork into canonical configurator.
