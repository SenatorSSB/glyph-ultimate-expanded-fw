# KazTest4 owner test sheet

Gameplay NOT_TESTED. The profile produces deterministic controller outputs;
move recognition, landing/while-rising timing, roll/spot-dodge thresholds and
cancel windows remain empirical owner tests. No game history is inferred.

After verified CREATE, use the established GameCube/Ultimate route. **MB1 →
.Profile → KazTest4**; navigate with **MB2/MB3**, select with **MB4**, allow the
normal save/reboot and verify the name. Keep **KazTest3** as an immediate rollback
menu choice. Ultimate, Kazuya and KazTest2 remain intact. No host reference write.

1. Ordinary RF8+RF7 CD with physical Up/Down preloaded: it stays down-diagonal
   by physical horizontal; no horizontal produces pure Down, never early neutral.
2. Release RF8 while any LF direction remains held: RF7 alone gives neutral.
3. Release RF7 afterward: chosen ordinary movement returns. Simultaneous RF8/RF7
   release can skip neutral; test deliberately without expecting an inserted frame.
4. Add LT2 during CD: neutral with double Shield, all9 physical directions.
5. Release RF8, keep RF7+LT2 and horizontal-only LF: opposite horizontal+Down
   with Shield. Compare actual Right and Left separately; direction5 falls to Down.
6. Prepare physical down-back with LT2: after RF8 release it stays manual
   down-back, without automatic flip. Check physical Up/Up-diagonals remain Default.
7. RF8+RF7 → addRF5 neutral/no A → releaseRF8 Up/no A → releaseRF7 Up+A.
   Repeat four-button route, RF6 additions/removals and reverse/simultaneous releases.
8. RF6-only spring-loaded grab keeps Default directional cancels/no Z until RF7
   release. Recheck EWGF, Hell's Gate, RF5-over-RF6 and RF6 physical7/8/9 strong Up.
9. LT6 now produces Down+A (Down Smash candidate), including command overlaps.
10. RF1 nair → RF8 fastfall/crouch → releaseRF1 → pressRF12 at chosen timing:
    neutral+A. Test RF12+LT6 (neutral wins), null/D-pad and independent buttons.
11. LT2 releases its own Shield for RF3, executable RF5 A, physical Up+RF1/RF2.
    RF7+RF5 keeps Shield. Check full ordinary angling, rolls/spot-dodges and independent
    LT1/RF16. LT2+RF12 intentionally keeps Shield absent another release condition;
    deciding a new RF12 Shield policy remains separate future work.
12. Repeat both physical horizontal sides and both Kazuya facing directions;
    check C-stick transforms, retained modifiers, ordinary buttons/menu/responsiveness.

Report selected profile, exact buttons/directions, release order, timing and
actual result/repeatability. No gameplay acceptance is assumed. Nunchuk NOT_TESTED.
